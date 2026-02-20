import { useNavigate, useLocation } from 'react-router';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export function ScreenNavigator() {
  const navigate = useNavigate();
  const location = useLocation();

  const screens = [
    { path: '/', label: 'Welcome' },
    { path: '/upload', label: 'Upload' },
    { path: '/processing', label: 'Processing' },
    { path: '/course-history', label: 'Course History' },
    { path: '/gap-analysis', label: 'Gap Analysis' },
    { path: '/recommendations', label: 'Recommendations' },
    { path: '/advisor-confirmation', label: 'Advisor Confirmation' },
    { path: '/complete', label: 'Complete' },
  ];

  const currentIndex = screens.findIndex((screen) => screen.path === location.pathname);
  const hasPrevious = currentIndex > 0;
  const hasNext = currentIndex < screens.length - 1 && currentIndex !== -1;

  const handlePrevious = () => {
    if (hasPrevious) {
      navigate(screens[currentIndex - 1].path);
    }
  };

  const handleNext = () => {
    if (hasNext) {
      navigate(screens[currentIndex + 1].path);
    }
  };

  if (currentIndex === -1) return null;

  return (
    <div
      className="fixed top-20 right-6 flex items-center gap-2 px-3 py-2 rounded-lg shadow-lg z-50"
      style={{
        backgroundColor: 'white',
        border: '1px solid var(--gray-200)',
      }}
    >
      <button
        onClick={handlePrevious}
        disabled={!hasPrevious}
        className="p-1 rounded transition-colors disabled:opacity-30"
        style={{
          color: hasPrevious ? 'var(--gray-700)' : 'var(--gray-400)',
          cursor: hasPrevious ? 'pointer' : 'not-allowed',
        }}
        title="Previous screen"
      >
        <ChevronLeft className="w-5 h-5" />
      </button>

      <span className="text-sm font-medium px-2" style={{ color: 'var(--gray-900)' }}>
        {currentIndex + 1} / {screens.length}
      </span>

      <button
        onClick={handleNext}
        disabled={!hasNext}
        className="p-1 rounded transition-colors disabled:opacity-30"
        style={{
          color: hasNext ? 'var(--gray-700)' : 'var(--gray-400)',
          cursor: hasNext ? 'pointer' : 'not-allowed',
        }}
        title="Next screen"
      >
        <ChevronRight className="w-5 h-5" />
      </button>
    </div>
  );
}
