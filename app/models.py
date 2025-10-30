from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SentimentPrediction(Base):
    __tablename__ = 'sentiment_predictions'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    prediction = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    request_id = Column(String(100), unique=True, nullable=False)
    processing_time = Column(Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text[:100] + '...' if len(self.text) > 100 else self.text,
            'prediction': self.prediction,
            'confidence': self.confidence,
            'sentiment_score': self.sentiment_score,
            'timestamp': self.timestamp.isoformat(),
            'request_id': self.request_id,
            'processing_time': self.processing_time
        }