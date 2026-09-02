from agents import Agents, Module1
from langgraph.graph import StateGraph, START, END
from events import emit_event

MAX_CODE_REPAIR = 3
MAX_ARCHITECTURE_REFINEMENT = 2
MAX_TEST_RETRY = 2


class Module1Workflow:

    def __init__(self, agents: Agents):
        self.agents = agents
        self.graph = self._build_graph()

    def requirements_node(self, state: Module1):
        print("➡️ Requirements Agent")
        emit_event({"type": "agent_start", "agent": "requirements"})
        try:
            state.requirements = self.agents.requirements_agent(state.requirements)
            print("Requirements Agent Finished.")
            emit_event({"type": "agent_end", "agent": "requirements"})
        except Exception as e:
            print(f"❌ Requirements Agent Error: {str(e)}")
            raise
        return state

    def architecture_node(self, state: Module1):
        print("➡️ Architecture Agent")
        emit_event({"type": "agent_start", "agent": "architecture"})
        try:
            state.architecture = self.agents.architecture_agent(state.requirements)
            print("Architecture Agent Finished.")
            emit_event({"type": "agent_end", "agent": "architecture"})
        except Exception as e:
            print(f"❌ Architecture Agent Error: {str(e)}")
            raise
        return state

    def boilerplate_node(self, state: Module1):
        print("➡️ Boilerplate Agent")
        emit_event({"type": "agent_start", "agent": "boilerplate"})
        try:
            state.boilerplate = self.agents.boilerplate_agent(
                state.requirements,
                state.architecture,
            )
            print("Boilerplate Agent ended")
            emit_event({"type": "agent_end", "agent": "boilerplate"})
        except Exception as e:
            print(f"❌ Boilerplate Agent Error: {str(e)}")
            raise
        return state

    def code_writing_node(self, state: Module1):
        print("➡️ Code Writing Agent")
        emit_event({"type": "agent_start", "agent": "code_writing"})
        try:
            feedback = ""

            if state.review_result:
                feedback += state.review_result.summary

                for finding in state.review_result.findings:
                    feedback += (
                        f"\nSeverity: {finding.severity}"
                        f"\nExplanation: {finding.explanation}"
                        f"\nCorrection: {finding.recommended_correction}"
                    )

            if state.test_result:
                feedback += (
                    f"\nTesting result: {state.test_result.summary}"
                    f"\nFailure type: {state.test_result.failure_type}"
                    f"\nOutput: {state.test_result.output}"
                )

            state.code = self.agents.code_writing_agent(
                requirements=state.requirements,
                architecture=state.architecture,
                boilerplate=state.boilerplate,
                existing_code=state.code,
                feedback=feedback,
                on_token=lambda token: emit_event(
                    {"type": "code_token", "token": token}
                ),
            )

            print("Code Writing Agent Finished.")
            emit_event({"type": "agent_end", "agent": "code_writing"})
        except Exception as e:
            print(f"❌ Code Writing Agent Error: {str(e)}")
            raise

        return state

    def review_node(self, state: Module1):
        print("➡️ Review Agent")
        emit_event({"type": "agent_start", "agent": "review"})
        try:
            result = self.agents.review_agent(
                requirements=state.requirements,
                architecture=state.architecture,
                generated_code=state.code,
            )

            # state.review_result = result  <-- Isko hata ke ye likh de:
            state.review_result = result.model_dump()
            state.report = result.summary

            print("Review Agent Finished.")
            emit_event({"type": "agent_end", "agent": "review"})
        except Exception as e:
            print(f"❌ Review Agent Error: {str(e)}")
            raise

        return state

    def generate_test_cases_node(self, state: Module1):
        print("➡️ Generate Test Cases Agent")
        emit_event({"type": "agent_start", "agent": "generate_test_cases"})
        try:
            result = self.agents.generate_test_cases(
                requirements=state.requirements,
                architecture=state.architecture,
                boilerplate=state.boilerplate,
                generated_code=state.code,
            )

            print("Test cases generated.")
            print("\nNumber of test cases ", len(result))

            state.test_cases = [tc.model_dump() for tc in result]

            # state.test_cases = result

            print("Test case generation Agent Finished.")
            emit_event({"type": "agent_end", "agent": "generate_test_cases"})
        except Exception as e:
            print(f"❌ Test Cases Agent Error: {str(e)}")
            raise

        return state

    # def testing_node(self, state: Module1):
    #     print("➡️ Testing Node")
    #     state.test_result = self.agents.testing_agent(
    #         requirements=state.requirements,
    #         architecture=state.architecture,
    #         generated_code=state.code,
    #     )

    #     return state

    # def review_router(self, state: Module1) -> str:

    #     if state.review_result.status == "PASS":
    #         return "testing"

    #     return "code_writing"

    # def testing_router(self, state: Module1) -> str:
    #     result = state.test_result
    #     if result.status == "PASS":
    #         return "end"
    #     return result.failure_type or "UNKNOWN"

    def _build_graph(self):

        workflow = StateGraph(Module1)

        workflow.add_node(
            "requirements",
            self.requirements_node,
        )

        workflow.add_node(
            "architecture",
            self.architecture_node,
        )

        workflow.add_node(
            "boilerplate",
            self.boilerplate_node,
        )

        workflow.add_node(
            "code_writing",
            self.code_writing_node,
        )

        workflow.add_node(
            "review",
            self.review_node,
        )

        workflow.add_node(
            "generate_test_cases",
            self.generate_test_cases_node,
        )

        workflow.add_edge(START, "requirements")

        workflow.add_edge(
            "requirements",
            "architecture",
        )

        workflow.add_edge(
            "architecture",
            "boilerplate",
        )

        workflow.add_edge(
            "boilerplate",
            "code_writing",
        )

        workflow.add_edge(
            "code_writing",
            "review",
        )

        workflow.add_edge(
            "review",
            "generate_test_cases",
        )

        workflow.add_edge("generate_test_cases", END)

        return workflow.compile()
