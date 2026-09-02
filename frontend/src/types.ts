export type AgentStatus = 
  | 'idle' 
  | 'requirements' 
  | 'architecture' 
  | 'boilerplate' 
  | 'code_writing' 
  | 'review' 
  | 'testing' 
  | 'complete' 
  | 'error';

export interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'error';
  output?: string;
  error?: string;
  timestamp?: number;
}

export interface StreamMessage {
  type: 'agent_start' | 'agent_end' | 'code_token' | 'status' | 'complete' | 'error';
  agent?: string;
  message?: string;
  token?: string;
  data?: Record<string, unknown>;
  error?: string;
}

export interface GenerationResult {
  requirements: string;
  architecture: string;
  boilerplate: string;
  code: string;
  report: string;
  review_result?: {
    status: 'PASS' | 'FAIL';
    findings: Array<{
      severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
      explanation: string;
      affected_file?: string;
      recommended_correction: string;
    }>;
    summary: string;
  };
  test_cases?: Array<{
    name: string;
    purpose: string;
    steps: string[];
    expected_result: string;
  }>;
}
