from pydantic import BaseModel, Field, field_validator
from typing import Optional

class chatStreamRequest(BaseModel):
    query: str = Field(..., description="The user's query for the chat stream.")
    session_id: Optional[str] = Field(None, description="Optional session identifier.")

    @field_validator('query')
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query must not be empty')
        return v

class authUser(BaseModel):
    userId: str = Field(..., description="The unique identifier for the user.")

    @field_validator('userId')
    def userId_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('User ID must not be empty')
        return v    
    
class refreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="The refresh token for obtaining a new access token.")

    @field_validator('refresh_token')
    def refresh_token_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Refresh token must not be empty')
        return v    