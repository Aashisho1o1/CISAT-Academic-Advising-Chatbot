import { ReactNode } from 'react';
import { TopNav } from './TopNav';

interface SplitLayoutProps {
  leftPanel: ReactNode;
  rightPanel: ReactNode;
}

export function SplitLayout({ leftPanel, rightPanel }: SplitLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: 'var(--gray-50)' }}>
      <TopNav />

      <main className="flex-1 flex">
        {/* 4rem = TopNav height (h-16). Update both values if nav height changes. */}
        <div
          className="w-2/5 border-r p-8 overflow-y-auto"
          style={{
            backgroundColor: 'white',
            borderColor: 'var(--gray-200)',
            minHeight: 'calc(100vh - 4rem)',
          }}
        >
          {leftPanel}
        </div>

        <div
          className="w-3/5 p-8 overflow-y-auto"
          style={{
            backgroundColor: 'var(--gray-50)',
            minHeight: 'calc(100vh - 4rem)',
          }}
        >
          <div className="max-w-2xl">{rightPanel}</div>
        </div>
      </main>
    </div>
  );
}
