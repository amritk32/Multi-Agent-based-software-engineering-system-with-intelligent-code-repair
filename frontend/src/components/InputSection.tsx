import React, { useState } from 'react';
import { Send } from 'lucide-react';

interface InputSectionProps {
  onSubmit: (requirements: string) => void;
  isLoading: boolean;
}

export const InputSection: React.FC<InputSectionProps> = ({ onSubmit, isLoading }) => {
  const [requirements, setRequirements] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (requirements.trim()) {
      onSubmit(requirements.trim());
    }
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="requirements" className="block text-sm font-semibold text-gray-200 mb-2">
            Project Requirements
          </label>
          <textarea
            id="requirements"
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            placeholder="Describe what you want to build. Be specific about functionality, constraints, and expected behavior..."
            disabled={isLoading}
            className="w-full h-32 px-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 resize-none transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-400">
            {requirements.length} characters
          </div>
          <button
            type="submit"
            disabled={isLoading || !requirements.trim()}
            className="flex items-center gap-2 px-6 py-2.5 bg-primary-500 hover:bg-primary-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors"
          >
            <Send size={18} />
            Generate Code
          </button>
        </div>
      </form>
    </div>
  );
};
