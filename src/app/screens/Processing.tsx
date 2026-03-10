import { useNavigate } from 'react-router';
import { useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { TopNav } from '../components/TopNav';
import { ChatbotButton } from '../components/ChatbotButton';
import { ScreenNavigator } from '../components/ScreenNavigator';

export default function Processing() {
  const navigate = useNavigate();

  // TODO: Replace this timer with a real API call once the backend is connected.
  // The timer should be removed and replaced with something like:
  //   api.processDocument(file).then(() => navigate('/course-history'));
  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/course-history');
    }, 3000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: 'var(--gray-50)' }}>
      <ChatbotButton />
      <ScreenNavigator />
      <TopNav />

      <main className="flex-1 flex items-center justify-center p-8">
        <div className="max-w-md w-full text-center">
          <div className="mb-6 flex justify-center">
            <Loader2 className="w-16 h-16 animate-spin" style={{ color: 'var(--cgu-red)' }} />
          </div>

          <h2 className="mb-3" style={{ color: 'var(--gray-900)' }}>
            Previewing the Analysis Step...
          </h2>

          <p style={{ color: 'var(--gray-600)' }}>
            This screen simulates the next step in the demo workflow while the live chat assistant stays available.
          </p>

          <div className="mt-8 space-y-3">
            <div
              className="p-3 rounded-lg border text-left flex items-center gap-3"
              style={{
                backgroundColor: 'white',
                borderColor: 'var(--gray-200)',
              }}
            >
              <div className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: 'var(--success)' }} />
              <span className="text-sm" style={{ color: 'var(--gray-700)' }}>
                Extracting course codes and titles...
              </span>
            </div>

            <div
              className="p-3 rounded-lg border text-left flex items-center gap-3"
              style={{
                backgroundColor: 'white',
                borderColor: 'var(--gray-200)',
              }}
            >
              <div className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: 'var(--info)' }} />
              <span className="text-sm" style={{ color: 'var(--gray-700)' }}>
                Calculating total units completed...
              </span>
            </div>

            <div
              className="p-3 rounded-lg border text-left flex items-center gap-3"
              style={{
                backgroundColor: 'white',
                borderColor: 'var(--gray-200)',
              }}
            >
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: 'var(--gray-300)' }} />
              <span className="text-sm" style={{ color: 'var(--gray-500)' }}>
                Comparing with CISAT requirements...
              </span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
