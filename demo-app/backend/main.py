import asyncio
import json
import os
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from stream_processor import StreamProcessor
from chat_handler import answer_question

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Media Monitor Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Stream Processor
YOUTUBE_URL = "https://www.youtube.com/watch?v=pykpO5kQJ98"
processor = StreamProcessor(YOUTUBE_URL)

# Chat request model
class ChatRequest(BaseModel):
    question: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

async def process_callback(data):
    """Transform Gemini analysis data for frontend WebSocket"""
    
    news_item = {
        "id": str(int(datetime.now().timestamp())),
        "source": data["source"],
        "title": data.get("headline_ocr", "Breaking News"),
        "ocr_text": data.get("headline_ocr", ""),
        "english_summary": data.get("summary", ""),
        "vietnamese_translation": data.get("vietnamese_translation", ""),
        "timestamp": data["timestamp"],
        "sentiment": "Positive" if data.get("sentiment_score", 0) > 0 else "Negative"
    }
    
    analytics = {
        "sentiment_score": data.get("sentiment_score", 0),
        "trending_keywords": data.get("keywords", []),
        "active_sources": 1,
        "total_mentions": 1240
    }
    
    subtitle = {
        "text": data.get("subtitle_vi", "Đang phân tích..."),
        "lang": "vi",
        "timestamp": data["timestamp"]
    }

    await manager.broadcast({"type": "news", "data": news_item})
    await manager.broadcast({"type": "analytics", "data": analytics})
    await manager.broadcast({"type": "subtitle", "data": subtitle})
    
    print(f"[WebSocket] Broadcasted: {subtitle['text'][:50]}...")

# Global task to hold stream processor
stream_task = None

@app.on_event("startup")
async def startup_event():
    global stream_task
    print("🚀 Starting Media Monitor Backend...")
    print("📡 Initializing stream processor...")
    stream_task = asyncio.create_task(processor.process_stream(process_callback))

@app.on_event("shutdown")
async def shutdown_event():
    global stream_task
    print("🛑 Shutting down stream processor...")
    processor.stop()
    if stream_task:
        stream_task.cancel()

@app.get("/")
async def root():
    return {"message": "Media Monitor Backend is running"}

@app.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Endpoint để chat với Gemini về dữ liệu đã thu thập"""
    result = await answer_question(request.question, db)
    return result

@app.websocket("/ws/monitor")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
