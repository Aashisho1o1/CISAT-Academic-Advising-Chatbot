import { Shield, ChevronRight } from 'lucide-react';

interface HITLBannerProps {
  // Literal union instead of `number` so TypeScript rejects checkpoint={0} or
  // checkpoint={99} at call sites — the switch only handles 1, 2, and 3.
  checkpoint: 1 | 2 | 3;
  onContinue: () => void;
  continueLabel?: string;
}

export function HITLBanner({ checkpoint, onContinue, continueLabel = 'Looks Good - Continue' }: HITLBannerProps) {
  const getCheckpointText = () => {
    switch (checkpoint) {
      case 1:
        return 'Please verify your course history is accurate before continuing.';
      case 2:
        return 'Review these recommendations before the future advisor-review step.';
      case 3:
        return 'This flow illustrates what a final reviewed plan could look like.';
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
