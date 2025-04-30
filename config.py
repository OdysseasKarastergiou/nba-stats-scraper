import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key')
    DEBUG = True
    
    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///nba_stats.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
