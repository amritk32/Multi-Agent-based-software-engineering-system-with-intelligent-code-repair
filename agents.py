# from langchain_openai import ChatOllama
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from aapi import OPEN_AI_API
from langchain_core.messages import HumanMessage, SystemMessage
from schemas import *

LLM = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0,
    # api_key=OPEN_AI_API,
)


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
    TEST_CASE_GENERATION_SYSTEM_PROMPT = """
You are the Test Case Generation Agent for Krishna Code AI.

Your responsibility is to design comprehensive and meaningful test cases for
the generated single-file application.

Analyze all of the following:

- User requirements
- Generated architecture
- Generated boilerplate
- Generated source code

Generate test cases that verify whether the implementation actually satisfies
the requirements and follows the intended architecture.

Test cases should cover, where applicable:

- Core functionality
- Normal / valid inputs
- Boundary conditions
- Invalid inputs
- Edge cases
- Error handling
- Important business logic
- Integration between major components
- Requirement-specific behavior
- Security-sensitive behavior when relevant

Do not generate random or unnecessary tests.

Each test case must have:

- A clear and unique name
- A specific purpose
- Concrete execution steps
- A clearly observable expected result

The test cases must be sufficiently precise that another execution system can
use them to construct and execute automated tests.

Do not execute the tests.

Do not determine whether the application passes or fails.

Do not classify failures.

Do not modify the generated application.

Return only a structured TestCaseList.
"""
    TESTING_SYSTEM_PROMPT = """
You are the Testing and Failure Analysis Agent for Krishna Code AI.

Analyze the generated single-file application and the actual test execution
results against the requirements, architecture, and boilerplate.

Determine whether the implementation passes the generated test suite.

Use the provided execution results as the primary evidence for determining
test outcomes. Do not claim that a test passed or failed without sufficient
evidence.

If a failure exists, classify its primary root cause as exactly one of:

CODE:
The generated implementation contains a coding, logical, syntax, or runtime
defect.

BOILERPLATE:
The structural skeleton or initial implementation setup is incorrect or
incomplete and caused the failure.

ARCHITECTURE:
The fundamental system design is incorrect or does not satisfy the
requirements. The architecture itself must be revised.

TEST:
The generated test case is incorrect, invalid, ambiguous, or does not
accurately represent the requirements.

ENVIRONMENT:
The failure is caused by the execution environment, dependency, configuration,
resource limitation, sandbox, or infrastructure rather than the generated
application.

UNKNOWN:
The root cause cannot be determined confidently from the available evidence.

Important rules:

- Do not claim that code was executed unless actual execution results are
  provided.
- Do not classify an issue as CODE merely because a test failed.
- Consider the architecture and boilerplate before assigning CODE.
- If the test itself is invalid, classify it as TEST.
- If execution infrastructure caused the failure, classify it as ENVIRONMENT.
- If multiple issues exist, select the primary root cause.
- Clearly explain the reasoning behind the failure classification.

Return a structured TestingResult.
"""

    def __init__(self, llm: ChatOpenAI) -> None:
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

    # def testing_agent(
    #     self,
    #     requirements: str,
    #     architecture: str,
    #     generated_code: str,
    # ) -> TestingResult:

    #     prompt = (
    #         f"Requirements:\n{requirements}\n\n"
    #         f"Architecture:\n{architecture}\n\n"
    #         f"Generated code:\n{generated_code}"
    #     )

    #     return self._invoke_structured(
    #         self.TESTING_SYSTEM_PROMPT,
    #         prompt,
    #         TestingResult,
    #     )

    def generate_test_cases(
        self,
        requirements: str,
        architecture: str,
        boilerplate: str,
        generated_code: str,
    ) -> list[TestCase]:

        print("🧪 Generate Test Cases: started")

        prompt = (
            f"Requirements:\n{requirements}\n\n"
            f"Architecture:\n{architecture}\n\n"
            f"Boilerplate:\n{boilerplate}\n\n"
            f"Generated code:\n{generated_code}"
        )

        print("🧪 Prompt prepared")

        structured_llm = self.llm.with_structured_output(TestCaseList)

        print("🧪 Calling Qwen for structured test cases...")

        result = structured_llm.invoke(
            [
                SystemMessage(content=self.TESTING_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
        )

        print("✅ Qwen returned structured test cases")

        return result.test_cases

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
    llm=ChatOpenAI(
        model="gpt-5-mini",
        temperature=0,
        # api_key=OPEN_AI_API,
    )
)
