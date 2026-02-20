import { useNavigate } from 'react-router';
import { Bot, Sparkles, CheckCircle2 } from 'lucide-react';
import { TopNav } from '../components/TopNav';
import { ChatbotButton } from '../components/ChatbotButton';
import { ScreenNavigator } from '../components/ScreenNavigator';

export default function Welcome() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: 'var(--gray-50)' }}>
      <ChatbotButton />
      <ScreenNavigator />
      <TopNav showNavigation={false} />

      <main className="flex-1 flex items-center justify-center p-8">
        <div className="max-w-2xl w-full text-center">
          <div className="mb-8 flex justify-center">
            <div
              className="w-20 h-20 rounded-2xl flex items-center justify-center"
              style={{ backgroundColor: 'var(--cgu-red)' }}
            >
              <Bot className="w-10 h-10 text-white" />
            </div>
          </div>

          <h1 className="mb-4" style={{ color: 'var(--gray-900)' }}>
            <span style={{ fontSize: '1.12em' }}>CISAT</span> Academic Advising Chatbot
          </h1>

          <p className="text-lg mb-8" style={{ color: 'var(--gray-600)' }}>
            Your AI-powered graduation planning companion for the CISAT MS program
          </p>

          <div className="grid gap-4 mb-10 text-left">
            <div
              className="p-4 rounded-lg border flex items-start gap-3"
              style={{
                backgroundColor: 'white',
                borderColor: 'var(--gray-200)',
              }}
            >
              <Sparkles className="w-5 h-5 mt-0.5" style={{ color: 'var(--cgu-red)' }} />
              <div>
                <h3 className="font-semibold mb-1" style={{ color: 'var(--gray-900)', fontSize: '1rem' }}>
                  Smart Graduation Progress Assistance
                </h3>
                <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
                  Upload your planning sheet and I'll analyze your progress toward graduation
                </p>
              </div>
            </div>

            <div
              className="p-4 rounded-lg border flex items-start gap-3"
              style={{
                backgroundColor: 'white',
                borderColor: 'var(--gray-200)',
              }}
            >
              <CheckCircle2 className="w-5 h-5 mt-0.5" style={{ color: 'var(--cgu-red)' }} />
              <div>
                <h3 className="font-semibold mb-1" style={{ color: 'var(--gray-900)', fontSize: '1rem' }}>
                  Personalized Recommendations
                </h3>
                <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
                  Get AI-powered course suggestions tailored to your academic goals
                </p>
              </div>
            </div>

            <div
              className="p-4 rounded-lg border flex items-start gap-3"
              style={{
                backgroundColor: 'white',
                borderColor: 'var(--gray-200)',
              }}
            >
              <Bot className="w-5 h-5 mt-0.5" style={{ color: 'var(--cgu-red)' }} />
              <div>
                <h3 className="font-semibold mb-1" style={{ color: 'var(--gray-900)', fontSize: '1rem' }}>
                  Faculty Oversight
                </h3>
                <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
                  All recommendations are reviewed and confirmed by your advisor
                </p>
              </div>
            </div>
          </div>

          <button
            onClick={() => navigate('/upload')}
            className="w-full px-8 py-4 rounded-lg font-semibold text-white text-lg transition-all hover:opacity-90"
            style={{ backgroundColor: 'var(--cgu-red)' }}
          >
            Get Started with SSO Login
          </button>

          <p className="mt-4 text-sm" style={{ color: 'var(--gray-500)' }}>
            Sign in with your CISAT credentials to continue
          </p>
        </div>
      </main>
    </div>
  );
}
