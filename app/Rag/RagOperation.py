from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.FirebaseOperations import get_transactions
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from config import settings
from app.Validator import chatStreamRequest
from langchain_core.documents import Document    
from datetime import date, datetime, timedelta, time
from langchain_core.prompts import PromptTemplate
import aiohttp
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))

embedding_model_id = "BAAI/bge-small-en"  # You can change to another HF embedding model
emabdding_llm = HuggingFaceEndpointEmbeddings(repo_id=embedding_model_id, huggingfacehub_api_token=settings.HUGGING_FACE_TOKEN)
llm_endpoint = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen3-Next-80B-A3B-Instruct",  # Replace with any HF LLM you want
        task="text-generation",
        max_new_tokens=150,
        temperature=0.5,
        huggingfacehub_api_token=settings.HUGGING_FACE_TOKEN,
        streaming=True,
        client=session
    )   
def preprocess_dataset(docs_list):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=50,
    )
    doc_splits = text_splitter.split_documents(docs_list)
    return doc_splits

def storeInVectorDB(doc_splits, userId):
    print("docs started here")
    return QdrantVectorStore.from_documents(
        doc_splits,
        emabdding_llm,
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        collection_name=f"{settings.QDRANT_COLLECTION_NAME}_{userId}",
        prefer_grpc=True,
        force_recreate = True,

    )

def fetchRetriever(userId):
    retriever = QdrantVectorStore.from_existing_collection(
        api_key=settings.QDRANT_API_KEY,
        collection_name=f"{settings.QDRANT_COLLECTION_NAME}_{userId}",
        embedding=emabdding_llm,
        url=settings.QDRANT_URL,

    )
    return retriever

async def generateEmbedding(query):
    embedding = await emabdding_llm.aembed_query(query)
    return embedding

def process_documents(userId):
    docs_list = get_transactions(userId)
    #convert dict into array of object
    docs = [
        Document(
            page_content=(
                f"amoun {doc['amount']} spent on {datetime.fromtimestamp(doc['date'] / 1000)} "
                f"for {doc.get('discrption', '')} in ({doc['category']}) category"
            ),
            metadata={
                'userId': userId,
                'amount': doc['amount'],
                'timestamp': datetime.fromtimestamp(doc['date'] / 1000).isoformat(),
                'category': doc['category']
            }
        )
        for doc in docs_list
    ]
    doc_splits = preprocess_dataset(docs)
    return storeInVectorDB(doc_splits, userId)

async def search_expense_vectors(user_id: str, query, top_k: int = 5):
    retriever = fetchRetriever(user_id)
    query_embadding = await generateEmbedding(query)
    docs= retriever.search(
        query=query,
        search_type="mmr"
        
    )
    # mmr_retriever = retriever.as_retriever(
    #     search_type="mmr",
    #     search_kwargs={"k": top_k}
    # )

    # # MMR search returns documents
    # docs = mmr_retriever
    # docs = retriever.similarity_search(query)
    return docs

def build_expense_context(retrieved_docs: list[Document]):
    return "\n\n".join(doc.page_content for doc in retrieved_docs)

async def rag_query_stream(query:chatStreamRequest, user: str):
# LLM setup using Hugging Face Endpoint
    # if(not query.session_id):
    #     # fetch data from firebase based on user and store in the 
    #     process_documents(user)

    chat_model = ChatHuggingFace(llm=llm_endpoint)
    prompt = PromptTemplate(
        template="""
    You are a finance assistant. Use expenses.
    If the context is insufficient, just say you don't know.

    expenses: {context}
    Question: {question}
    """,
        input_variables=["context", "question"]
    )

    #2 vectore search
    docs = await search_expense_vectors(user, query.query)
    context = build_expense_context(docs)
    print(context)
    chain = prompt | chat_model
    
    
    return chain.astream({
        'context': context,
        "question": query.query
    },      
    
    )     
