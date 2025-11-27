import cv2
import yt_dlp
import time
import os
from openai import OpenAI
from PIL import Image
import json
import asyncio
from datetime import datetime
from database import SessionLocal
from models import AnalysisLog
import base64
from io import BytesIO

# Configure Groq
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

class StreamProcessor:
    def __init__(self, youtube_url, source_name="Euronews"):
        self.youtube_url = youtube_url
        self.source_name = source_name
        self.cap = None
        self.running = False

    def get_stream_url(self):
        """Lấy URL stream từ YouTube bằng yt-dlp"""
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'quiet': True,
            'no_warnings': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.youtube_url, download=False)
                return info['url']
        except Exception as e:
            print(f"Error getting stream URL: {e}")
            return None

    async def process_stream(self, callback):
        """Xử lý stream liên tục với Groq"""
        self.running = True
        print(f"Starting stream processing for {self.source_name}...")
        
        frame_count = 0
        reconnect_attempts = 0
        max_reconnect = 3
        
        while self.running and reconnect_attempts < max_reconnect:
            try:
                # Get stream URL
                stream_url = self.get_stream_url()
                if not stream_url:
                    print("Failed to get stream URL. Retrying in 10s...")
                    await asyncio.sleep(10)
                    reconnect_attempts += 1
                    continue
                
                # Open video stream
                self.cap = cv2.VideoCapture(stream_url)
                if not self.cap.isOpened():
                    print("Failed to open video stream. Retrying...")
                    await asyncio.sleep(10)
                    reconnect_attempts += 1
                    continue
                
                print(f"✓ Connected to {self.source_name} stream")
                reconnect_attempts = 0  # Reset on success
                
                # Process frames
                while self.running:
                    ret, frame = self.cap.read()
                    
                    if not ret:
                        print("Stream ended or error. Reconnecting...")
                        break
                    
                    frame_count += 1
                    
                    # Process every 15 seconds (assuming ~30fps = 450 frames)
                    if frame_count % 450 == 0:
                        try:
                            # Convert frame to PIL Image
                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            pil_image = Image.fromarray(rgb_frame)
                            
                            # Analyze with Groq
                            analysis = await self.analyze_frame_comprehensive(pil_image)
                            
                            if analysis:
                                # Save to database
                                self.save_to_db(analysis)
                                # Send to WebSocket
                                await callback(analysis)
                                
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Processed frame {frame_count}")
                            
                        except Exception as e:
                            print(f"Error analyzing frame: {e}")
                    
                    # Small delay to prevent CPU overload
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                print(f"Stream error: {e}. Reconnecting in 10s...")
                await asyncio.sleep(10)
                reconnect_attempts += 1
            finally:
                if self.cap:
                    self.cap.release()

    def image_to_base64(self, image):
        """Convert PIL Image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    async def analyze_frame_comprehensive(self, image):
        """Phân tích toàn diện frame bằng Groq Vision (OCR, Dịch, Phân tích)"""
        
        # Convert image to base64
        image_base64 = self.image_to_base64(image)
        
        prompt = """
Bạn là hệ thống AI phân tích tin tức thời gian thực. Hãy phân tích khung hình từ kênh tin tức này và trả về JSON với cấu trúc sau:

{
  "headline_ocr": "Tiêu đề chính trích xuất từ màn hình (nếu có, bằng tiếng Anh gốc)",
  "summary": "Tóm tắt ngắn gọn nội dung đang diễn ra (2-3 câu, tiếng Anh)",
  "vietnamese_translation": "Bản dịch tiếng Việt của tóm tắt trên",
  "keywords": ["từ khóa 1", "từ khóa 2", "từ khóa 3"],
  "sentiment_score": 0.0,
  "subtitle_vi": "Phụ đề ngắn gọn bằng tiếng Việt mô tả cảnh đang diễn ra"
}

Trong đó:
- headline_ocr: Đọc chữ từ banner/ticker trên màn hình
- summary: Mô tả những gì đang xảy ra (dựa vào hình ảnh, người, địa điểm, sự kiện)
- vietnamese_translation: Dịch summary sang tiếng Việt
- keywords: 3-5 từ khóa quan trọng
- sentiment_score: Điểm cảm xúc từ -1.0 (tiêu cực) đến 1.0 (tích cực)
- subtitle_vi: Câu phụ đề ngắn gọn bằng tiếng Việt

Chỉ trả về JSON, không có markdown code blocks.
"""
        
        try:
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            text = response.choices[0].message.content.strip()
            
            # Remove markdown if present
            text = text.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(text)
            
            # Add metadata
            data["source"] = self.source_name
            data["timestamp"] = datetime.now().isoformat()
            data["ocr_text"] = data.get("headline_ocr", "")
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Raw response: {text}")
            return None
        except Exception as e:
            print(f"Groq API Error: {e}")
            return None

    def save_to_db(self, data):
        """Lưu kết quả phân tích vào PostgreSQL"""
        db = SessionLocal()
        try:
            log = AnalysisLog(
                source=data["source"],
                summary=data.get("summary", ""),
                vietnamese_translation=data.get("vietnamese_translation", ""),
                raw_text=data.get("ocr_text", ""),
                sentiment_score=data.get("sentiment_score", 0.0),
                trending_keywords=data.get("keywords", []),
                video_timestamp=datetime.now().strftime("%H:%M:%S")
            )
            db.add(log)
            db.commit()
            print(f"✓ Saved to database: {data.get('summary', '')[:50]}...")
        except Exception as e:
            print(f"DB Error: {e}")
            db.rollback()
        finally:
            db.close()

    def stop(self):
        """Dừng stream processor"""
        self.running = False
        if self.cap:
            self.cap.release()
        print(f"Stopped processing {self.source_name}")
