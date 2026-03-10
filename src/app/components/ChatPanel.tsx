import { useState, useRef, useEffect } from 'react';
import { X, Send, Loader2 } from 'lucide-react';
import { AIBubble, UserBubble } from './ChatBubbles';
import { API_URL } from '@/config';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ChatPanel({ isOpen, onClose }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hi! I\'m the CISAT advising chat assistant. Ask me about deadlines, requirements, or next steps in the program.' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [messages]);

  const MAX_MESSAGE_LENGTH = 4000;

  const sendMessage = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    if (trimmed.length > MAX_MESSAGE_LENGTH) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: `Message too long (${trimmed.length} chars). Please keep it under ${MAX_MESSAGE_LENGTH} characters.` },
      ]);
      return;
    }

    const userMsg: Message = { role: 'user', content: trimmed };
    const history = messages;
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed, history }),
      });
      if (!res.ok) {
        if (res.status === 429) throw new Error('Too many requests');
        if (res.status === 503) throw new Error('Service unavailable');
        throw new Error(`Server error: ${res.status}`);
      }
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
    } catch (error) {
      const reply =
        error instanceof Error && error.message === 'Too many requests'
          ? 'You have hit the chat rate limit. Please wait a minute and try again.'
          : error instanceof Error && error.message === 'Service unavailable'
            ? 'The advising chat is not configured yet. Check the backend environment settings.'
            : 'Sorry, I couldn\'t connect to the advising server. Make sure the backend is running.';
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: reply },
      ]);
    }
    setLoading(false);
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed bottom-24 right-4 w-[calc(100vw-2rem)] sm:w-96 sm:right-6 rounded-xl shadow-2xl flex flex-col z-50 overflow-hidden"
      style={{ height: '500px', border: '1px solid var(--gray-200)' }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3 flex-shrink-0"
        style={{ backgroundColor: 'var(--cgu-red)', color: 'white' }}
      >
        <span className="font-semibold text-sm">CISAT Advising Chat</span>
        <button onClick={onClose} className="hover:opacity-75 transition-opacity">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Messages */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4"
        style={{ backgroundColor: 'var(--gray-50)' }}
      >
        {messages.map((msg, i) =>
          msg.role === 'assistant' ? (
            <AIBubble key={i}>{msg.content}</AIBubble>
          ) : (
            <UserBubble key={i}>{msg.content}</UserBubble>
          )
        )}
        {loading && (
          <div className="flex gap-3 mb-4">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: 'var(--gray-900)' }}
            >
              <Loader2 className="w-4 h-4 text-white animate-spin" />
            </div>
            <div
              className="px-4 py-3 rounded-lg text-sm"
              style={{ backgroundColor: 'white', border: '1px solid var(--gray-200)', color: 'var(--gray-500)' }}
            >
              Thinking...
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div
        className="flex gap-2 p-3 flex-shrink-0"
        style={{ borderTop: '1px solid var(--gray-200)', backgroundColor: 'white' }}
      >
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about deadlines, requirements..."
          maxLength={MAX_MESSAGE_LENGTH}
          className="flex-1 text-sm px-3 py-2 rounded-lg outline-none"
          style={{ border: '1px solid var(--gray-300)', color: 'var(--gray-800)' }}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 transition-opacity disabled:opacity-40"
          style={{ backgroundColor: 'var(--cgu-red)', color: 'white' }}
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
