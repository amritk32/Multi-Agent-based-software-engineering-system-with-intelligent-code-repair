# from langchain_openai import ChatOllama
from langchain_ollama import ChatOllama
from api import OPENAI_API_KEY
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

LLM = ChatOllama(model="qwen2.5:3b", temperature=0)


# ================================
# Define Schemas
# ================================


class TestCase(BaseModel):
    name: str
    purpose: str
    steps: list[str]
    expected_result: str


class TestingResult(BaseModel):
    status: Literal["PASS", "FAIL"]
    failure_type: (
        Literal["CODE", "BOILERPLATE", "ARCHITECTURE", "TEST", "ENVIRONMENT", "UNKNOWN"]
        | None
    ) = None

    test_cases: list[TestCase] = Field(default_factory=list)
    passed: int = 0
    failed: int = 0
    output: str = ""
    summary: str


class ReviewFinding(BaseModel):
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    explanation: str
    affected_file: str | None = None
    recommended_correction: str


class ReviewResult(BaseModel):
    status: Literal["PASS", "FAIL"]
    findings: list[ReviewFinding] = Field(default_factory=list)
    summary: str


class Module1(BaseModel):
    requirements: str = ""
    architecture: str = ""
    boilerplate: str = ""
    code: str = ""
    report: str = ""
    review_result: ReviewResult | None = None
    test_result: TestingResult | None = None


