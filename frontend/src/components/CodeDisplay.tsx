import React, { useState } from 'react';
import { Copy, CheckCircle2 } from 'lucide-react';

interface CodeDisplayProps {
  code: string;
  language?: string;
  title?: string;
  isStreaming?: boolean;
}

export const CodeDisplay: React.FC<CodeDisplayProps> = ({
  code,
  language = 'python',
  title = 'Generated Code',
  isStreaming = false,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const lineCount = code.split('\n').length;

  return (
    <div className="w-full bg-gray-900 rounded-xl border border-gray-800 overflow-hidden shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-gray-900/80 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full transition-all ${isStreaming ? 'bg-leaf-green animate-pulse' : 'bg-leaf-green'}`} />
          <span className="text-base font-semibold text-white">{title}</span>
          {isStreaming && (
            <span className="text-xs text-leaf-green ml-2 animate-pulse">Generating...</span>
          )}
        </div>
        <button
          onClick={handleCopy}
          disabled={!code}
          className="flex items-center gap-2 px-4 py-2 bg-leaf-green/20 hover:bg-leaf-green/30 disabled:bg-gray-800 disabled:cursor-not-allowed text-sm text-leaf-green rounded-lg transition-colors border border-leaf-green/30 hover:border-leaf-green/50"
        >
          {copied ? (
            <>
              <CheckCircle2 size={16} />
              Copied!
            </>
          ) : (
            <>
              <Copy size={16} />
              Copy
            </>
          )}
        </button>
      </div>

      {/* Code Content */}
      <div className="relative overflow-hidden">
        <pre className="px-6 py-6 text-base leading-relaxed text-gray-100 overflow-x-auto font-mono bg-black/30">
          <code className={`language-${language}`}>
            {code || (
              <span className="text-gray-500 italic">
                {isStreaming ? 'Generating code...' : 'No code generated yet'}
              </span>
            )}
            {isStreaming && code && <span className="code-cursor" />}
          </code>
        </pre>

        {/* Gradient overlay for long code */}
        {code && lineCount > 20 && (
          <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-gray-900 via-gray-900/50 to-transparent pointer-events-none" />
        )}
      </div>

      {/* Footer Info */}
      {code && (
        <div className="px-6 py-3 bg-gray-900/80 border-t border-gray-800 text-xs text-gray-400 flex gap-4">
          <span className="flex items-center gap-1">
            <span className="text-leaf-green">•</span>
            {lineCount} lines
          </span>
          <span className="flex items-center gap-1">
            <span className="text-leaf-green">•</span>
            {code.length} characters
          </span>
          {isStreaming && (
            <span className="flex items-center gap-1 text-leaf-green animate-pulse">
              <span className="text-leaf-green">•</span>
              Streaming...
            </span>
          )}
        </div>
      )}
    </div>
  );
};
