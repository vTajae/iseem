from app.api.dependencies.user_dependencies import get_user_service
from app.api.services.user_service import UserService
from app.utils.utils import get_env_variable
from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from dotenv import load_dotenv

load_dotenv()

USER_JWT_SECRET_KEY = get_env_variable('USER_JWT_SECRET_KEY')
USER_JWT_ALGORITHM = get_env_variable('USER_JWT_ALGORITHM')
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = get_env_variable(
    'JWT_ACCESS_TOKEN_EXPIRE_MINUTES')


async def get_current_user_v2(request: Request, user_service: UserService = Depends(get_user_service), return_user: bool = False):
    token = request.cookies.get("my_token")
    if not token:
        raise HTTPException(
            status_code=401, detail="No authentication token found")
    try:
        payload = jwt.decode(token, USER_JWT_SECRET_KEY,
                             algorithms=[USER_JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=403, detail="User ID not found in token")

        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=403, detail="User not found")

        return user if return_user else user.id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=403, detail="Could not validate credentials")


# Function to get user ID
async def get_current_user_id(request: Request, user_service: UserService = Depends(get_user_service)):
    return await get_current_user_v2(request, user_service, return_user=False)

# Function to get full user object
async def get_current_user(request: Request, user_service: UserService = Depends(get_user_service)):
    return await get_current_user_v2(request, user_service, return_user=True)
