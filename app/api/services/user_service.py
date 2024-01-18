from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import jwt
from app.api.repository.user_repository import UserRepository
from app.api.repository.auth_repository import AuthRepository

from app.api.models.User import User
import bcrypt
from app.utils.utils import get_env_variable


load_dotenv()

USER_JWT_SECRET_KEY = get_env_variable('USER_JWT_SECRET_KEY')
USER_JWT_ALGORITHM = get_env_variable('USER_JWT_ALGORITHM')
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = get_env_variable(
    'JWT_ACCESS_TOKEN_EXPIRE_MINUTES')


class UserService:
    def __init__(self, user_repo: UserRepository, auth_repo: AuthRepository):
        self.user_repo = user_repo
        self.auth_repo = auth_repo

    async def invalidate_refresh_token(self, token: str):
        return await self.auth_repo.invalidate_token(token)


    async def get_user_by_username(self, username: str):
        user = await self.user_repo.get_user_by_username(username)
        return user

    async def get_user_by_id(self, id: str):
        user = await self.user_repo.get_user_by_id(id)
        return user

    async def register_user(self, username: str, password: str):
        if await self.user_repo.user_exists(username):
            return False
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        # Decode the hashed password to a UTF-8 string
        decoded_hashed_password = hashed_password.decode('utf-8')
        user = User(username=username, hashed_password=decoded_hashed_password)
        return await self.user_repo.add_user(user)

    def generate_jwt_token(self, user_id: int):
        return jwt.encode({"user_id": user_id}, USER_JWT_SECRET_KEY, algorithm=USER_JWT_ALGORITHM)


    async def login_user(self, username: str, password: str) -> Optional[User]:
        user = await self.user_repo.get_user_by_username(username)
        # print(f"User: {user}")
        if user is None:
            return None
        # Verify the password using bcrypt
        if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            return None
        return user

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.user_repo.get_user_by_id(user_id)
        return user


    def create_a_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Short lifespan for access token
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, USER_JWT_SECRET_KEY, algorithm=USER_JWT_ALGORITHM)
        return encoded_jwt
    
    
