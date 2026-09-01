from agents import Agents, Module1
from langgraph.graph import StateGraph, START, END

MAX_CODE_REPAIR = 3
MAX_ARCHITECTURE_REFINEMENT = 2
MAX_TEST_RETRY = 2


class Module1Workflow:

    def __init__(self, agents: Agents):
        self.agents = agents
        self.graph = self._build_graph()

    def requirements_node(self, state: Module1):
        print("➡️ Requirements Agent")
        state.requirements = self.agents.requirements_agent(state.requirements)
        return state

    def architecture_node(self, state: Module1):
        print("➡️ Architecture Node")
        state.architecture = self.agents.architecture_agent(state.requirements)
        return state

    def boilerplate_node(self, state: Module1):
        print("➡️ Boilerplate Node")
        state.boilerplate = self.agents.boilerplate_agent(
            state.requirements,
            state.architecture,
        )

        print("Boilerplate node ended")
        return state

    def code_writing_node(self, state: Module1):
        print("➡️ Code Writing Node")
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
        )

        return state

    def review_node(self, state: Module1):
        print("➡️ Review Node")
        result = self.agents.review_agent(
            requirements=state.requirements,
            architecture=state.architecture,
            generated_code=state.code,
        )

        state.review_result = result
        state.report = result.summary

        return state

    def generate_test_cases_node(self, state: Module1):
        print("➡️ Generate Test Cases Node")

        result = self.agents.generate_test_cases(
            requirements=state.requirements,
            architecture=state.architecture,
            boilerplate=state.boilerplate,
            generated_code=state.code,
        )

        print("Test cases generated.")

        print("\nNumber of test cases ", len(result))

        state.test_cases = result

        print("Test cases stored in state.")

        return state

    def testing_node(self, state: Module1):
        print("➡️ Testing Node")
        state.test_result = self.agents.testing_agent(
            requirements=state.requirements,
            architecture=state.architecture,
            generated_code=state.code,
        )

        return state

    def review_router(self, state: Module1) -> str:

        if state.review_result.status == "PASS":
            return "testing"

        return "code_writing"

    def testing_router(self, state: Module1) -> str:
        result = state.test_result
        if result.status == "PASS":
            return "end"
        return result.failure_type or "UNKNOWN"

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
