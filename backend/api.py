import os
import json
import threading
import queue
import time
from fastapi.encoders import jsonable_encoder
from aapi import OPEN_AI_API
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from agents import Agents
from mod1_workflow import Module1Workflow
from events import set_event_queue, get_event_queue

app = FastAPI(
    title="Krishna Code AI",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    requirements: str


api_key = OPEN_AI_API

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set. Export it before starting FastAPI.")


llm1 = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0,
    api_key=api_key,
)
llm2 = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0,
    api_key=api_key,
)

# llm1 = ChatOllama(model="qwen2.5:3b", temperature=0)
# llm2 = ChatOllama(model="qwen2.5:3b", temperature=0)

agents = Agents(llm1, llm2)
workflow = Module1Workflow(agents)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "Krishna Code AI",
    }


@app.post("/api/generate")
def generate(request: GenerateRequest):
    requirements = request.requirements.strip()

    if not requirements:
        raise HTTPException(
            status_code=400,
            detail="Requirements cannot be empty.",
        )

    try:
        print(f"\n{'='*60}")
        print(f"Starting workflow with requirements...")
        print(f"{'='*60}\n")

        # Invoke workflow with proper state initialization
        result = workflow.graph.invoke(
            {
                "requirements": requirements,
                "architecture": "",
                "boilerplate": "",
                "code": "",
                "report": "",
                "test_cases": [],
                "review_result": None,
                "test_result": None,
            }
        )

        print(f"\n{'='*60}")
        print(f"Workflow completed successfully!")
        print(f"{'='*60}\n")

    except Exception as exc:
        print(f"\n{'='*60}")
        print(f"❌ WORKFLOW ERROR: {str(exc)}")
        print(f"{'='*60}\n")
        import traceback

        traceback.print_exc()
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


@app.get("/api/generate-stream")
async def generate_stream(requirements: str):
    """
    Stream-based code generation endpoint using Server-Sent Events.
    Emits real-time updates as each agent in the workflow completes.
    """
    requirements = requirements.strip()

    if not requirements:
        raise HTTPException(
            status_code=400,
            detail="Requirements cannot be empty.",
        )

    async def event_generator():
        """Generator that yields Server-Sent Events"""
        # Create event queue for this stream
        event_q: queue.Queue = queue.Queue()
        set_event_queue(event_q)

        try:
            # Emit start event
            yield f"data: {json.dumps({'type': 'status', 'message': 'Starting code generation workflow'})}\n\n"

            print(f"\n{'='*60}")
            print(f"Starting streaming workflow...")
            print(f"{'='*60}\n")

            # Run workflow in a thread so we can monitor the queue
            result_holder = {}
            exception_holder = {}

            def run_workflow():
                try:
                    result_holder["result"] = workflow.graph.invoke(
                        {
                            "requirements": requirements,
                            "architecture": "",
                            "boilerplate": "",
                            "code": "",
                            "report": "",
                            "test_cases": [],
                            "review_result": None,
                            "test_result": None,
                        }
                    )
                except Exception as e:
                    exception_holder["error"] = e
                finally:
                    # Signal completion
                    event_q.put({"type": "workflow_done"})

            workflow_thread = threading.Thread(target=run_workflow, daemon=True)
            workflow_thread.start()

            # Monitor queue and emit events
            workflow_complete = False
            while not workflow_complete:
                try:
                    # Get events from queue with timeout to avoid blocking forever
                    event = event_q.get(timeout=0.1)

                    if event["type"] == "workflow_done":
                        workflow_complete = True
                        break
                    elif event["type"] == "agent_start":
                        yield f"data: {json.dumps({'type': 'agent_start', 'agent': event.get('agent')})}\n\n"
                    elif event["type"] == "agent_end":
                        yield f"data: {json.dumps({'type': 'agent_end', 'agent': event.get('agent')})}\n\n"
                    elif event["type"] == "code_token":
                        yield f"data: {json.dumps({'type': 'code_token', 'token': event.get('token', '')})}\n\n"
                except queue.Empty:
                    # No events, continue waiting
                    if not workflow_thread.is_alive():
                        # Thread finished but didn't signal completion properly
                        workflow_complete = True
                        break
                    continue

            # Check if there was an error
            if "error" in exception_holder:
                raise exception_holder["error"]

            result = result_holder.get("result", {})

            print(f"\n{'='*60}")
            print(f"Streaming workflow completed!")
            print(f"{'='*60}\n")

            # Emit complete event with full result
            completion_data = {
                "type": "complete",
                "data": {
                    "requirements": result.get("requirements", ""),
                    "architecture": result.get("architecture", ""),
                    "boilerplate": result.get("boilerplate", ""),
                    "code": result.get("code", ""),
                    "report": result.get("report", ""),
                    "review_result": result.get("review_result"),
                    "test_cases": result.get("test_cases", []),
                },
            }
            # jsonable_encoder saare Pydantic models (jaise ReviewResult aur TestCases)
            # ko automatically normal dictionary me badal dega.
            safe_data = jsonable_encoder(completion_data)
            yield f"data: {json.dumps(safe_data)}\n\n"

        except Exception as exc:
            print(f"\n{'='*60}")
            print(f"❌ STREAMING WORKFLOW ERROR: {str(exc)}")
            print(f"{'='*60}\n")
            import traceback

            traceback.print_exc()
            error_message = f"Workflow execution failed: {str(exc)}"
            yield f"data: {json.dumps({'type': 'error', 'error': error_message})}\n\n"
        finally:
            # Clean up
            set_event_queue(None)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
