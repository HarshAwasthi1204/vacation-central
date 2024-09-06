from fastapi import APIRouter, Depends, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from typing import Annotated
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from models.models import Token, TokenData, User, SecureUser
from dbstuff.dbcrud import read_user_login
from security.hashers import verify_password
from security.jwtconfig import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

# fake_users_db = {
#     "johndoe": {
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
#     },
#     "johndoe@gmail.com": {
#         "username": "johndoe1",
#         "full_name": "John Doe1",
#         "email": "johndoe1@example.com",
#         "hashed_password": "$2a$04$31yor9JRi5hqyqaSqSkshuX7FTLVEqY86XGluheYPkR1FGa.ixxFG",
#     }
# }

auth_router = APIRouter()


oauth2_pwdbearer_flow = OAuth2PasswordBearer(tokenUrl="token")

# def get_user(db: dict, username: str | None):
#     if username in db:
#         user_dict = db[username]
#         return SecureUser(**user_dict)
#         # return User2InDB(**user_dict)

# def authenticate_user(fakedb: dict, username: str, password: str):
async def authenticate_user(username: str, password: str):
    # user = get_user(fakedb, username)
    user = await read_user_login(username)
    if not user or isinstance(user, JSONResponse):
        return None
    elif not verify_password(password, user.hashed_password):
        return False
    return user
    
# def create_access_token(payload: dict, expiration_time : timedelta | None = None) -> str:
def create_access_token(payload: dict, expiration_time : timedelta) -> str:
    data_to_encode = payload.copy()
    if expiration_time:
        expire_at = datetime.now(timezone.utc) + expiration_time
    # else:
    #     # expire_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #     expire_at = datetime.now(timezone.utc) + timedelta(seconds=20)
    data_to_encode.update({"exp" : expire_at.timestamp()})
    encoded_jwt = jwt.encode(claims=data_to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# def create_refresh_token(payload: dict, expiration_time : timedelta | None = None) -> str:
def create_refresh_token(payload: dict, expiration_time : timedelta) -> str:
    data_to_encode = payload.copy()
    data_to_encode["refresh"] = True  # Flag to identify refresh token
    if expiration_time:
        expire_at = datetime.now(timezone.utc) + expiration_time
    # else:
    #     expire_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    data_to_encode.update({"exp": expire_at.timestamp()})
    encoded_refresh_jwt = jwt.encode(claims=data_to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_jwt

def decode_token(jwttoken: str, verify: bool = True):
    # try:
        if verify:
            payload = jwt.decode(token=jwttoken, key=SECRET_KEY, algorithms=[ALGORITHM])
        else:
            payload = jwt.decode(token=jwttoken, key=SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        return payload
    # except ExpiredSignatureError:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid Token",
    #         headers={"WWW-Authenticate" : "Bearer"},
    #     )
    # except JWTError:
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Invalid Token",
        #     headers={"WWW-Authenticate" : "Bearer"},
        # )

# def get_current_user(token: Annotated[str, Depends(oauth2_pwdbearer_flow)]) -> User:
async def get_current_user(token: Annotated[str, Depends(oauth2_pwdbearer_flow)]) -> SecureUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        jwt_payload = decode_token(jwttoken = token)
        username : str | None = jwt_payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    if token_data.username:
        current_user = await read_user_login(token_data.username)
    if current_user is None or isinstance(current_user, JSONResponse):
        raise credentials_exception
    return current_user

@auth_router.post("/token", response_model=Token)
async def get_token_by_authentication(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], rememberme: Annotated[str | None, Form()] = None) -> Token:
    # user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Username or Password",
            headers={"WWW-Authenticate" : "Bearer"},
        )
    access_token_expiration_time = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(payload={"sub" : user.username}, expiration_time = access_token_expiration_time)
    if rememberme == "on":
        print("Remember me is checked.")
        refresh_token_expiration_time = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_refresh_token(payload={"sub" : user.username}, expiration_time = refresh_token_expiration_time)
    else:
        refresh_token = None
    return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)

@auth_router.post("/refreshtoken", response_model=Token)
async def get_refresh_token_by_authentication(token: str = Depends(oauth2_pwdbearer_flow)) -> Token:
    try:
        jwt_refresh_payload = decode_token(jwttoken = token)
        if not jwt_refresh_payload.get("refresh", False):  # Check if it's a refresh token
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Refresh Token",
                headers={"WWW-Authenticate" : "Bearer"},
            )
        username : str | None = jwt_refresh_payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Refresh Token",
                headers={"WWW-Authenticate" : "Bearer"},
            )
        access_token_expiration_time = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(payload={"sub" : username}, expiration_time = access_token_expiration_time)
        return Token(access_token=access_token, token_type="bearer", refresh_token=token)
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Refresh Token",
            headers={"WWW-Authenticate" : "Bearer"},
        )


@auth_router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user