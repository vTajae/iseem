from datetime import timedelta
from app.utils.utils import get_env_variable
from dotenv import load_dotenv

import jwt
from app.api.models.User import User
from app.api.schemas.quickbooks.quickbooks_TransactionList import TokenResponse
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response
from fastapi.params import Cookie
from fastapi.responses import RedirectResponse
from app.api.dependencies.auth import get_current_user, get_current_user_id
from app.api.dependencies.user_dependencies import get_user_service
from app.api.schemas.user_schema import UserLoginSchema, UserModel, UserRegisterSchema, UserResponse
from app.api.services.user_service import UserService

router = APIRouter()

load_dotenv()

USER_JWT_SECRET_KEY = get_env_variable('USER_JWT_SECRET_KEY')
USER_JWT_ALGORITHM = get_env_variable('USER_JWT_ALGORITHM')
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = get_env_variable(
    'JWT_ACCESS_TOKEN_EXPIRE_MINUTES')


@router.post("/register")
async def register_user(user_data: UserRegisterSchema, service: UserService = Depends(get_user_service)):
    if await service.register_user(user_data.username, user_data.password):
        return {"message": "User registered successfully"}
    else:
        raise HTTPException(status_code=400, detail="Username already exists")


@router.post("/login", response_model=UserResponse)
async def login_user(response: Response, user_data: UserLoginSchema, service: UserService = Depends(get_user_service)):
    user = await service.login_user(user_data.username, user_data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create and save tokens
    tokens = await service.create_and_save_tokens(user.id)
        
    # Set refresh token in HttpOnly cookie
    response.set_cookie(key="myRefresh_token", value=tokens["refresh_token"], httponly=True, max_age=7 * 24 * 60 * 60)
    
    return({"user": user, "tokens": tokens})
    


@router.get("/user/profile", response_model=UserModel)
async def user_profile(
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    if not user.username:
        raise HTTPException(
            status_code=401, detail="Session invalid or expired, please login.")

    return await user_service.get_user_by_id(user.id)


@router.get("/refresh")
async def refresh_token(request: Request, response: Response, user_service: UserService = Depends(get_user_service),
):
    old_refresh_token = request.cookies.get("myRefresh_token")
    
    if not old_refresh_token:
        raise HTTPException(status_code=403, detail="Refresh token not found")
    
    try:
        payload = jwt.decode(old_refresh_token, USER_JWT_SECRET_KEY, algorithms=[USER_JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=403, detail="Invalid refresh token")
        
        # Invalidate the old refresh token
        await user_service.invalidate_refresh_token(old_refresh_token)
        
    
        # Create and save tokens
        tokens = await user_service.create_and_save_tokens(user_id)
        
        # print(tokens, "tokenzzz")
        
        # Set the new refresh token in a secure HttpOnly cookie
        response.set_cookie(key="myRefresh_token", value=tokens["refresh_token"], httponly=True, max_age=7 * 24 * 60 * 60)
        
        # Return the new access token in the response body
        return {"access_token": tokens["access_token"], "message": "Access token refreshed"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Refresh token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


@router.get("/dashboard")
async def dashboard():
    # Your dashboard logic here
    return {"message": "Welcome to the dashboard"}
