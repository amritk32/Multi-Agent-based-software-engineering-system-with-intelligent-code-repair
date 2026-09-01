import type { TestCase, WorkflowStep } from "./types";

export const initialWorkflowSteps: WorkflowStep[] = [
  {
    id: "requirements",
    title: "Understanding Requirements",
    description: "Analyzing what you want to build...",
    status: "completed",
    time: "10:42:15 AM",
  },
  {
    id: "architecture",
    title: "Finalising Architecture",
    description: "Designing the high-level architecture...",
    status: "completed",
    time: "10:42:18 AM",
  },
  {
    id: "boilerplate",
    title: "Designing Project Structure",
    description: "Planning the project skeleton...",
    status: "completed",
    time: "10:42:20 AM",
  },
  {
    id: "code",
    title: "Writing Code",
    description: "Generating the implementation...",
    status: "completed",
    time: "10:42:30 AM",
  },
  {
    id: "review",
    title: "Reviewing Code",
    description: "Checking the generated implementation...",
    status: "completed",
    time: "10:42:35 AM",
  },
  {
    id: "tests",
    title: "Generating Test Cases",
    description: "Preparing test cases for validation...",
    status: "completed",
    time: "10:42:38 AM",
  },
];

export const demoCode = `class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b


if __name__ == "__main__":
    calculator = Calculator()
    print("Krishna Code AI Calculator")`;

export const demoTests: TestCase[] = [
  {
    name: "test_add",
    purpose: "Verify addition functionality.",
    steps: ["Create calculator instance.", "Call add(5, 3)."],
    expectedResult: "Should return 8.",
  },
  {
    name: "test_subtract",
    purpose: "Verify subtraction functionality.",
    steps: ["Create calculator instance.", "Call subtract(10, 4)."],
    expectedResult: "Should return 6.",
  },
  {
    name: "test_multiply",
    purpose: "Verify multiplication functionality.",
    steps: ["Create calculator instance.", "Call multiply(5, 4)."],
    expectedResult: "Should return 20.",
  },
  {
    name: "test_divide",
    purpose: "Verify division functionality.",
    steps: ["Create calculator instance.", "Call divide(15, 3)."],
    expectedResult: "Should return 5.",
  },
  {
    name: "test_divide_by_zero",
    purpose: "Verify division-by-zero handling.",
    steps: ["Create calculator instance.", "Call divide(10, 0)."],
    expectedResult: "Should raise ValueError.",
  },
];
