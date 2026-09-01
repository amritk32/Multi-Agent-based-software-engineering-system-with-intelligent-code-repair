from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import Agents
from aapi import OPEN_AI_API
from mod1_workflow import Module1Workflow
from langchain_openai import ChatOpenAI

# ============================================================
# FastAPI application
# ============================================================

app = FastAPI(
    title="Krishna Code AI",
    version="0.1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Request schema
# ============================================================


class GenerateRequest(BaseModel):
    requirements: str


# ============================================================
# AI system initialization
# ============================================================

llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0,
    # api_key=OPEN_AI_API,
)

agents = Agents(llm)
workflow = Module1Workflow(agents)


# ============================================================
# Health endpoint
# ============================================================


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "Krishna Code AI",
    }


# ============================================================
# Generation endpoint
# ============================================================


@app.post("/api/generate")
def generate(request: GenerateRequest):

    requirements = request.requirements.strip()

    if not requirements:
        raise HTTPException(
            status_code=400,
            detail="Requirements cannot be empty.",
        )

    initial_state = {
        "requirements": requirements,
    }

    try:
        result = workflow.graph.invoke(initial_state)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {exc}",
        ) from exc

    return {
        "requirements": result.get("requirements", ""),
        "architecture": result.get("architecture", ""),
        "boilerplate": result.get("boilerplate", ""),
        "code": result.get("code", ""),
        "report": result.get("report", ""),
        "review_result": result.get("review_result"),
        "test_cases": result.get("test_cases", []),
    }
