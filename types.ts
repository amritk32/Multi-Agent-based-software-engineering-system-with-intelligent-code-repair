export type AgentStatus = "pending" | "running" | "completed" | "error";

export type WorkflowStep = {
  id: string;
  title: string;
  description: string;
  status: AgentStatus;
  time?: string;
};

export type TestCase = {
  name: string;
  purpose: string;
  steps: string[];
  expectedResult: string;
};

export type WorkflowResult = {
  requirements: string;
  architecture: string;
  boilerplate: string;
  code: string;
  reviewResult?: unknown;
  testCases: TestCase[];
};
