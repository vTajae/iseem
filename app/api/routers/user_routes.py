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
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    my_token_expires = timedelta(seconds=60 * 60)
    refresh_token_expires = timedelta(seconds=7 * 24 * 60 * 60)

    my_token = service.create_a_token(
        data={"user_id": user.id}, expires_delta=my_token_expires)
    refresh_token = service.create_a_token(
        data={"user_id": user.id}, expires_delta=refresh_token_expires)

    tokens = {"access_token": my_token, "refresh_token": refresh_token}

    # Set the tokens in HTTP-only cookies
    response.set_cookie(
        key="my_token", value=my_token, httponly=True, max_age=60 * 60)
    response.set_cookie(
        key="myRefresh_token", value=refresh_token, httponly=True, max_age=7 * 24 * 60 * 60)

    # print(f"User: {user}")

    response = {"user": user, "tokens": tokens}

    return response


@router.get("/user/profile", response_model=UserModel)
async def user_profile(
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    if not user.username:
        raise HTTPException(
            status_code=401, detail="Session invalid or expired, please login.")

    response = await user_service.get_user_by_id(user.id)

    return response


@router.post("/refresh")
async def refresh_token(request: Request, response: Response, service: UserService = Depends(get_user_service)):
    refresh_token = request.cookies.get("myRefresh_token")
    if not refresh_token:
        raise HTTPException(status_code=403, detail="Refresh token not found")

    try:
        payload = jwt.decode(refresh_token, USER_JWT_SECRET_KEY, algorithms=[USER_JWT_ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=403, detail="Invalid refresh token")

        my_token_expires = timedelta(minutes=15)

        new_access_token = service.create_a_token(
            data={"user_id": user_id}, expires_delta=my_token_expires)

        # Set the new access token in an HTTP-only cookie with max_age
        response.set_cookie(
            key="my_token", value=new_access_token, httponly=True, max_age=15 * 60)

        return {"message": "Access token refreshed"}
    except jwt.ExpiredSignatureError:
        # Here, you inform the frontend that the token has expired.
        raise HTTPException(status_code=403, detail="Refresh token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid refresh token")

# @router.get("/users/{id}", response_model=UserModel)
# async def get_user(id: str, service: UserService = Depends(get_user_service)):
#     user = await service.get_user_by_username(id)
#     if user:
#         return UserModel.from_orm(user)
#     raise HTTPException(status_code=404, detail="User not found")


@router.get("/dashboard")
async def dashboard():
    # Your dashboard logic here
    return {"message": "Welcome to the dashboard"}
