# database.py
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.quickbooks_config import get_env_variable
import ssl

load_dotenv()


CAT_FILE = get_env_variable("CAT_FILE")
DATABASE_URL = get_env_variable("DATABASE_URL")
# Create an SSL context
ssl_context = ssl.create_default_context(cafile=CAT_FILE)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_REQUIRED

# Define the Base class using SQLModel
Base = declarative_base()


class AsyncDatabaseSession:
    def __init__(self, db_url):
        self.db_url = db_url
        self.engine = None
        self.session_factory = None

    async def init(self):
        self.engine = create_async_engine(
            self.db_url,
            future=True,
            echo=False,
            pool_size=10,
            max_overflow=20,
            connect_args={"ssl": ssl_context}
        )
        self.session_factory = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession)

    async def create_all(self):
        async with self.engine.begin() as conn:
            async with self.engine.begin() as conn:
                # Drop all tables
                # await conn.run_sync(Base.metadata.drop_all)
                # Create all tables
                await conn.run_sync(Base.metadata.create_all)

    async def get_session(self):
        async with self.session_factory() as session:
            yield session

    async def close(self):
        await self.engine.dispose()


async_database_session = AsyncDatabaseSession(DATABASE_URL)
