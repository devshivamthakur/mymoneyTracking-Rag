from fastapi import APIRouter, HTTPException, Depends, Request
from app.Validator import authUser, refreshTokenRequest, chatStreamRequest
from app.auth import jwt_bearer, get_current_user, validate_refersh_token
from app.FirebaseOperations import validate_user, get_user_info
from app.FirebaseOperations import get_transactions
from app.Rag.RagOperation import rag_query_stream
from sse_starlette import  EventSourceResponse
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
import json
from app.Rag.Ragutility import save_messages_jsonl
import uuid
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/v1/user", tags=["User"])

@router.post("/auth/")
@limiter.limit("5/minute")
async def auth_user(request: Request, user: authUser):
    if not user.userId:
        raise HTTPException(status_code=400, detail="User ID is required.")
    tokens = validate_user(user.userId)
    
    return {"message": "User authenticated successfully.", "tokens": tokens}

@router.get("/info/")
@limiter.limit("5/minute")
async def getUserInfo(request: Request,user = Depends(get_current_user)):
    userInfo = get_user_info(user)
    return {"data": userInfo, "message": "User info retrieved successfully."}

@router.post("/refresh_token/")
async def refresh_token(request: Request,body: refreshTokenRequest):
    tokens = validate_refersh_token(body.refresh_token)
    return {"message": "Token refreshed successfully.", "tokens": tokens}

@router.get("/transactions/")
@limiter.limit("5/minute")
async def getUserTransactions(request: Request,user = Depends(get_current_user)):
    transactions = get_transactions(user)
    return {"data": transactions, "message": "User transactions retrieved successfully."}

@router.post("/chat/")
@limiter.limit("5/minute")
async def chat_endpoint(request: Request,body:chatStreamRequest, user = Depends(get_current_user)):
    stream = await rag_query_stream(body.query, body.userId, body.session_id)
    human_msg = HumanMessage(content=body.query)
    ai_buffer = ""
    
    async def event_gen():
        nonlocal ai_buffer
        response = json.dumps({"type": "metaInfo", "sessionId": str(uuid.uuid1())})
        yield f"{response}"
        async for chunk in stream:
            ai_buffer += chunk
            content = chunk
            if chunk == " ":
                content = chunk.replace(" ", "&nbsp;")
            response = json.dumps({"type": "content", "content": content})
            yield f"{response}"

        ai_msg = AIMessage(content= ai_buffer)    
        save_messages_jsonl(human_msg, ai_msg, body.userId)
        yield "\n\n"
    return EventSourceResponse(event_gen(), media_type="text/event-stream")




