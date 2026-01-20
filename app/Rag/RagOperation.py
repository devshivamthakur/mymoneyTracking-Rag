from app.FirebaseOperations import query_firestore_generic_extended
from config import settings
from langchain_core.prompts import PromptTemplate
from app.Rag.OutputModal import pyOutPutParser2
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from typing import List
from app.Rag.Ragutility import load_messages_jsonl, clear_chat_history, DEFAULT_FIREBASE_FILTER
from langchain_openai import ChatOpenAI

def generateFirebaseFilter(query: str):
    try:
        jsonLLm = ChatOpenAI(
            model=settings.json_model,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.base_url,
            temperature=0.3,     
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

        chain = prompt | jsonLLm | pyOutPutParser2
        result = chain.invoke({"query": query})

        filter = result.dict()

        if 'isQueryToAppFinanceRelated' in filter:
            return filter
        return DEFAULT_FIREBASE_FILTER 
    
    except Exception as e:
        return DEFAULT_FIREBASE_FILTER

async def rag_query_stream(query: str, user: str, sessionId: str|None):  
    filters = generateFirebaseFilter(query)
    chat_model = ChatOpenAI(
            model=settings.json_model,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.base_url,
            temperature=0.3,   
            streaming=True
        )
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
