import React from 'react';

interface TabNavigationProps {
  tabs: { id: string; label: string; count?: number }[];
  activeTab: string;
  onChange: (tabId: string) => void;
}

export const TabNavigation: React.FC<TabNavigationProps> = ({
  tabs,
  activeTab,
  onChange,
}) => {
  return (
    <div className="flex gap-2 border-b border-gray-700 overflow-x-auto">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
            activeTab === tab.id
              ? 'border-primary-500 text-primary-400'
              : 'border-transparent text-gray-400 hover:text-gray-300'
          }`}
        >
          {tab.label}
          {tab.count !== undefined && (
            <span className="ml-2 px-2 py-0.5 bg-gray-700 rounded text-xs">
              {tab.count}
            </span>
          )}
        </button>
      ))}
    </div>
  );
};
