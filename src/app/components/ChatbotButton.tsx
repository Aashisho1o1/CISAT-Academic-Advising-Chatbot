import { useState } from 'react';
import { MessageCircle, X } from 'lucide-react';
import { ChatPanel } from './ChatPanel';

export function ChatbotButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <ChatPanel isOpen={isOpen} onClose={() => setIsOpen(false)} />
      <button
        onClick={() => setIsOpen(prev => !prev)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all hover:scale-110 z-50"
        style={{ backgroundColor: 'var(--cgu-red)', color: 'white' }}
        title="Ask CISAT Advisor"
      >
        {isOpen ? <X className="w-6 h-6" /> : <MessageCircle className="w-6 h-6" />}
      </button>
    </>
  );
}
