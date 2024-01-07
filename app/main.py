from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import plaid_routes, user_routes, quickbooks_routes
from app.api.dependencies.database import async_database_session
from app.utils.utils import get_env_variable

# origins = ["http://localhost:3000", "https://c893af99.iseem-front-cf.pages.dev/", "http://localhost:3000"]

# Define your async context manager for lifespan events
load_dotenv()

CORS_ORIGIN = get_env_variable('CORS_ORIGIN')

@asynccontextmanager
async def lifespan(app: FastAPI):

    await async_database_session.init()
    await async_database_session.create_all()

    yield  # This yield separates startup and shutdown actions

    # Perform shutdown actions
    await async_database_session.close()  # Close database connection


# Create your FastAPI app using the lifespan context manager
app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://main.iseem-front-cf.pages.dev/api/quickbooks"],  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    
)

# Include routers
app.include_router(user_routes.router)
app.include_router(quickbooks_routes.router)
app.include_router(plaid_routes.router)


# Additional routers can be included here as your application grows
