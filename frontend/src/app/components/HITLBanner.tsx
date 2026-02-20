import { Shield, ChevronRight } from 'lucide-react';

interface HITLBannerProps {
  checkpoint: number;
  onContinue: () => void;
  continueLabel?: string;
}

export function HITLBanner({ checkpoint, onContinue, continueLabel = 'Looks Good - Continue' }: HITLBannerProps) {
  const getCheckpointText = () => {
    switch (checkpoint) {
      case 1:
        return 'Please verify your course history is accurate before continuing.';
      case 2:
        return 'Review the course recommendations before sending to your advisor.';
      case 3:
        return 'Your graduation plan is complete and advisor-approved.';
      default:
        return 'Please review before continuing.';
    }
  };

  return (
    <div
      className="border-b px-8 py-4 flex items-center justify-between"
      style={{
        backgroundColor: 'var(--gray-50)',
        borderColor: 'var(--gray-200)',
      }}
    >
      <div className="flex items-center gap-3">
        <Shield className="w-5 h-5" style={{ color: 'var(--cgu-red)' }} />
        <div>
          <p className="font-semibold text-sm" style={{ color: 'var(--gray-900)' }}>
            Human-in-the-Loop Checkpoint {checkpoint}/3
          </p>
          <p className="text-xs" style={{ color: 'var(--gray-600)' }}>
            {getCheckpointText()}
          </p>
        </div>
      </div>

      <button
        onClick={onContinue}
        className="flex items-center gap-2 px-5 py-2 rounded-lg font-medium text-sm text-white transition-all hover:opacity-90"
        style={{ backgroundColor: 'var(--cgu-red)' }}
      >
        {continueLabel}
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
}
