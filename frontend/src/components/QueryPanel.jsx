import { useState } from 'react';
import { Search, Send, CheckCircle, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { useApi } from '../hooks/useApi';
import { LoadingSpinner, SkeletonLoader } from './LoadingSpinner';

export const QueryPanel = () => {
  const [formData, setFormData] = useState({
    question: '',
    collection: 'legal_docs',
    top_k: 5,
    model: 'phi3:mini',
    use_llm: true
  });

  const { loading, error, data, execute, reset } = useApi();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const payload = {
      ...formData,
      top_k: parseInt(formData.top_k)
    };

    await execute(apiService.queryDocuments, payload);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    reset();
  };

  const models = [
    { value: 'phi3:mini', label: 'Phi-3 Mini' },
    { value: 'mistral', label: 'Mistral' },
    { value: 'llama3', label: 'Llama 3' }
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center space-x-3 mb-6">
        <Search className="w-6 h-6 text-green-600" />
        <h2 className="text-xl font-semibold text-gray-900">Document Query</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Legal Question *
          </label>
          <textarea
            required
            value={formData.question}
            onChange={(e) => handleInputChange('question', e.target.value)}
            placeholder="Enter your legal question here..."
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-vertical"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Collection
            </label>
            <input
              type="text"
              value={formData.collection}
              onChange={(e) => handleInputChange('collection', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Top K Results
            </label>
            <input
              type="number"
              min="1"
              max="20"
              value={formData.top_k}
              onChange={(e) => handleInputChange('top_k', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Model
            </label>
            <select
              value={formData.model}
              onChange={(e) => handleInputChange('model', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              {models.map(model => (
                <option key={model.value} value={model.value}>
                  {model.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.use_llm}
                onChange={(e) => handleInputChange('use_llm', e.target.checked)}
                className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
              />
              <span className="text-sm font-medium text-gray-700">Use LLM</span>
            </label>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || !formData.question.trim()}
          className="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
        >
          {loading ? (
            <LoadingSpinner size="small" text="" />
          ) : (
            <Send className="w-4 h-4" />
          )}
          <span>{loading ? 'Processing Query...' : 'Send Query'}</span>
        </button>
      </form>

      {/* Results Section */}
      <div className="mt-6">
        {loading && <SkeletonLoader lines={6} />}
        
        {error && (
          <div className="flex items-center space-x-2 p-4 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <div>
              <p className="text-red-800 font-medium">Query Failed</p>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          </div>
        )}

        {data && (
          <div className="space-y-4">
            <div className="flex items-center space-x-2 p-4 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-green-800 font-medium">Query Successful</span>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <pre className="text-sm text-gray-800 whitespace-pre-wrap overflow-x-auto">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};