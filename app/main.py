from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import user_routes
from app.api.routers import quickbooks_routes
from app.api.routers import quickbooks_routes


app = FastAPI()


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


app.include_router(user_routes.router)
app.include_router(quickbooks_routes.router)


# You can also include other routers as your application grows
# uvicorn main:app --reload