class Agents:
    """Agent implementations for Module 1.

    This class contains agent logic only. Workflow orchestration, routing,
    persistence, and execution infrastructure belong in separate layers.
    """

    REQUIREMENTS_SYSTEM_PROMPT = """
You are the Requirements Agent for Krishna Code AI.

Transform the user's raw software request into clear, structured requirements.
Identify the project's goals, users, functional requirements, non-functional
requirements, constraints, assumptions, inputs, outputs, and acceptance criteria.

Do not generate source code. Return a concise but detailed requirements
specification draft suitable for an architecture agent.
"""

    ARCHITECTURE_SYSTEM_PROMPT = """
You are the Architecture Agent for Krishna Code AI.

Design a production-oriented architecture from the supplied requirements.
Describe the project structure, components, responsibilities, dependencies,
interfaces or APIs, data storage decisions, configuration, and important
architectural decisions.

Do not generate complete application code. Return an implementation-ready
architecture specification.


Do NOT introduce:
- multiple source files
- file dictionaries
- GeneratedFile models
- project file trees
- multi-file code generation
- module-by-module file generation
"""

    BOILERPLATE_SYSTEM_PROMPT = """
You are the Boilerplate Generation Agent for Krishna Code AI.

Create a project skeleton based on the requirements and architecture.
Describe directories, files, configuration, interfaces, and minimal
structural code needed to establish the project.

Do not implement complete business logic. Clearly distinguish different modules of the architecture and
include only structural code.


Do NOT introduce:
- multiple source files
- file dictionaries
- GeneratedFile models
- project file trees
- multi-file code generation
- module-by-module file generation

Example -

class Module1:
    pass
    
class Module2:
    pass
    
def function():
    return {} 

if __name__ == "main":
    pass
"""

    CODE_WRITING_SYSTEM_PROMPT = """
You are the Code Writing Agent for Krishna Code AI.

Generate and maintain the COMPLETE application in ONE SINGLE SOURCE CODE FILE.

The application must never be split into multiple source files.

You will receive:
- requirements
- architecture
- boilerplate
- existing generated code
- correction feedback when applicable

Return the COMPLETE updated source code.

When existing code is provided, preserve correct functionality and modify only
what is necessary to address the supplied feedback.

Do not return explanations outside the source code.
"""

    REVIEW_SYSTEM_PROMPT = """
You are the Review Agent for Krishna Code AI.

Perform a comprehensive review of the generated code against the requirements
and architecture. Check correctness, logical consistency, architecture
adherence, maintainability, runtime risks, obvious security concerns, and
missing requirements.

Return a structured result with PASS or FAIL. Include actionable findings,
severity, affected file where applicable, explanation, and recommended
correction. PASS is appropriate only when no blocking or material issues
remain.
"""

    TESTING_SYSTEM_PROMPT = """
You are the Testing Agent for Krishna Code AI.

Analyze the generated single-file application against the requirements,
architecture, and boilerplate.

Determine whether the implementation passes.

If a failure exists, classify its primary cause as exactly one of:

CODE:
The implementation contains a coding, logic, syntax, or runtime defect.

BOILERPLATE:
The structural skeleton or initial project setup is incorrect or incomplete.

ARCHITECTURE:
The fundamental system design does not satisfy the requirements or causes
the implementation to be incorrect. The architecture itself must be revised.

TEST:
The generated test case is incorrect, invalid, or does not correctly represent
the requirements.

ENVIRONMENT:
The failure is caused by an execution environment, dependency, configuration,
or infrastructure issue rather than the generated application.

UNKNOWN:
The root cause cannot be confidently classified.

Do not claim that code was executed if an execution environment is unavailable.

Return a structured TestingResult.
"""

    def __init__(self, llm: ChatOllama) -> None:
        """Initialize agents with one reusable, injected LLM instance."""
        self.llm = llm

    def requirements_agent(self, user_requirements: str) -> str:
        """Convert raw user requirements into a structured specification."""
        return self._invoke_text(
            self.REQUIREMENTS_SYSTEM_PROMPT,
            user_requirements,
        )

    def architecture_agent(self, requirements: str) -> str:
        """Design an architecture from the structured requirements."""
        return self._invoke_text(
            self.ARCHITECTURE_SYSTEM_PROMPT,
            f"Requirements:\n{requirements}",
        )

    def boilerplate_agent(self, requirements: str, architecture: str) -> str:
        """Generate a project skeleton from requirements and architecture."""
        return self._invoke_text(
            self.BOILERPLATE_SYSTEM_PROMPT,
            (f"Requirements:\n{requirements}\n\n" f"Architecture:\n{architecture}"),
        )

    def code_writing_agent(
        self,
        requirements: str,
        architecture: str,
        boilerplate: str,
        existing_code: str,
        feedback: str = "",
    ) -> str:
        """Generate code for one target file or logical module."""
        prompt = (
            f"Requirements:\n{requirements}\n\n"
            f"Architecture:\n{architecture}\n\n"
            f"Boilerplate:\n{boilerplate}\n\n"
            f"Existing generated code/context:\n{existing_code}\n\n"
            f"Correction feedback:\n{feedback}"
        )
        return self._invoke_text(self.CODE_WRITING_SYSTEM_PROMPT, prompt)

    def review_agent(
        self,
        requirements: str,
        architecture: str,
        generated_code: str,
    ) -> ReviewResult:
        """Review generated code and return a machine-readable report."""
        prompt = (
            f"Requirements:\n{requirements}\n\n"
            f"Architecture:\n{architecture}\n\n"
            f"Generated code:\n{generated_code}"
        )
        return self._invoke_structured(
            self.REVIEW_SYSTEM_PROMPT,
            prompt,
            ReviewResult,
        )

    def testing_agent(
        self,
        requirements: str,
        architecture: str,
        generated_code: str,
    ) -> TestingResult:

        prompt = (
            f"Requirements:\n{requirements}\n\n"
            f"Architecture:\n{architecture}\n\n"
            f"Generated code:\n{generated_code}"
        )

        return self._invoke_structured(
            self.TESTING_SYSTEM_PROMPT,
            prompt,
            TestingResult,
        )

    def _invoke_text(self, system_prompt: str, user_prompt: str) -> str:
        """Invoke the LLM and normalize its text response."""
        try:
            response = self.llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
            content = response.content

            if isinstance(content, str):
                return content.strip()

            return "".join(
                block.get("text", "") for block in content if isinstance(block, dict)
            ).strip()
        except Exception as exc:
            raise RuntimeError("LLM text generation failed.") from exc

    def _invoke_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: type[BaseModel],
    ) -> BaseModel:
        """Invoke the LLM with a Pydantic structured-output schema."""
        try:
            structured_llm = self.llm.with_structured_output(schema)
            return structured_llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
        except Exception as exc:
            raise RuntimeError(
                f"Structured LLM generation failed for {schema.__name__}."
            ) from exc


agents = Agents(
    llm=ChatOllama(
        model="gpt-4o",
        temperature=0,
    )
)
