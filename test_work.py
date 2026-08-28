from schemas import TestCase, ExecutableTest, ExecutableTestList, TestingResult
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from docker_execution import DockerExecutionEngine, ExecutionResult


class Testing:
    EXECUTABLE_TEST_SYSTEM_PROMPT = """
You are the Executable Test Generation Agent for Krishna Code AI.

Convert the supplied test specifications into executable Python tests.

You will receive:
- requirements
- generated application code
- structured test cases

For every supplied test case, generate an executable Python test.

Rules:
- Generate one executable test for each supplied TestCase.
- The test must verify the intended behaviour of the generated application.
- Use valid Python syntax.
- Do not modify the generated application.
- Do not invent functionality that is not present in the requirements.
- Do not generate Docker commands.
- Do not generate shell commands.
- Return only structured ExecutableTest objects.

The generated tests will later be executed inside an isolated Docker
environment.
"""

    ANALYZE_EXECUTION_RESULTS_SYSTEM_PROMPT = """
You are the Execution Analysis and Testing Agent for Krishna Code AI.

Your responsibility is to analyze the results produced by the isolated Docker
execution environment and determine whether the generated application and its
tests satisfy the given requirements.

You will receive:

1. Requirements
2. Architecture
3. Generated code
4. Execution results from Docker

The Docker execution results are objective execution evidence. They may contain
status, stdout, stderr, exit code, execution time, and error information.

Your task is to reason over ALL provided context and return a structured
TestingResult.

IMPORTANT:

- Do not claim that code was executed unless execution results explicitly
  provide evidence of execution.
- Do not infer a failure merely because an error field is present. Examine the
  execution status, stderr, exit code, and other available evidence.
- Distinguish between an application defect, a test defect, an architectural
  defect, a boilerplate defect, and an environment/infrastructure failure.
- Do not automatically classify every syntax or runtime error as CODE.
  Determine the most likely root cause from the complete context.
- If the evidence is insufficient to determine the root cause confidently,
  classify it as UNKNOWN.
- Do not invent execution output, errors, test results, or behaviour that is
  not present in the provided context.

Failure classification:

CODE:
The generated application contains a coding, logic, syntax, or runtime defect
that causes one or more tests to fail.

BOILERPLATE:
The generated structural skeleton or initial project setup is incorrect,
incomplete, or prevents the application from satisfying the requirements.

ARCHITECTURE:
The fundamental system design is incorrect or incompatible with the
requirements and must be revised rather than merely fixing implementation
details.

TEST:
The generated test or executable test is incorrect, invalid, or does not
accurately represent the requirements or intended application behaviour.

ENVIRONMENT:
The failure is caused by the execution environment, Docker infrastructure,
dependency, configuration, resource limitation, or another external execution
problem rather than the generated application.

UNKNOWN:
The available evidence is insufficient to confidently determine the root cause.

Evaluation procedure:

1. Compare the requirements against the architecture.
2. Compare the requirements and architecture against the generated code.
3. Inspect every provided execution result.
4. Determine which tests passed and which failed.
5. Examine stdout, stderr, exit codes, execution status, and errors.
6. Determine the most likely primary root cause of the failure.
7. If all relevant tests passed and the implementation satisfies the
   requirements, return PASS.
8. If one or more relevant tests failed, return FAIL and classify the primary
   failure cause.
9. Provide an accurate summary based only on the available evidence.

Return ONLY the structured TestingResult.
"""

    def __init__(self, execution_engine: DockerExecutionEngine, llm):
        self.execution_engine = execution_engine
        self.llm = llm

    def execute_test(
        self,
        generated_code: str,
        test_case: TestCase,
    ):
        test_code = self._build_test_code(
            generated_code=generated_code,
            test_case=test_case,
        )

        return self.execution_engine.execute(
            code=test_code,
        )

    def execute_tests(
        self,
        executable_tests: list[ExecutableTest],
    ) -> list[ExecutionResult]:

        results = []

        for test in executable_tests:

            result = self.execution_engine.execute(code=test.code)

            results.append(result)

        return results

    def _build_test_code(
        self,
        generated_code: str,
        test_case: TestCase,
    ) -> str:

        steps = "\n".join(f"# {step}" for step in test_case.steps)

        return (
            f"{generated_code}\n\n"
            f"# Test: {test_case.name}\n"
            f"# Purpose: {test_case.purpose}\n"
            f"{steps}\n"
            f"# Expected: {test_case.expected_result}\n"
        )

    def generate_executable_tests(
        self,
        requirements: str,
        generated_code: str,
        test_cases: list[TestCase],
    ) -> list[ExecutableTest]:

        prompt = (
            f"Requirements:\n{requirements}\n\n"
            f"Generated application:\n{generated_code}\n\n"
            f"Test cases:\n{test_cases}"
        )

        structured_llm = self.llm.with_structured_output(ExecutableTestList)

        result = structured_llm.invoke(
            [
                SystemMessage(content=self.EXECUTABLE_TEST_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
        )

        return result

    def analyse_execution_results(
        self,
        requirements: str,
        architecture: str,
        code: str,
        execution_results: list[ExecutionResult],
    ) -> TestingResult:

        prompt = (
            f"Requirements:\n{requirements}\n\n"
            f"Architecture:\n{architecture}\n\n"
            f"Code:\n{code}\n\n"
            f"Execution Results:\n{execution_results}\n\n"
        )

        structured_llm = self.llm.with_structured_output(TestingResult)

        result = structured_llm.invoke(
            [
                SystemMessage(content=self.ANALYZE_EXECUTION_RESULTS_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
        )

        return result

    def route_testing_result(self, testing_results: TestingResult) -> str | None:

        if testing_results.status == "PASS":
            return "SUCCESS"

        else:
            if testing_results.failure_type == "ARCHITECTURE":
                return "ARCHITECTURE"

            elif testing_results.failure_type == "BOILERPLATE":
                return "BOILERPLATE"

            elif testing_results.failure_type == "CODE":
                return "CODE"

            elif testing_results.failure_type == "TEST":
                return "TEST"

            elif testing_results.failure_type == "ENVIRONMENT":
                return "ENVIRONMENT"

            elif testing_results.failure_type == "UNKNOWN":
                return "UNKNOWN"
