from fastapi import APIRouter, HTTPException, Depends
from app.Validator import authUser, refreshTokenRequest, chatStreamRequest
from app.auth import jwt_bearer, get_current_user, validate_refersh_token
from app.FirebaseOperations import validate_user, get_user_info
from app.FirebaseOperations import get_transactions
from app.Rag.RagOperation import rag_query_stream
from sse_starlette import  EventSourceResponse
import json

router = APIRouter(prefix="/api/v1/user", tags=["User"])

@router.post("/auth/")
async def auth_user(user: authUser):
    if not user.userId:
        raise HTTPException(status_code=400, detail="User ID is required.")
    tokens = validate_user(user.userId)
    
    return {"message": "User authenticated successfully.", "tokens": tokens}

@router.get("/info/")
async def getUserInfo(user = Depends(get_current_user)):
    userInfo = get_user_info(user)
    return {"data": userInfo, "message": "User info retrieved successfully."}

@router.post("/refresh_token/")
async def refresh_token(body: refreshTokenRequest):
    tokens = validate_refersh_token(body.refresh_token)
    return {"message": "Token refreshed successfully.", "tokens": tokens}

@router.get("/transactions/")
async def getUserTransactions(user = Depends(get_current_user)):
    transactions = get_transactions(user)
    return {"data": transactions, "message": "User transactions retrieved successfully."}

@router.get("/chat/")
async def chat_endpoint(
     userId: str = '',
     query: str = '',
     session_id: str = '', 
     user = Depends(get_current_user)
):
    stream = await rag_query_stream(query, userId)

    async def event_gen():
        async for chunk in stream:
            yield f"{chunk.content}\n\n"

        yield "event: END\ndata: \n\n"

    return EventSourceResponse(event_gen(), media_type="text/event-stream")

