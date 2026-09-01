# Krishna Code AI Frontend

React + TypeScript + Vite frontend for Krishna Code AI.

## Run

```bash
npm install
npm run dev
```

## Current state

This scaffold is intentionally backend-agnostic. It contains:

- glassmorphism AI developer UI
- workflow activity timeline
- project status
- requirements/architecture/boilerplate/code/review/test tabs
- generated code panel
- copy-code interaction
- structured test case cards
- prompt composer
- loading/spinner states

## Next integration

Connect the React client to the Python/LangGraph backend.

Recommended API contract:

POST /api/generate

Request:
```json
{
  "requirements": "..."
}
```

The backend should eventually stream workflow events and final artifacts rather
than returning one giant response.

Suggested event types:

- assistant_message
- agent_started
- agent_completed
- artifact_updated
- code_chunk
- test_case_created
- workflow_completed
- workflow_error
