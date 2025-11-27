import os
from openai import OpenAI
from sqlalchemy.orm import Session
from models import AnalysisLog
from datetime import datetime, timedelta

# Configure Groq
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

async def answer_question(question: str, db: Session):
    """
    Trả lời câu hỏi của user bằng Groq dựa trên dữ liệu real-time đã thu thập
    """
    
    # Lấy dữ liệu phân tích gần nhất (30 phút trước)
    time_threshold = datetime.now() - timedelta(minutes=30)
    recent_logs = db.query(AnalysisLog).filter(
        AnalysisLog.timestamp >= time_threshold
    ).order_by(AnalysisLog.timestamp.desc()).limit(10).all()
    
    # Xây dựng context từ database
    context_parts = []
    if recent_logs:
        context_parts.append("=== DỮ LIỆU TIN TỨC GẦN NHẤT ===\n")
        for log in recent_logs:
            context_parts.append(f"""
Thời gian: {log.timestamp.strftime('%H:%M:%S')}
Nguồn: {log.source}
Tóm tắt (EN): {log.summary}
Dịch (VI): {log.vietnamese_translation}
Từ khóa: {', '.join(log.trending_keywords or [])}
Cảm xúc: {log.sentiment_score}
---
""")
    else:
        context_parts.append("Hiện chưa có dữ liệu phân tích nào.\n")
    
    context = "".join(context_parts)
    
    # Tạo prompt cho Groq
    prompt = f"""
Bạn là trợ lý AI phân tích tin tức thông minh cho hệ thống giám sát truyền thông.

CONTEXT (Dữ liệu real-time đã thu thập):
{context}

CÂU HỎI CỦA NGƯỜI DÙNG:
{question}

HƯỚNG DẪN:
- Trả lời bằng tiếng Việt, ngắn gọn và chính xác
- Dựa vào dữ liệu context ở trên để trả lời
- Nếu không có đủ thông tin, hãy nói rõ
- Nếu người dùng hỏi về "tin tức mới nhất", hãy tóm tắt các sự kiện gần đây
- Nếu hỏi về xu hướng, hãy phân tích từ khóa và cảm xúc
- Trả lời tối đa 3-4 câu

TRẢ LỜI:
"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content.strip()
        return {
            "answer": answer,
            "context_used": len(recent_logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Groq Chat Error: {e}")
        return {
            "answer": "Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi. Vui lòng thử lại.",
            "context_used": 0,
            "timestamp": datetime.now().isoformat()
        }
