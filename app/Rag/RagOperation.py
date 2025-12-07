from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.FirebaseOperations import query_firestore_generic_extended
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from config import settings
from app.Validator import chatStreamRequest
from langchain_core.documents import Document    
from langchain_core.prompts import PromptTemplate
import aiohttp
import ssl
from app.Rag.OutputModal import pyOutPutParser2
from langchain_core.output_parsers import StrOutputParser

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))
llm_endpoint = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.2",  # Replace with any HF LLM you want
        task="text-generation",
        temperature=0,
        huggingfacehub_api_token=settings.HUGGING_FACE_TOKEN,
        streaming=True,
        client=session,
        max_new_tokens=250,
    )   

def generateFirebaseFilter(query: str):
    llm_endpoint = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",  # Updated to top-performing model for structured output
    task="text-generation",
    max_new_tokens=200,  # Increased to allow more room for JSON output
    temperature=0.3,     # Lower temperature for more deterministic/JSON-compliant output
    top_p=0.95,          # Optional: keep output focused
    huggingfacehub_api_token=settings.HUGGING_FACE_TOKEN,
    client=session
    )
    prompt = PromptTemplate(
        template="""
You convert natural language into a structured Firestore query filter.

User query:
{query}

Your job:
1. Interpret the user query.
2. Convert it into a structured Firestore filter object.
3. Use operators such as: eq, in, gte, lte, lt, gt.
4. Only use these allowed Firestore fields:
   - date (integer ms timestamp)
   - category
   - amount
   - month ("MMM")
5. If no month is detected → set isAllData = True
6. Output only the structure required by the parser.

{format_ins}
""",
        input_variables=["query"],
        partial_variables={"format_ins": pyOutPutParser2.get_format_instructions()}
    )

    chat_model = ChatHuggingFace(llm=llm_endpoint)

    chain = prompt | chat_model | pyOutPutParser2

    result = chain.invoke({"query": query})

    return result.dict()

async def rag_query_stream(query: str, user: str):
    filters = generateFirebaseFilter(query)
    chat_model = ChatHuggingFace(llm=llm_endpoint)
    prompt: PromptTemplate | None = None
    params = {}
    if (filters['isQueryToAppFinanceRelated']):
        context = query_firestore_generic_extended(user, filters)
        prompt = PromptTemplate(
            template="""
    You are a knowledgeable finance assistant helping users analyze their expenses and manage finances effectively.

    You are given a list of user expenses in JSON format. Use the data to provide detailed and actionable insights. Format your response using markdown for better readability.

    If the context is empty or not sufficient, return only an informational message. Do not infer or fabricate details.
    **Expenses data:** {context}

    **User question:** {question}

    **Instructions:**
    - Highlight unusual or significant expenses
    - Suggest ways to optimize spending or save money
    - Keep the response professional and easy to understand
    - All amounts are in Indian Rupees (₹)
    - Only provide meaningful and required responses
    - provide only text do not send any image or code some thing
    - Do NOT output code, code blocks,
    -Provide explanations, insights, and suggestions *only in natural language*.

    most important the response must be with in max token of 150

    **Response:**
    """,
            input_variables=["context", "question"]
        )
        
        params = {
            'context': context,
            "question": query
        }
    else:
        prompt = PromptTemplate(
            template="{question}",
            input_variables=['question']
        )
        params = {
            "question": query
        }
    
    
    chain = prompt | chat_model | StrOutputParser()
        
    return chain.astream(params)