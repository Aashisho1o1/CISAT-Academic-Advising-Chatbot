import { ReactNode } from 'react';
import { Bot } from 'lucide-react';

interface ChatBubbleProps {
  children: ReactNode;
}

export function AIBubble({ children }: ChatBubbleProps) {
  return (
    <div className="mb-4 flex gap-3">
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: 'var(--gray-900)' }}
      >
        <Bot className="w-4 h-4 text-white" />
      </div>
      <div
        className="flex-1 p-4 rounded-lg"
        style={{
          backgroundColor: 'white',
          border: '1px solid var(--gray-200)',
        }}
      >
        <div style={{ color: 'var(--gray-800)' }}>{children}</div>
      </div>
    </div>
  );
}

export function UserBubble({ children }: ChatBubbleProps) {
  return (
    <div className="mb-4 flex justify-end">
      <div className="max-w-[80%] p-4 rounded-lg text-white" style={{ backgroundColor: 'var(--cgu-red)' }}>
        {children}
      </div>
    </div>
  );
}
