import { ReactNode } from 'react';

interface QuickReplyChipProps {
  children: ReactNode;
  onClick?: () => void;
}

export function QuickReplyChip({ children, onClick }: QuickReplyChipProps) {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 rounded-full text-sm font-medium border transition-all hover:bg-gray-50"
      style={{
        borderColor: 'var(--gray-300)',
        color: 'var(--gray-700)',
        backgroundColor: 'white',
      }}
    >
      {children}
    </button>
  );
}
