import { ChevronLeft, ChevronRight, Home } from 'lucide-react';
import { useNavigate } from 'react-router';

interface WorkflowControlsProps {
  onPrevious?: () => void;
  onNext?: () => void;
  nextLabel?: string;
  showHome?: boolean;
}

export function WorkflowControls({ onPrevious, onNext, nextLabel = 'Next', showHome = false }: WorkflowControlsProps) {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-between gap-4">
      {onPrevious ? (
        <button
          onClick={onPrevious}
          className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium border transition-all hover:bg-gray-50"
          style={{ borderColor: 'var(--gray-300)', color: 'var(--gray-700)' }}
        >
          <ChevronLeft className="w-4 h-4" />
          Previous
        </button>
      ) : showHome ? (
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium border transition-all hover:bg-gray-50"
          style={{ borderColor: 'var(--gray-300)', color: 'var(--gray-700)' }}
        >
          <Home className="w-4 h-4" />
          Home
        </button>
      ) : (
        <div />
      )}

      {onNext && (
        <button
          onClick={onNext}
          className="flex items-center gap-2 px-6 py-2 rounded-lg font-medium text-white transition-all hover:opacity-90"
          style={{ backgroundColor: 'var(--cgu-red)' }}
        >
          {nextLabel}
          <ChevronRight className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
