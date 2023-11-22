from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()

port = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)