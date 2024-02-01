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


async def get_current_user_id(request: Request, user_service: UserService = Depends(get_user_service)):
    token = request.cookies.get("my_token")
    print(token, "token")
    
    print("get_current_user", request.cookies)

    
    if not token:
        raise HTTPException(
            status_code=403, detail="No authentication token found")
    try:
        payload = jwt.decode(token, USER_JWT_SECRET_KEY,
                             algorithms=[USER_JWT_ALGORITHM])
        
        print(payload, "payload")
        user_id = payload.get("user_id")

        if user_id is None:
            print("2")
            raise HTTPException(
                status_code=403, detail="User ID not found in token")

        user = await user_service.get_user_by_id(user_id)
        print(user, "user12")
        if user:
            return user.id
        else:
            print("3")
            raise HTTPException(status_code=403, detail="User not found")

    except jwt.ExpiredSignatureError:
        print("4")
        # Here, you inform the frontend that the token has expired.
        raise HTTPException(status_code=403, detail="Token has expired")

    except jwt.PyJWTError as e:
        print("5")
        raise HTTPException(
            status_code=403, detail="Could not validate credentials")


async def get_current_user(request: Request, user_service: UserService = Depends(get_user_service)):
    token = request.cookies.get("myRefresh_token")
    print(token, "token")
    
        
    print("get_current_user", request.cookies)


    if not token:
        print("1")
        raise HTTPException(
            status_code=403, detail="No authentication token found")
    try:
        payload = jwt.decode(token, USER_JWT_SECRET_KEY,
                             algorithms=[USER_JWT_ALGORITHM])
        
        print(payload, "payload")
        
        user_id = payload.get("user_id")

        if user_id is None:
            print("2")
            raise HTTPException(
                status_code=403, detail="User ID not found in token")

        user = await user_service.get_user_by_id(user_id)
        if user:
            return user
        else:
            print("3")
            raise HTTPException(status_code=403, detail="User not found")

    except jwt.ExpiredSignatureError:
        print("4")
        # Here, you inform the frontend that the token has expired.
        raise HTTPException(status_code=403, detail="Token has expired")

    except jwt.PyJWTError as e:
        print("5")
        raise HTTPException(
            status_code=403, detail="Could not validate credentials")
