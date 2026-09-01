import { useMemo, useState } from "react";
import { demoCode, demoTests, initialWorkflowSteps } from "./data";
import type { AgentStatus, WorkflowStep } from "./types";

const tabs = [
  { id: "requirements", label: "Requirements", icon: "◈" },
  { id: "architecture", label: "Architecture", icon: "⌘" },
  { id: "boilerplate", label: "Boilerplate", icon: "□" },
  { id: "code", label: "Code", icon: "</>" },
  { id: "review", label: "Review", icon: "⌕" },
  { id: "tests", label: "Test Cases", icon: "✓" },
] as const;

type TabId = (typeof tabs)[number]["id"];

function StatusIcon({ status }: { status: AgentStatus }) {
  if (status === "running") {
    return <span className="status-spinner" aria-label="Running" />;
  }

  if (status === "completed") {
    return <span className="status-check">✓</span>;
  }

  if (status === "error") {
    return <span className="status-error">!</span>;
  }

  return <span className="status-pending">•</span>;
}

function App() {
  const [activeTab, setActiveTab] = useState<TabId>("code");
  const [prompt, setPrompt] = useState("");
  const [copied, setCopied] = useState(false);
  const [steps] = useState<WorkflowStep[]>(initialWorkflowSteps);
  const [isGenerating, setIsGenerating] = useState(false);

  const greeting = useMemo(
    () =>
      isGenerating
        ? "Sure — I'm working through the request step by step."
        : "Sure — I'll help you build your application step by step.",
    [isGenerating],
  );

  async function copyCode() {
    await navigator.clipboard.writeText(demoCode);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  function submitPrompt() {
    if (!prompt.trim()) return;

    setIsGenerating(true);

    // Backend integration will replace this demo behaviour.
    window.setTimeout(() => {
      setIsGenerating(false);
      setPrompt("");
    }, 1400);
  }

  return (
    <main className="app-shell">
      <aside className="sidebar glass-panel">
        <div className="brand">
          <div className="brand-mark">✦</div>
          <div>
            <div className="brand-title">KRISHNA</div>
            <div className="brand-accent">CODE AI</div>
          </div>
        </div>

        <button className="new-project-btn">
          <span>＋</span>
          New Project
        </button>

        <div className="sidebar-section-label">RECENT PROJECTS</div>

        <div className="project-list">
          {[
            "Python Calculator App",
            "Todo Web App",
            "Student Management API",
            "Weather Dashboard",
          ].map((project, index) => (
            <button
              key={project}
              className={`project-item ${index === 0 ? "active-project" : ""}`}
            >
              <span>{project}</span>
              <span className="project-dot" />
            </button>
          ))}
        </div>

        <div className="profile-card">
          <div className="avatar">K</div>
          <div className="profile-copy">
            <strong>Krishna Dev</strong>
            <span>AI Developer</span>
          </div>
          <span className="profile-chevron">⌄</span>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="workspace-title">
            <span className="bot-orb">🤖</span>
            <span>Krishna Code AI</span>
          </div>

          <div className="topbar-actions">
            <button className="theme-btn">◐&nbsp; Dark⌄</button>
            <button className="icon-btn" aria-label="Settings">
              ⚙
            </button>
          </div>
        </header>

        <section className="assistant-message glass-panel">
          <div>{greeting}</div>
          <div className="assistant-subtitle">
            Let&apos;s start by understanding your requirements.
          </div>
        </section>

        <section className="status-card glass-panel">
          <div>
            <span className="status-label">PROJECT STATUS</span>
            <strong>{isGenerating ? "Working..." : "Completed"}</strong>
          </div>
          <div className={`status-badge ${isGenerating ? "active" : ""}`}>
            {isGenerating ? <span className="status-spinner" /> : "✓"}
          </div>
        </section>

        <section className="content-grid">
          <section className="workflow-panel glass-panel">
            <div className="panel-heading">
              <span>WORKFLOW PROGRESS</span>
              <span className="panel-line" />
            </div>

            <div className="workflow-list">
              {steps.map((step) => (
                <div className="workflow-step" key={step.id}>
                  <div className={`workflow-node ${step.status}`}>
                    <StatusIcon status={isGenerating && step.id === "code" ? "running" : step.status} />
                  </div>
                  <div className="workflow-copy">
                    <div className="workflow-title-row">
                      <strong>{step.title}</strong>
                      <span>{step.time}</span>
                    </div>
                    <p>{step.description}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="workflow-complete">
              <span>✓</span>
              {isGenerating ? "Workflow in progress..." : "Workflow Completed 🎉"}
            </div>
          </section>

          <section className="artifact-panel glass-panel">
            <nav className="tab-bar">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  className={`tab ${activeTab === tab.id ? "active-tab" : ""}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <span>{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>

            {activeTab === "code" && (
              <>
                <div className="artifact-card code-card">
                  <div className="artifact-header">
                    <div>
                      <h2>Generated Code</h2>
                      <span className="artifact-meta">Python</span>
                    </div>
                    <button className="copy-btn" onClick={copyCode}>
                      {copied ? "✓ Copied" : "⧉ Copy"}
                    </button>
                  </div>

                  <div className="code-editor">
                    <div className="line-numbers">
                      {demoCode.split("\n").map((_, i) => (
                        <span key={i}>{i + 1}</span>
                      ))}
                    </div>
                    <pre>
                      <code>{demoCode}</code>
                    </pre>
                  </div>
                </div>

                <TestCases tests={demoTests} />
              </>
            )}

            {activeTab !== "code" && (
              <div className="empty-artifact">
                <div className="empty-orb">{tabs.find((t) => t.id === activeTab)?.icon}</div>
                <h2>{tabs.find((t) => t.id === activeTab)?.label}</h2>
                <p>
                  This panel is ready for live backend data. The current UI keeps
                  the same contract-driven structure for future LangGraph output.
                </p>
              </div>
            )}
          </section>
        </section>

        <section className="composer glass-panel">
          <textarea
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                submitPrompt();
              }
            }}
            placeholder="Describe the application you want to build..."
            rows={1}
          />
          <div className="composer-footer">
            <div className="composer-tools">
              <button>↗ Attach</button>
              <button>✧ Examples</button>
            </div>
            <button
              className="send-btn"
              onClick={submitPrompt}
              aria-label="Generate"
            >
              ➤
            </button>
          </div>
        </section>
      </section>
    </main>
  );
}

function TestCases({ tests }: { tests: typeof demoTests }) {
  return (
    <div className="tests-section">
      <div className="tests-heading">
        <div>
          <h2>Generated Test Cases</h2>
          <p>Structured tests returned by the testing agent.</p>
        </div>
        <button className="secondary-btn">⇩ Download All</button>
      </div>

      <div className="tests-grid">
        {tests.map((test) => (
          <article className="test-card" key={test.name}>
            <div className="test-title-row">
              <strong>{test.name}</strong>
              <span className="test-pass">✓</span>
            </div>

            <div className="test-label">Purpose</div>
            <p>{test.purpose}</p>

            <div className="test-label">Steps</div>
            <ol>
              {test.steps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>

            <div className="test-label">Expected Result</div>
            <p className="expected">{test.expectedResult}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

export default App;
