# MyMoney Tracking RAG

An AI-powered personal finance assistant that uses Retrieval-Augmented Generation (RAG) to provide intelligent insights about your transactions through conversational chat.

## 🎥 Demo

Watch the demo: [YouTube Shorts](https://www.youtube.com/shorts/nOOtQEi9duQ)

## 📋 Features

- **User Authentication**: Secure JWT-based authentication with refresh tokens
- **Transaction Management**: Track and retrieve financial transactions
- **AI-Powered Chat**: RAG-based conversational AI that understands your financial data
- **Streaming Responses**: Real-time streaming chat responses using Server-Sent Events (SSE)
- **Session Management**: Persistent chat history stored in JSONL format
- **Firebase Integration**: Secure cloud-based data storage and retrieval

## 🛠️ Technologies

### Backend & Framework
- **FastAPI**: Modern async web framework for building APIs
- **Python 3.x**: Core language

### AI & ML
- **LangChain**: RAG framework and LLM orchestration
- **LangGraph**: Advanced graph-based LLM workflows
- **OpenRouter API**: LLM provider for generative AI

### Database & Storage
- **Firebase/Firestore**: Real-time cloud database
- **JSONL**: Chat history persistence

### Authentication
- **JWT (JSON Web Tokens)**: Secure token-based authentication
- **PyJWT**: JWT implementation

### Async & Streaming
- **aiohttp**: Asynchronous HTTP client
- **SSE Starlette**: Server-Sent Events for streaming responses

### Validation & Configuration
- **Pydantic**: Data validation and settings management
- **email-validator**: Email validation

## 📁 Project Structure

```
mymoneyTracking-Rag/
├── main.py                          # Application entry point
├── router.py                        # API route definitions
├── config.py                        # Configuration settings
├── requirements.txt                 # Python dependencies
├── mymoneytracking.json            # Configuration file
├── app/
│   ├── auth.py                     # JWT authentication logic
│   ├── FirebaseOperations.py       # Firebase database operations
│   ├── Validator.py                # Request validators (Pydantic models)
│   ├── DB/
│   │   └── FireBaseInit.py         # Firebase initialization
│   └── Rag/
│       ├── RagOperation.py         # RAG query and streaming logic
│       ├── Ragutility.py           # RAG utility functions
│       ├── OutputModal.py          # Response formatting
│       └── StreamingCollector.py   # Streaming response handler
├── ChatHistory/                     # Chat conversation history
└── __pycache__/                    # Python cache
```

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mymoneyTracking-Rag
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```
   secret_key=your_jwt_secret_key
   refresh_secret_key=your_refresh_token_secret
   algorithm=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_MINUTES=10080
   json_model=your_json_model
   chat_model=your_chat_model
   base_url=your_base_url
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```

5. **Configure Firebase**
   Set up Firebase credentials in `app/DB/FireBaseInit.py`

## 📡 API Endpoints

### Authentication
- **POST** `/api/v1/user/auth/` - Authenticate user with userId
- **POST** `/api/v1/user/refresh_token/` - Refresh JWT tokens

### User Data
- **GET** `/api/v1/user/info/` - Get authenticated user info
- **GET** `/api/v1/user/transactions/` - Get user transactions

### Chat
- **POST** `/api/v1/user/chat/` - Stream AI responses about transactions

## ⚙️ Configuration

Edit `config.py` to customize:
- `CHUNK_SIZE`: RAG document chunk size (default: 500)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)
- `TOP_K`: Number of retrieved documents (default: 5)
- `TEMPERATURE`: LLM creativity level (default: 0.7)

## 🏃 Running the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📝 Request/Response Examples

### Authenticate User
```bash
curl -X POST "http://localhost:8000/api/v1/user/auth/" \
  -H "Content-Type: application/json" \
  -d '{"userId": "user123"}'
```

### Chat with AI
```bash
curl -X POST "http://localhost:8000/api/v1/user/chat/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How much did I spend on groceries?",
    "userId": "user123",
    "session_id": "session123"
  }'
```

## 🔐 Security

- JWT token-based authentication
- CORS middleware configured
- Environment variable protection for sensitive data
- Firebase security rules for data access

## 📚 Dependencies Highlights

Key packages:
- `fastapi==0.128.0` - Web framework
- `langchain==1.2.6` - RAG framework
- `langgraph==1.0.6` - LLM graph workflows
- `google-cloud-firestore==2.22.0` - Database
- `sse-starlette` - Server-Sent Events
- `pydantic` - Data validation

## 📄 License

[Add your license information here]

## 👤 Author

[Add author information here]

## 🤝 Contributing

[Add contribution guidelines here]

---

For more information or issues, please visit the repository or contact the development team.
