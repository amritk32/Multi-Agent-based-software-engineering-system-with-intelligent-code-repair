import { useState, useCallback, useRef } from 'react';
import { CheckCircle2, Circle, AlertCircle, Activity, ArrowUpRight, RotateCcw, Sparkles, Copy, Check } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { apiClient } from './api';
import { WorkflowStep, StreamMessage, GenerationResult } from './types';
import './styles.css';



const WORKFLOW_STEPS: WorkflowStep[] = [
  {
    id: 'requirements',
    name: 'Requirements',
    description: 'Analyzing requirements',
    status: 'pending',
  },
  {
    id: 'architecture',
    name: 'Architecture',
    description: 'Designing architecture',
    status: 'pending',
  },
  {
    id: 'boilerplate',
    name: 'Boilerplate',
    description: 'Creating structure',
    status: 'pending',
  },
  {
    id: 'code_writing',
    name: 'Code Writing',
    description: 'Generating code',
    status: 'pending',
  },
  {
    id: 'review',
    name: 'Review',
    description: 'Reviewing code',
    status: 'pending',
  },
  {
    id: 'generate_test_cases',
    name: 'Testing',
    description: 'Generating tests',
    status: 'pending',
  },
];

export default function App() {
  const [requirements, setRequirements] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState<WorkflowStep[]>(WORKFLOW_STEPS);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [generatedCode, setGeneratedCode] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [activeTab, setActiveTab] = useState('code');
  const [copied, setCopied] = useState(false);
  const codeRef = useRef('');

  const copyGeneratedCode = useCallback(async () => {
    if (!generatedCode) return;
    try {
      await navigator.clipboard.writeText(generatedCode);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      setError('Unable to copy generated code.');
    }
  }, [generatedCode]);

  const updateStep = useCallback((stepId: string, updates: Partial<WorkflowStep>) => {
    setSteps((prev) =>
      prev.map((step) =>
        step.id === stepId ? { ...step, ...updates } : step
      )
    );
  }, []);

  const handleStreamMessage = useCallback(
    (message: StreamMessage) => {
      console.log('Stream message:', message);

      switch (message.type) {
        case 'agent_start':
          updateStep(message.agent || '', {
            status: 'in-progress',
            timestamp: Date.now(),
          });
          break;

        case 'agent_end':
          updateStep(message.agent || '', {
            status: 'completed',
            timestamp: Date.now(),
          });
          break;

        case 'code_token':
          if (message.token) {
            codeRef.current += message.token;
            setGeneratedCode(codeRef.current);
          }
          break;

        case 'status':
          setError(null);
          break;

        case 'complete':
          if (message.data) {
            const fullResult = message.data as unknown as GenerationResult;
            setResult(fullResult);
            codeRef.current = fullResult.code || '';
            setGeneratedCode(codeRef.current);
          }
          setIsLoading(false);
          break;

        case 'error':
          setError(message.error || 'An error occurred');
          updateStep(message.agent || '', {
            status: 'error',
            error: message.error,
          });
          setIsLoading(false);
          break;
      }
    },
    [updateStep]
  );

  const handleGenerate = useCallback(async (req: string) => {
    if (!req.trim()) {
      setError('Please enter your requirements');
      return;
    }

    setIsLoading(true);
    setError(null);
    setGeneratedCode('');
    codeRef.current = '';
    setResult(null);
    setShowResults(true);
    setSteps(WORKFLOW_STEPS.map((step) => ({ ...step, status: 'pending', error: undefined })));

    try {
      const streamPromise = new Promise<void>((resolve, reject) => {
        apiClient.generateCodeStream(
          req,
          handleStreamMessage,
          (error) => {
            console.error('Stream error:', error);
            reject(error);
          },
          () => resolve()
        );
      });

      try {
        await streamPromise;
      } catch (streamError) {
        console.log('Stream endpoint not available, using standard API...', streamError);
        const fullResult = await apiClient.generateCode(req);
        setResult(fullResult);
        codeRef.current = fullResult.code || '';
        setGeneratedCode(codeRef.current);
        setSteps((prev) =>
          prev.map((step) => ({
            ...step,
            status: 'completed' as const,
            timestamp: Date.now(),
          }))
        );
        setIsLoading(false);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate code';
      setError(errorMessage);
      setIsLoading(false);
    }
  }, [handleStreamMessage]);

  const getStepIcon = (status: string) => {
    if (status === 'completed') {
      return <CheckCircle2 className="w-5 h-5 text-leaf-green" />;
    }
    if (status === 'in-progress') {
      return <div className="w-5 h-5 border-2 border-leaf-green border-t-transparent rounded-full animate-spin" />;
    }
    if (status === 'error') {
      return <AlertCircle className="w-5 h-5 text-red-500" />;
    }
    return <Circle className="w-5 h-5 text-gray-500" />;
  };

  if (showResults) {
    return (
      <div className="signal-shell">
        {/* Header */}
        <div className="signal-header">
          <div className="brand-mark"><span className="brand-icon"><Activity size={21} /></span> krishna.code</div>
          <nav className="header-nav"><span className="active">Workspace</span><span>Intelligence</span><span>Activity log</span></nav>
          <div className="network-status"><span className="status-dot" /><span className="mono-label">Agent network online</span></div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                setShowResults(false);
                setRequirements('');
                setSteps(WORKFLOW_STEPS.map((s) => ({ ...s, status: 'pending' })));
              }}
              className="new-generation"
            >
              <RotateCcw size={16} /> New run
            </button>
          </div>
        </div>

        <div className="results-shell">
          <div className="results-header"><div><div className="eyebrow">Intelligence workspace / 05</div><h1 className="results-title">Generation signal</h1></div></div>
          <div className="results-grid">
            {/* Workflow Steps */}
            <div className="lg:col-span-1">
              <div className="sticky top-20 space-y-3">
                <h2 className="workflow-title mono-label">Agent pipeline</h2>
                {steps.map((step) => (
                  <div
                    key={step.id}
                    className={`workflow-item ${
                      step.status === 'completed'
                        ? 'border-leaf-green/50 bg-leaf-green/5'
                        : step.status === 'in-progress'
                        ? 'border-leaf-green bg-leaf-green/10'
                        : step.status === 'error'
                        ? 'border-red-500/50 bg-red-500/5'
                        : 'border-gray-700 bg-gray-900/50'
                    }`}
                  >
                    <div className="mt-0.5">{getStepIcon(step.status)}</div>
                    <div className="flex-1 min-w-0">
                      <p>{step.name}</p>
                      <p className="text-xs text-gray-400 truncate">{step.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Code Display */}
            <div className="lg:col-span-2">
              <div className="space-y-4">
                {error && (
                  <div className="p-4 rounded-lg border border-red-500/50 bg-red-500/10">
                    <p className="text-sm text-red-300 font-mono">{error}</p>
                  </div>
                )}

                {/* Naya Colorful Code Block */}
                <div className="result-code">
                  {/* Custom Header */}
                  <div className="code-toolbar">
                    <span className="text-sm text-gray-300 font-medium flex items-center gap-2">
                      {isLoading && <div className="w-2 h-2 rounded-full bg-leaf-green animate-pulse" />}
                      {isLoading ? 'Generating Code...' : 'Generated Code'}
                    </span>
                    <div className="code-toolbar-actions">
                      <span className="language-tag">Python / live output</span>
                      <button className="copy-code-button" onClick={copyGeneratedCode} disabled={!generatedCode} title="Copy generated code">
                        {copied ? <Check size={15} /> : <Copy size={15} />}
                        {copied ? 'Copied' : 'Copy code'}
                      </button>
                    </div>
                  </div>
                  
                  {/* Syntax Highlighter */}
                  <div className="p-2">
                    <SyntaxHighlighter
                      language="python"
                      style={vscDarkPlus}
                      useInlineStyles={false}
                      customStyle={{
                        margin: 0,
                        background: "transparent",
                        fontSize: "13px",
                        fontFamily: "'JetBrains Mono', monospace",
                      }}
                      showLineNumbers={true}
                      lineNumberStyle={{ color: "#414a63", paddingRight: "16px", minWidth: "40px" }}
                    >
                      {generatedCode || "# Initializing Agent..."}
                    </SyntaxHighlighter>
                  </div>
                </div>

                {result && !isLoading && (
                  <div className="space-y-4">
                    {/* Tabs */}
                    <div className="result-tabs">
                      {[
                        { id: 'code', label: 'Code' },
                        { id: 'requirements', label: 'Requirements' },
                        { id: 'architecture', label: 'Architecture' },
                        { id: 'boilerplate', label: 'Boilerplate' },
                        { id: 'review', label: `Review (${result.review_result?.findings.length || 0})` },
                        { id: 'tests', label: `Tests (${result.test_cases?.length || 0})` },
                      ].map((tab) => (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id)}
                          className={`${activeTab === tab.id ? 'active' : ''} ${
                            activeTab === tab.id
                              ? 'border-leaf-green text-leaf-green'
                              : 'border-transparent text-gray-400 hover:text-gray-300'
                          }`}
                        >
                          {tab.label}
                        </button>
                      ))}
                    </div>

                    {/* Tab Content */}
                    <div className="result-tab-content max-h-96 overflow-y-auto">
                      {activeTab === 'requirements' && (
                        <p className="text-gray-200 text-sm whitespace-pre-wrap font-mono">
                          {result.requirements}
                        </p>
                      )}
                      {activeTab === 'architecture' && (
                        <p className="text-gray-200 text-sm whitespace-pre-wrap font-mono">
                          {result.architecture}
                        </p>
                      )}
                      {activeTab === 'boilerplate' && (
                        <p className="text-gray-200 text-sm whitespace-pre-wrap font-mono">
                          {result.boilerplate}
                        </p>
                      )}
                      {activeTab === 'review' && result.review_result && (
                        <div className="space-y-2">
                          <p
                            className={`font-semibold text-sm ${
                              result.review_result.status === 'PASS'
                                ? 'text-leaf-green'
                                : 'text-red-400'
                            }`}
                          >
                            {result.review_result.status}
                          </p>
                          <p className="text-gray-300 text-sm">{result.review_result.summary}</p>
                          {result.review_result.findings.map((finding, idx) => (
                            <div key={idx} className="mt-2 p-2 bg-gray-800 rounded text-xs text-gray-300">
                              <p className="font-semibold text-yellow-400">{finding.severity}</p>
                              <p>{finding.explanation}</p>
                            </div>
                          ))}
                        </div>
                      )}
                      {activeTab === 'tests' && (
                        <div className="space-y-2">
                          {result.test_cases?.map((tc, idx) => (
                            <div key={idx} className="p-2 bg-gray-800 rounded text-xs text-gray-300">
                              <p className="font-semibold text-leaf-green">{tc.name}</p>
                              <p className="text-gray-400">{tc.purpose}</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="signal-shell">
      <header className="signal-header">
        <div className="brand-mark"><span className="brand-icon"><Activity size={21} /></span> krishna.code</div>
        <nav className="header-nav"><span className="active">Workspace</span><span>Intelligence</span><span>Activity log</span></nav>
        <div className="network-status"><span className="status-dot" /><span className="mono-label">Agent network online</span></div>
        <button className="new-generation" title="Reset workspace" onClick={() => setRequirements('')}><RotateCcw size={16} /></button>
      </header>

      <main className="intake-layout">
        <section>
          <div className="eyebrow">Intelligence workspace / 04</div>
          <h1 className="hero-title">Turn the<br />noise <em>into signal.</em></h1>
          <p className="hero-copy">A focused engineering desk for turning your ideas into working software, with an agent network that explains every decision.</p>
          <div className="hero-meta"><span className="meta-icon"><Sparkles size={15} /></span> Complete agent orchestration <ArrowUpRight size={15} /></div>
          <div className="hero-stats"><div className="hero-stat">04<small>agents ready</small></div><div className="hero-stat">7D<small>always learning</small></div><div className="hero-stat">AI<small>native workflow</small></div></div>
        </section>

        <section className="intake-panel">
          <div className="panel-topline mono-label"><span>Node_04 / intake</span><span className="secure-link">Secure link</span></div>
          <div className="panel-question">What should we investigate?</div>
          <textarea
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            placeholder="e.g. A REST API for a todo app with database integration"
            className="intake-textarea"
            rows={2}
            onKeyDown={(e) => { if (e.ctrlKey && e.key === 'Enter') handleGenerate(requirements); }}
          />
          <div className="panel-controls">
            <button className="panel-submit" onClick={() => handleGenerate(requirements)} disabled={isLoading || !requirements.trim()} title="Start agentic workflow">
              <span>{isLoading ? 'Launching Workflow...' : 'Start Agentic Workflow 🚀'}</span>
              <ArrowUpRight size={19} />
            </button>
          </div>
          <div className="pipeline"><div className="pipeline-label mono-label">Agent pipeline <span>/ ready to deploy</span></div><div className="pipeline-nodes"><div className="pipeline-node"><span className="node-icon"><Activity size={14} /></span>Discover</div><span className="pipeline-line" /><div className="pipeline-node"><span className="node-icon"><Circle size={14} /></span>Verify</div><span className="pipeline-line" /><div className="pipeline-node"><span className="node-icon"><Sparkles size={14} /></span>Synthesize</div></div></div>
          {error && <div className="error-banner">{error}</div>}
        </section>
      </main>
    </div>
  );
}
