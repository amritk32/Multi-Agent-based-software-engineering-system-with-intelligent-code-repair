import React from 'react';
import { CheckCircle2, Circle, Clock, AlertCircle } from 'lucide-react';
import { WorkflowStep } from '../types';

interface StepIndicatorProps {
  steps: WorkflowStep[];
}

export const StepIndicator: React.FC<StepIndicatorProps> = ({ steps }) => {
  const getStatusIcon = (status: WorkflowStep['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-6 h-6 text-leaf-green" />;
      case 'in-progress':
        return <Clock className="w-6 h-6 text-primary-500 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-6 h-6 text-red-400" />;
      default:
        return <Circle className="w-6 h-6 text-gray-500" />;
    }
  };

  const getStatusColor = (status: WorkflowStep['status']): string => {
    switch (status) {
      case 'completed':
        return 'border-leaf-green bg-leaf-green/10';
      case 'in-progress':
        return 'border-primary-500 bg-primary-500/10';
      case 'error':
        return 'border-red-400 bg-red-400/10';
      default:
        return 'border-gray-600 bg-gray-800/50';
    }
  };

  return (
    <div className="w-full">
      <h3 className="text-sm font-semibold text-gray-200 mb-4">Workflow Progress</h3>
      <div className="space-y-3">
        {steps.map((step) => (
          <div key={step.id} className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-1">
              {getStatusIcon(step.status)}
            </div>
            <div className="flex-grow min-w-0">
              <div className={`p-3 rounded-lg border ${getStatusColor(step.status)} transition-all`}>
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-semibold text-gray-100">{step.name}</h4>
                  <span className="text-xs text-gray-400">{step.status}</span>
                </div>
                <p className="text-sm text-gray-300 mb-1">{step.description}</p>
                {step.error && (
                  <p className="text-xs text-red-300 mt-2">Error: {step.error}</p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
