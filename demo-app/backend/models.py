from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from database import Base

class AnalysisLog(Base):
    __tablename__ = "analysis_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String, index=True)
    summary = Column(Text)
    vietnamese_translation = Column(Text)
    raw_text = Column(Text) # OCR text or transcript
    sentiment_score = Column(Float)
    trending_keywords = Column(JSON)
    video_timestamp = Column(String) # Timestamp in the video
