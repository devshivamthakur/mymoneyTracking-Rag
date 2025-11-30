#utils/auth.py or crud.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from datetime import date, datetime, timedelta, time
from typing import Union, Any, Optional
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from config import Settings, settings
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

def create_access_token(subject: Union[str, Any]) -> str:
    # Use provided delta or fallback to settings
    expire_minutes = float(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)

    to_encode = {
        "sub": str(subject),
        "exp": expire
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


def create_refresh_token(subject: Union[str, Any]) -> str:

    expires_delta = datetime.now(timezone.utc) + timedelta(minutes=float(settings.REFRESH_TOKEN_EXPIRE_MINUTES))

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.refresh_secret_key, settings.algorithm)
    return encoded_jwt

def decodeJWT(jwtoken: str):
    try:
        payload = jwt.decode(jwtoken,settings.secret_key, settings.algorithm)
        return payload
    except:
        return None

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
       tokens = await super(JWTBearer, self).__call__(request)
       if tokens:
            credentials: HTTPAuthorizationCredentials = tokens
            if credentials:
                if not credentials.scheme == "Bearer":
                    raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
                payload = self.verify_jwt(credentials.credentials) 
                if not payload:
                    raise HTTPException(status_code=403, detail="Invalid token or expired token.")
                return credentials
       else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
       
    def verify_jwt(self, token: str):
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            return payload  # return decoded claims
        except:
            return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(JWTBearer())):
    token = credentials.credentials
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )
    return payload.get("sub")

def validate_refersh_token(token: str):
    try:
       #decode the token and return new tokens
         payload = jwt.decode(
              token,
              settings.refresh_secret_key,
              algorithms=[settings.algorithm]
         )
         accessToken = create_access_token(payload.get("sub"))
         refreshToken = create_refresh_token(payload.get("sub"))
         return {"access_token": accessToken, "refresh_token": refreshToken}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid refresh token",
        )
    
jwt_bearer = JWTBearer()