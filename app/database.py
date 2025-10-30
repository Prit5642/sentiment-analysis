from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from config.settings import Config

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URI)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def init_db(self):
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()
    
    def close_session(self, session):
        session.close()

# Global database manager
db_manager = DatabaseManager()