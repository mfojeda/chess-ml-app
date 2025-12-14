"""
Database connection module
Handles PostgreSQL connections for the chess application
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Database configuration
DB_USER = os.getenv('USER')  # Your Mac username
DB_PASSWORD = ''  # Empty for local Postgres.app
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'chess_app'

# Connection string
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

def get_engine():
    """Create and return database engine"""
    return create_engine(DATABASE_URL, echo=False)

def get_session():
    """Create and return database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def test_connection():
    """Test database connection"""
    try:
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"PostgreSQL version: {version}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
