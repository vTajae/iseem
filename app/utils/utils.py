from datetime import datetime
from json import JSONEncoder
from app.api.dependencies.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            # Format datetime object as a string
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, obj)