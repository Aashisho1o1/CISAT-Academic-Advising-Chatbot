import { useState, useRef, useEffect } from 'react';
import { X, Send, Loader2 } from 'lucide-react';
import { AIBubble, UserBubble } from './ChatBubbles';
import { API_URL } from '@/config';
import { useAdvisingStore } from '../store';
import { useNavigate } from 'react-router';

const INITIAL_ASSISTANT_MESSAGE =
  'Hi! I\'m the CISAT advising chat assistant. Ask me about deadlines, requirements, or next steps in the program.';
const MAX_MESSAGE_LENGTH = 4000;
const REQUEST_HISTORY_LIMIT = 6;

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
    { role: 'assistant', content: INITIAL_ASSISTANT_MESSAGE },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  
  const { threadId, fileId, setExtractedData } = useAdvisingStore();
  const navigate = useNavigate();

  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [messages]);

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
    const history = messages.slice(1).slice(-REQUEST_HISTORY_LIMIT);
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      if (!threadId) {
         setMessages(prev => [...prev, { role: 'assistant', content: 'No active session found. Please upload a plan first to start a thread.' }]);
         setLoading(false);
         return;
      }

      // We only attach the fileId on the very first message sent by the user to attach it to the thread.
      const isFirstUserMessage = messages.filter(m => m.role === 'user').length === 0;
      
      const payload = { 
        thread_id: threadId, 
        message: trimmed,
        file_ids: fileId && isFirstUserMessage ? [fileId] : [],
      };

      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        if (res.status === 429) throw new Error('Too many requests');
        if (res.status === 503) throw new Error('Service unavailable');
        throw new Error(`Server error: ${res.status}`);
      }
      
      // The new response schema can give `reply` OR `tool_call`
      const data: { reply?: string; tool_call?: { name: string; args: any } } = await res.json();
      
      if (data.tool_call) {
        // Handle Assistant's function call to frontend
        if (data.tool_call.name === 'trigger_ui_navigation') {
          const { target_route, extracted_data } = data.tool_call.args;
          if (extracted_data) {
             setExtractedData(extracted_data);
          }
          
          let routePath = `/${target_route.toLowerCase()}`;
          // Map backend enum string roughly to react-router typical pathing
          if (target_route === 'GapAnalysis') routePath = '/gap-analysis';
          if (target_route === 'Recommendations') routePath = '/recommendations';
          if (target_route === 'CourseHistory') routePath = '/course-history';
          if (target_route === 'AdvisorConfirmation') routePath = '/advisor-confirmation';
          
          navigate(routePath);
          setMessages(prev => [...prev, { role: 'assistant', content: `Ok! I've navigated you to the ${target_route} screen based on your request.` }]);
        } else {
           setMessages(prev => [...prev, { role: 'assistant', content: `[Executed internal tool: ${data.tool_call.name}]` }]);
        }
      } else if (data.reply) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
      } else {
        throw new Error('Invalid response - neither reply nor tool_call was found.');
      }
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
    } finally {
      setLoading(false);
    }
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
