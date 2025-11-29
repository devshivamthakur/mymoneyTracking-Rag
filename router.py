from fastapi import APIRouter, HTTPException, Depends
from app.Validator import authUser, refreshTokenRequest
from app.auth import jwt_bearer, get_current_user, validate_refersh_token
from app.FirebaseOperations import validate_user, get_user_info
router = APIRouter(prefix="/api/v1/user", tags=["User"])

@router.post("/auth/")
async def auth_user(user: authUser):
    if not user.userId:
        raise HTTPException(status_code=400, detail="User ID is required.")
    tokens = validate_user(user.userId)
    
    return {"message": "User authenticated successfully.", "tokens": tokens}

@router.get("/info/")
async def getUserInfo(user = Depends(get_current_user)):
    print("Decoded JWT claims:", user)
    userInfo = get_user_info(user)
    return {"data": userInfo, "message": "User info retrieved successfully."}

@router.post("/refresh_token/")
async def refresh_token(body: refreshTokenRequest):
    tokens = validate_refersh_token(body.refresh_token)
    return {"message": "Token refreshed successfully.", "tokens": tokens}
