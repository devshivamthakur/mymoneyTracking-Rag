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
            content = chunk
            if chunk == " ":
                content = chunk.replace(" ", "&nbsp;")
            response = json.dumps({"type": "content", "content": content})
            yield f"{response}"

        yield "\n\n"

    return EventSourceResponse(event_gen(), media_type="text/event-stream")


# 1. Define an async generator function
async def event_generator():
    import asyncio

    # Simulated LLM output — tokenized manually for demo
    tokens = [
        "This", " ", "is", " ", "a", " ", "real-time", " ", 
        "LangChain-style", " ", "response.", "\n\n",
        "Here", " ", "is", " ", "a", " ", "Markdown", " ", "table:", "\n\n",
        "| Name | Age | Role |\n",
        "|------|-----|------|\n",
        "| Alice | 30 | Engineer |\n",
        "| Bob   | 25 | Designer |\n",
        "| Carol | 28 | Manager |\n",
        "\n",
        "End", " ", "of", " ", "demo."
    ]

    for token in tokens:
        # Preserve spaces with &nbsp; for HTML rendering
        content = token
        if token == "":
            content = token.replace(" ", "&nbsp;")

        response = json.dumps({"type": "content", "content": content})
        yield f"{response}"
        await asyncio.sleep(0.05)  # fast, real-time feel



