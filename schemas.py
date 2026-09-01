from pydantic import BaseModel, Field
from typing import Literal


class TestCase(BaseModel):
    name: str
    purpose: str
    steps: list[str]
    expected_result: str


class ExecutableTest(BaseModel):
    name: str
    code: str


class TestingResult(BaseModel):
    status: Literal["PASS", "FAIL"]

    failure_type: (
        Literal[
            "CODE",
            "BOILERPLATE",
            "ARCHITECTURE",
            "TEST",
            "ENVIRONMENT",
            "UNKNOWN",
        ]
        | None
    ) = None

    test_cases: list[TestCase] = Field(default_factory=list)
    executable_tests: list[ExecutableTest] = Field(default_factory=list)

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


class ExecutableTestList(BaseModel):
    tests: list[ExecutableTest] = Field(default_factory=list)


class Module1(BaseModel):
    requirements: str = ""
    architecture: str = ""
    boilerplate: str = ""
    code: str = ""
    report: str = ""
    test_cases: list[TestCase] = Field(default_factory=list)
    review_result: ReviewResult | None = None
    test_result: TestingResult | None = None


class TestCaseList(BaseModel):
    test_cases: list[TestCase] = Field(default_factory=list)
