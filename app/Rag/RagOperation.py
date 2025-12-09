from app.FirebaseOperations import query_firestore_generic_extended
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from config import settings
from langchain_core.prompts import PromptTemplate
import aiohttp
import ssl
from app.Rag.OutputModal import pyOutPutParser2
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from typing import List
from app.Rag.Ragutility import load_messages_jsonl, clear_chat_history

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))
llm_endpoint = HuggingFaceEndpoint(
        repo_id="aisingapore/Gemma-SEA-LION-v4-27B-IT",
        task="text-generation",
        temperature=0,
        huggingfacehub_api_token=settings.HUGGING_FACE_TOKEN,
        streaming=True,
        client=session,
        max_new_tokens=250,
    )   


def generateFirebaseFilter(query: str):
    llm_endpoint = HuggingFaceEndpoint(
    repo_id="ServiceNow-AI/Apriel-1.6-15b-Thinker",  # Updated to top-performing model for structured output
    task="text-generation",
    temperature=0.3,     # Lower temperature for more deterministic/JSON-compliant output
    top_p=0.95,          # Optional: keep output focused
    huggingfacehub_api_token=settings.HUGGING_FACE_TOKEN,
    client=session,
    return_full_text=True
    )
    prompt = PromptTemplate(
        template="""
You convert natural language into a structured Firestore query filter.

User query:
{query}

Your job:
1. Interpret the user query.
2. Convert it into a structured Firestore filter object.
5. If no month is detected → set isAllData = True
6. Output only the structure required by the parser.

formate instruction to follow
{format_ins}
""",
        input_variables=["query"],
        partial_variables={"format_ins": pyOutPutParser2.get_format_instructions()}
    )

    chat_model = ChatHuggingFace(llm=llm_endpoint)

    chain = prompt | chat_model | pyOutPutParser2

    result = chain.invoke({"query": query})
    return result.dict()

async def rag_query_stream(query: str, user: str, sessionId: str|None):  
    filters = generateFirebaseFilter(query)
    print(filters)
    chat_model = ChatHuggingFace(llm=llm_endpoint)
    params = {}
    history:List[BaseMessage] = []
    if(sessionId):
        history = load_messages_jsonl(user)
    else:
        clear_chat_history(user)    

    finalPrompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name='chat_history'),
    ])

    if (filters['isQueryToAppFinanceRelated']):
        context = query_firestore_generic_extended(user, filters)
        params = {
            'context': context,
            "question": query,
            'chat_history': history
        }
        finalPrompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "You are a knowledgeable finance assistant helping users analyze their expenses "
                "and manage finances effectively.\n\n"
                "You are given a list of user expenses in JSON format. Use the data to provide "
                "detailed and actionable insights. Format your response using markdown.\n\n"
                "If the context is empty or insufficient, return only an informational message.\n"
                "Do NOT infer or fabricate details.\n\n"
                "Instructions:\n"
                "- Highlight unusual or significant expenses\n"
                "- Suggest ways to optimize spending or save money\n"
                "- Keep the response professional and clear\n"
                "- All amounts are in Indian Rupees (₹)\n"
                "- Only provide meaningful responses\n"
                "- Provide text only; no images or code\n"
                "- Keep the response within 150 tokens"
            )
        ),
        
        MessagesPlaceholder(variable_name="chat_history"),

        HumanMessagePromptTemplate.from_template(
            "Expenses data: {context}\n\nUser question: {question}"
        )
    ])

    else:
        finalPrompt.append(('human','{question}'))
        params = {
            "question": query,
            'chat_history': history

        }

    chain = finalPrompt | chat_model | StrOutputParser()
    return chain.astream(params)
