from unittest import result
from app.Rag.Prompt import SYSTEM_PROMPT
from app.Rag.Tools import firestore_query_tool, get_current_date_tool
from config import settings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from app.Rag.Ragutility import load_messages_jsonl, clear_chat_history, DEFAULT_FIREBASE_FILTER
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from typing import List
from langchain_core.messages import BaseMessage

llm = ChatOpenAI(
    model=settings.json_model,
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.base_url,
    temperature=0.3,
    streaming=True
)

agent = create_agent(
    model=llm,
    tools=[firestore_query_tool, get_current_date_tool],
    system_prompt=SYSTEM_PROMPT
)

def get_chat_history(user: str, sessionId: str | None) -> List[BaseMessage]:
    """
    Loads chat history only if sessionId exists.
    Clears history for a new session.
    """
    if sessionId:
        return load_messages_jsonl(user)

    clear_chat_history(user)
    return []


async def rag_stream_single_invoke(
    query: str,
    user: str,
    sessionId: str | None
):
    history = get_chat_history(user, sessionId)

    history.append(HumanMessage(content=f"{query}, userId: {user}"))

    return agent.astream({
        "messages": history,
        "user_preferences": {
            "style": "informal", 
            "verbosity": "concise"
            },
    },stream_mode="messages")
