import { useState } from 'react';
import { Code, Play, Square } from 'lucide-react';
import { HealthCheck } from './HealthCheck';
import { IngestPanel } from './IngestPanel';
import { QueryPanel } from './QueryPanel';

export const ApiTester = () => {
  const [activeTab, setActiveTab] = useState('query');

  const tabs = [
    { id: 'health', label: 'Health Check', component: HealthCheck },
    { id: 'ingest', label: 'Document Ingest', component: IngestPanel },
    { id: 'query', label: 'Document Query', component: QueryPanel },
  ];

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <Code className="w-8 h-8 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">Legal SLM RAG POC</h1>
          </div>
          <p className="text-lg text-gray-600">
            Test your Legal Document API with this interactive interface
          </p>
        </div>

        {/* Health Status */}
        <div className="mb-6">
          <HealthCheck />
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="flex border-b border-gray-200">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-4 font-medium text-sm border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 bg-blue-50'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Play className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {ActiveComponent && <ActiveComponent />}
          </div>
        </div>

        {/* API Info */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Code className="w-4 h-4 text-yellow-600" />
            <span className="font-semibold text-yellow-800">API Information</span>
          </div>
          <p className="text-sm text-yellow-700">
            Base URL: <code className="bg-yellow-100 px-1 rounded">https://localhost:8000</code>
          </p>
        </div>
      </div>
    </div>
  );
};