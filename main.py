from module1 import Agents
from mod1_workflow import Module1Workflow
from langchain_ollama import ChatOllama


def main():

    llm = ChatOllama(
        model="qwen2.5:3b",
        temperature=0,
    )

    agents = Agents(llm)

    workflow = Module1Workflow(agents)

    initial_state = {
        "requirements": """
        Build a Python calculator application.
        It should support addition, subtraction, multiplication and division.
        Handle division by zero properly.
        """,
    }

    print("🚀 Workflow started")
    result = workflow.graph.invoke(initial_state)
    print("✅ Workflow finished")
    print(result)
    print("\n========== FINAL RESULT ==========\n")
    print(result["code"])


if __name__ == "__main__":
    main()
