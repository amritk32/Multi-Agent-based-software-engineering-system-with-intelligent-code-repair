# execution_engine.py

from __future__ import annotations

import time
from enum import Enum

import docker
from docker.errors import (
    APIError,
    ContainerError,
    DockerException,
    ImageNotFound,
)
from pydantic import BaseModel

# ============================================================
# Execution Configuration
# ============================================================


class ExecutionConfig(BaseModel):
    image: str = "python:3.12-slim"

    timeout: int = 5

    cpu_limit: float = 1.0
    memory_limit: str = "512m"

    network_disabled: bool = True

    remove_container: bool = True


# ============================================================
# Execution Status
# ============================================================


class ExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    SYNTAX_ERROR = "SYNTAX_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    TIMEOUT = "TIMEOUT"
    ENVIRONMENT_ERROR = "ENVIRONMENT_ERROR"
    DOCKER_ERROR = "DOCKER_ERROR"


# ============================================================
# Execution Result
# ============================================================


class ExecutionResult(BaseModel):
    status: ExecutionStatus

    stdout: str = ""
    stderr: str = ""

    exit_code: int | None = None

    execution_time: float = 0.0

    error: str | None = None


# ============================================================
# Docker Execution Engine
# ============================================================


class DockerExecutionEngine:
    """
    Executes untrusted/generated Python code inside
    an isolated Docker container.

    Responsibilities:
    - Docker communication
    - Container lifecycle
    - Code execution
    - Timeout handling
    - Resource limits
    - Network isolation
    - Output collection
    - Failure classification
    - Cleanup
    """

    def __init__(
        self,
        config: ExecutionConfig | None = None,
    ) -> None:

        self.config = config or ExecutionConfig()

        try:
            self.client = docker.from_env()
            self.client.ping()

        except DockerException as exc:
            raise RuntimeError("Unable to connect to Docker Engine.") from exc

    # ========================================================
    # Public API
    # ========================================================

    def execute(self, code: str) -> ExecutionResult:
        """
        Execute Python source code inside Docker.
        """

        start_time = time.perf_counter()

        container = None

        try:

            self._validate_code(code)

            self._ensure_image()

            container = self._create_container(code)

            container.start()

            try:
                result = container.wait(timeout=self.config.timeout)

            except Exception as exc:

                if self._is_timeout(exc):

                    self._terminate_container(container)

                    execution_time = time.perf_counter() - start_time

                    return ExecutionResult(
                        status=ExecutionStatus.TIMEOUT,
                        execution_time=execution_time,
                        error=(
                            f"Execution exceeded " f"{self.config.timeout} seconds."
                        ),
                    )

                raise

            stdout, stderr = self._collect_output(container)

            execution_time = time.perf_counter() - start_time

            exit_code = result.get("StatusCode", 1)

            status = self._classify_execution(
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
            )

            return ExecutionResult(
                status=status,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time=execution_time,
                error=stderr if status != ExecutionStatus.SUCCESS else None,
            )

        except ImageNotFound as exc:

            return self._environment_error(
                start_time,
                f"Docker image not found: {self.config.image}",
                exc,
            )

        except ContainerError as exc:

            return self._environment_error(
                start_time,
                "Docker container execution failed.",
                exc,
            )

        except APIError as exc:

            return self._docker_error(
                start_time,
                str(exc),
            )

        except DockerException as exc:

            return self._environment_error(
                start_time,
                "Docker environment error.",
                exc,
            )

        except Exception as exc:

            return self._environment_error(
                start_time,
                "Unexpected execution error.",
                exc,
            )

        finally:

            if container is not None:

                self._cleanup(container)

    # ========================================================
    # Container Creation
    # ========================================================

    def _create_container(self, code: str):

        return self.client.containers.create(
            image=self.config.image,
            command=[
                "python",
                "-c",
                code,
            ],
            detach=True,
            network_disabled=self.config.network_disabled,
            mem_limit=self.config.memory_limit,
            nano_cpus=int(self.config.cpu_limit * 1_000_000_000),
            working_dir="/workspace",
        )

    # ========================================================
    # Docker Image
    # ========================================================

    def _ensure_image(self) -> None:

        try:

            self.client.images.get(self.config.image)

        except ImageNotFound:

            self.client.images.pull(self.config.image)

    # ========================================================
    # Output
    # ========================================================

    def _collect_output(self, container):

        stdout = container.logs(
            stdout=True,
            stderr=False,
        ).decode(
            "utf-8",
            errors="replace",
        )

        stderr = container.logs(
            stdout=False,
            stderr=True,
        ).decode(
            "utf-8",
            errors="replace",
        )

        return stdout, stderr

    # ========================================================
    # Failure Classification
    # ========================================================

    def _classify_execution(
        self,
        stdout: str,
        stderr: str,
        exit_code: int,
    ) -> ExecutionStatus:

        if exit_code == 0:

            return ExecutionStatus.SUCCESS

        error_text = stderr.lower()

        if (
            "syntaxerror" in error_text
            or "indentationerror" in error_text
            or "taberror" in error_text
        ):

            return ExecutionStatus.SYNTAX_ERROR

        return ExecutionStatus.RUNTIME_ERROR

    # ========================================================
    # Timeout Detection
    # ========================================================

    def _is_timeout(self, exc: Exception) -> bool:

        return isinstance(
            exc,
            TimeoutError,
        )

    # ========================================================
    # Container Termination
    # ========================================================

    def _terminate_container(self, container) -> None:

        try:

            container.kill()

        except DockerException:
            pass

    # ========================================================
    # Cleanup
    # ========================================================

    def _cleanup(self, container) -> None:

        if not self.config.remove_container:
            return

        try:

            container.remove(force=True)

        except DockerException:
            pass

    # ========================================================
    # Validation
    # ========================================================

    def _validate_code(self, code: str) -> None:

        if not isinstance(code, str):

            raise TypeError("Code must be a string.")

        if not code.strip():

            raise ValueError("Code cannot be empty.")

    # ========================================================
    # Error Helpers
    # ========================================================

    def _environment_error(
        self,
        start_time: float,
        message: str,
        exc: Exception,
    ) -> ExecutionResult:

        return ExecutionResult(
            status=ExecutionStatus.ENVIRONMENT_ERROR,
            execution_time=time.perf_counter() - start_time,
            error=f"{message} {exc}",
        )

    def _docker_error(
        self,
        start_time: float,
        message: str,
    ) -> ExecutionResult:

        return ExecutionResult(
            status=ExecutionStatus.DOCKER_ERROR,
            execution_time=time.perf_counter() - start_time,
            error=message,
        )
