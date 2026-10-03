import { useState } from 'react';
import { Upload, FolderOpen, CheckCircle, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { useApi } from '../hooks/useApi';
import { LoadingSpinner, SkeletonLoader } from './LoadingSpinner';

export const IngestPanel = () => {
  const [formData, setFormData] = useState({
    directory: '',
    collection: 'legal_docs',
    chunk_size: 900,
    overlap: 150,
    metadata: ''
  });

  const { loading, error, data, execute, reset } = useApi();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const payload = {
      ...formData,
      chunk_size: parseInt(formData.chunk_size),
      overlap: parseInt(formData.overlap),
      metadata: formData.metadata ? JSON.parse(formData.metadata) : null
    };

    await execute(apiService.ingestDocuments, payload);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    reset();
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center space-x-3 mb-6">
        <Upload className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-semibold text-gray-900">Document Ingest</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Directory Path *
          </label>
          <div className="relative">
            <FolderOpen className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              required
              value={formData.directory}
              onChange={(e) => handleInputChange('directory', e.target.value)}
              placeholder="/path/to/legal/documents"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Collection Name
            </label>
            <input
              type="text"
              value={formData.collection}
              onChange={(e) => handleInputChange('collection', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chunk Size
            </label>
            <input
              type="number"
              min="100"
              max="2000"
              value={formData.chunk_size}
              onChange={(e) => handleInputChange('chunk_size', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Overlap
            </label>
            <input
              type="number"
              min="0"
              max="500"
              value={formData.overlap}
              onChange={(e) => handleInputChange('overlap', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Metadata (JSON)
          </label>
          <textarea
            value={formData.metadata}
            onChange={(e) => handleInputChange('metadata', e.target.value)}
            placeholder='{"key": "value"}'
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Ingesting Documents...' : 'Start Ingestion'}
        </button>
      </form>

      {/* Results Section */}
      <div className="mt-6">
        {loading && <SkeletonLoader lines={4} />}
        
        {error && (
          <div className="flex items-center space-x-2 p-4 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <div>
              <p className="text-red-800 font-medium">Ingestion Failed</p>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          </div>
        )}

        {data && (
          <div className="flex items-center space-x-2 p-4 bg-green-50 border border-green-200 rounded-lg">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <div>
              <p className="text-green-800 font-medium">Ingestion Successful</p>
              <pre className="text-green-600 text-sm mt-1 whitespace-pre-wrap">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};