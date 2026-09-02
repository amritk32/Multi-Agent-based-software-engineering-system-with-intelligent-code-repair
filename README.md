# Krishna Code AI

Krishna Code AI is a full-stack agentic code-generation workspace. Users submit software requirements through the React interface, then watch a FastAPI and LangGraph workflow analyze the request, design an architecture, generate Python code, review it, and create test cases.

## Project layout

```text
krishna-code-ai-stack/
├── backend/
│   ├── api.py              # FastAPI endpoints and SSE streaming
│   ├── agents.py           # LLM agent implementations
│   ├── events.py           # Workflow event queue
│   ├── mod1_workflow.py    # LangGraph workflow
│   ├── schemas.py          # Pydantic models
│   └── aapi.py             # Environment-based API key loading
├── frontend/
│   ├── src/                # React application and visual workspace
│   ├── package.json
│   └── vite.config.ts
├── run.sh                  # Start backend and frontend together
├── SETUP.sh                # Install project dependencies
└── README.md
```

`frontend/` and `backend/` are intentionally kept as sibling directories inside this single project folder. Upload the complete root folder to GitHub, excluding ignored files.

## Requirements

- Python 3.10 or newer
- Node.js 16 or newer
- npm
- An OpenAI API key

## Secure configuration

Set the API key in your shell. Never commit it to GitHub or place it directly in Python source:

```bash
export OPENAI_API_KEY="your-api-key"
```

The key is read by `backend/aapi.py` from `OPENAI_API_KEY`.

## Setup

From the project root:

```bash
chmod +x SETUP.sh run.sh
./SETUP.sh
```

The setup script installs the Python and frontend dependencies. It does not store your API key.

## Run the application

The simplest option is one command from the project root:

```bash
export OPENAI_API_KEY="your-api-key"
./run.sh
```

Or run both services separately:

```bash
# Terminal 1
cd backend
python -m uvicorn api:app --reload --port 8000

# Terminal 2
cd frontend
npm run dev
```

Open `http://localhost:5173`. The backend runs at `http://localhost:8000`.

## API endpoints

### Health check

```http
GET /api/health
```

### Standard generation

```http
POST /api/generate
Content-Type: application/json
```

```json
{
  "requirements": "Build a Python calculator application"
}
```

### Streaming generation

```http
GET /api/generate-stream?requirements=Build%20a%20Python%20calculator
Accept: text/event-stream
```

The stream reports agent lifecycle events, code chunks, completion data, and errors. The frontend renders code progressively and provides a copy action when output is available.

## Frontend commands

```bash
cd frontend
npm install
npm run dev       # Development server
npm run build     # TypeScript check and production build
npm run preview   # Preview the production build
```
