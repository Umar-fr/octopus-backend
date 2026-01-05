# Octopus Backend

A FastAPI-based backend service for analyzing GitHub issues and generating AI-powered solutions. This backend provides RESTful APIs and WebSocket support for real-time progress updates.

## 🚀 Features

- **GitHub Integration**: Authenticate and manage GitHub repositories
- **Issue Analysis**: Ingest and classify GitHub issues by difficulty
- **AI-Powered Solutions**: Generate code solutions using Azure OpenAI
- **Feedback System**: Refine solutions based on user feedback
- **Real-time Updates**: WebSocket support for progress tracking
- **User Management**: JWT-based authentication with GitHub OAuth

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (via SQLAlchemy)
- **AI**: Azure OpenAI
- **Authentication**: JWT, GitHub OAuth
- **Real-time**: WebSockets
- **Containerization**: Docker

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL database
- Azure OpenAI account
- GitHub OAuth App credentials

## 🔧 Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd octopus-backend
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
   
   Create a `.env.local` file in the root directory:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/octopus_db
   AZURE_OPENAI_API_KEY=your_azure_openai_key
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   JWT_SECRET=your_jwt_secret_key
   GITHUB_TOKEN_SECRET=your_github_token_secret
   ```

5. **Initialize the database**
   ```bash
   python create_tables.py
   ```

6. **Run the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

## 🐳 Docker

### Build the image
```bash
docker build -t octopus-backend .
```

### Run the container
```bash
docker run -p 8000:8000 --env-file .env.local octopus-backend
```

## ☁️ Azure Container Apps Deployment

This backend is designed to be deployed on Azure Container Apps. Follow these steps:

### Prerequisites
- Azure CLI installed and configured
- Docker Hub or Azure Container Registry account
- Azure Container Apps environment created

### Deployment Steps

1. **Build and push Docker image**
   ```bash
   # Tag your image
   docker tag octopus-backend <your-registry>/octopus-backend:latest
   
   # Push to registry
   docker push <your-registry>/octopus-backend:latest
   ```

2. **Create Container App**
   
   Using Azure CLI:
   ```bash
   az containerapp create \
     --name octopus-backend \
     --resource-group <your-resource-group> \
     --environment <your-container-apps-environment> \
     --image <your-registry>/octopus-backend:latest \
     --target-port 8000 \
     --ingress external \
     --env-vars \
       DATABASE_URL=<your-database-url> \
       AZURE_OPENAI_API_KEY=<your-key> \
       AZURE_OPENAI_ENDPOINT=<your-endpoint> \
       AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment> \
       JWT_SECRET=<your-secret> \
       GITHUB_TOKEN_SECRET=<your-secret>
   ```

3. **Configure Environment Variables**
   
   Set all required environment variables in the Azure Container App configuration:
   - `DATABASE_URL`
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_DEPLOYMENT_NAME`
   - `JWT_SECRET`
   - `GITHUB_TOKEN_SECRET`

4. **Update CORS settings**
   
   Update the allowed origins in `app/main.py` to include your frontend domain.

## 📁 Project Structure

```
octopus-backend/
├── app/
│   ├── api/              # API route handlers
│   │   ├── issues.py     # Issue management endpoints
│   │   ├── repo.py       # Repository management
│   │   ├── solution.py   # Solution generation
│   │   ├── feedback.py   # Feedback handling
│   │   ├── ws.py         # WebSocket endpoints
│   │   └── github_repos.py
│   ├── auth/             # Authentication modules
│   │   ├── github.py     # GitHub OAuth
│   │   └── dependencies.py
│   ├── config/           # Configuration
│   │   └── settings.py   # Environment settings
│   ├── core/             # Core utilities
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   │   ├── github_service.py
│   │   ├── solution_generator.py
│   │   ├── issue_ingestor.py
│   │   └── ...
│   ├── utils/            # Utility functions
│   │   ├── db.py         # Database connection
│   │   ├── jwt.py        # JWT utilities
│   │   └── crypto.py     # Encryption utilities
│   ├── ws/               # WebSocket handlers
│   └── main.py           # FastAPI application
├── create_tables.py      # Database initialization
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
└── README.md
```

## 🔌 API Endpoints

### Authentication
- `POST /auth/github` - GitHub OAuth authentication

### Repositories
- `GET /repos` - List user repositories
- `POST /repos` - Add/analyze a repository
- `GET /repos/{repo_id}` - Get repository details

### Issues
- `GET /issues` - List issues (with optional difficulty filter)

### Solutions
- `GET /solutions/{issue_id}` - Get or generate solution for an issue
- `POST /solutions/{issue_id}/feedback` - Submit feedback for solution refinement

### WebSocket
- `WS /ws/{session_id}` - Real-time progress updates

## 🔐 Security

- JWT-based authentication
- Encrypted GitHub token storage
- CORS configuration for allowed origins
- User-based access control for repositories

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Yes |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | Yes |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Azure OpenAI deployment name | Yes |
| `JWT_SECRET` | Secret key for JWT token signing | Yes |
| `GITHUB_TOKEN_SECRET` | Secret key for encrypting GitHub tokens | Yes |

## 🧪 Development

### Running Tests
```bash
# Add test commands here when tests are implemented
```

### Code Style
```bash
# Follow PEP 8 guidelines
```

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📞 Support

[Add support/contact information here]
