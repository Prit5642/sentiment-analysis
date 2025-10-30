import os

class Config:
    # Database
    DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///sentiment_predictions.db')
    
    # Model paths
    MODEL_PATH = "C:/Prit/MLOps/assignment/ml_model/model.pth"
    VOCAB_PATH = "C:/Prit/MLOps/assignment/ml_model/vocab.pkl"
    
    # Monitoring
    PROMETHEUS_PORT = 9090
    GRAFANA_PORT = 3000
    WEBAPP_PORT = 5000
    DBAPP_PORT = 5001
    
    # Application
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', False)