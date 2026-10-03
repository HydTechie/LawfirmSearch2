export const LoadingSpinner = ({ size = 'medium', text = 'Loading...' }) => {
  const sizes = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className={`animate-spin rounded-full border-4 border-gray-300 border-t-blue-600 ${sizes[size]}`}></div>
      {text && <p className="mt-2 text-sm text-gray-600">{text}</p>}
    </div>
  );
};

export const SkeletonLoader = ({ lines = 3 }) => {
  return (
    <div className="space-y-3">
      {Array.from({ length: lines }, (_, i) => (
        <div key={i} className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          {i === lines - 1 && <div className="h-4 bg-gray-200 rounded w-3/4 mt-2"></div>}
        </div>
      ))}
    </div>
  );
};