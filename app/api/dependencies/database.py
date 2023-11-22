from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config.quickbooks_config import get_env_variable

load_dotenv()


# Database URL, typically taken from environment variables for security
DATABASE_URL = get_env_variable("DATABASE_URL","postgresql://test:sOGpuootyvg79ekZdbkJOA@smiley-tapir-13443.5xj.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full")

# Create the SQLAlchemy engine
# The `echo` flag is optional, it enables verbose logging of SQL queries
engine = create_engine(DATABASE_URL, echo=True)

# SessionLocal class - this is a factory for creating new Session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class - use this as a parent class for your ORM models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
