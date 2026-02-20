import { useNavigate } from 'react-router';
import { CheckCircle2, Download, Calendar, Mail } from 'lucide-react';
import { SplitLayout } from '../components/SplitLayout';
import { AIBubble } from '../components/ChatBubbles';
import { HITLBanner } from '../components/HITLBanner';
import { ChatbotButton } from '../components/ChatbotButton';
import { ScreenNavigator } from '../components/ScreenNavigator';

export default function Complete() {
  const navigate = useNavigate();

  const leftPanel = (
    <div>
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <CheckCircle2 className="w-8 h-8" style={{ color: 'var(--success)' }} />
          <h2 style={{ color: 'var(--gray-900)' }}>All Set!</h2>
        </div>
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          Your graduation plan has been approved by Prof. Zhang
        </p>
      </div>

      <div
        className="p-5 rounded-lg border mb-6"
        style={{
          backgroundColor: 'white',
          borderColor: 'var(--gray-200)',
        }}
      >
        <h3 className="font-semibold mb-4" style={{ color: 'var(--gray-900)' }}>
          Your Action Plan
        </h3>

        <div className="space-y-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4" style={{ color: 'var(--info)' }} />
              <span className="text-sm font-semibold" style={{ color: 'var(--gray-700)' }}>
                Fall 2025 (Current)
              </span>
            </div>
            <div className="pl-6 space-y-1 text-sm">
              <p style={{ color: 'var(--gray-600)' }}>- IST 330 - Natural Language Processing (4 units)</p>
              <p style={{ color: 'var(--gray-600)' }}>- IST 335 - Cloud Computing (4 units)</p>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4" style={{ color: 'var(--cgu-red)' }} />
              <span className="text-sm font-semibold" style={{ color: 'var(--gray-700)' }}>
                Spring 2026 (Final Term)
              </span>
            </div>
            <div className="pl-6 space-y-1 text-sm">
              <p style={{ color: 'var(--gray-900)' }}>
                <strong>- IST 340 - AI for Business (4 units)</strong>
              </p>
              <p className="text-xs" style={{ color: 'var(--gray-500)' }}>
                Registration opens November 15, 2025
              </p>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 className="w-4 h-4" style={{ color: 'var(--success)' }} />
              <span className="text-sm font-semibold" style={{ color: 'var(--gray-700)' }}>
                Graduation
              </span>
            </div>
            <div className="pl-6 text-sm" style={{ color: 'var(--gray-600)' }}>
              <p>Expected: May 2026</p>
              <p className="text-xs" style={{ color: 'var(--gray-500)' }}>
                Apply for graduation by March 1, 2026
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <button
          className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium text-white transition-all hover:opacity-90"
          style={{ backgroundColor: 'var(--cgu-red)' }}
        >
          <Download className="w-4 h-4" />
          Download Full Report (PDF)
        </button>

        <button
          className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium border transition-all hover:bg-gray-50"
          style={{ borderColor: 'var(--gray-300)', color: 'var(--gray-700)' }}
        >
          <Mail className="w-4 h-4" />
          Email Report to Myself
        </button>

        <button
          onClick={() => navigate('/')}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium border transition-all hover:bg-gray-50"
          style={{ borderColor: 'var(--gray-300)', color: 'var(--gray-700)' }}
        >
          Start New Session
        </button>
      </div>
    </div>
  );

  const rightPanel = (
    <div>
      <AIBubble>
        <div className="flex items-center gap-2 mb-2">
          <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--success)' }} />
          <strong>Your plan is approved!</strong>
        </div>
        <p>Prof. Zhang reviewed your recommendations and confirmed:</p>
        <div className="mt-3 p-3 rounded-lg" style={{ backgroundColor: 'var(--gray-50)' }}>
          <p className="text-sm" style={{ color: 'var(--gray-700)' }}>
            <em>
              "IST 340 is an excellent choice given Jordan's strong performance in data analytics courses.
              This will position them well for AI-related career opportunities."
            </em>
          </p>
          <p className="text-xs mt-2" style={{ color: 'var(--gray-500)' }}>
            - Prof. Rachel Zhang, Academic Advisor
          </p>
        </div>
      </AIBubble>

      <AIBubble>
        <p>
          <strong>What you need to do:</strong>
        </p>
        <ol className="mt-3 space-y-2">
          <li>1. Finish your current Fall 2025 courses</li>
          <li>2. Register for IST 340 when enrollment opens (Nov 15)</li>
          <li>3. Complete IST 340 in Spring 2026</li>
          <li>4. Apply for graduation by March 1, 2026</li>
        </ol>
      </AIBubble>

      <AIBubble>
        <p>
          <strong>You're on track to graduate in May 2026!</strong>
        </p>
        <p className="mt-3 text-sm" style={{ color: 'var(--gray-600)' }}>
          I've saved this action plan to your student portal. You can always come back and chat with me
          if you have questions.
        </p>
      </AIBubble>

      <AIBubble>
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          <strong>Need help?</strong> Contact Prof. Zhang at rzhang@cgu.edu or visit the CISAT advising office
          in Building 3, Room 201.
        </p>
      </AIBubble>
    </div>
  );

  return (
    <>
      <ChatbotButton />
      <ScreenNavigator />
      <HITLBanner checkpoint={3} onContinue={() => navigate('/')} continueLabel="Back to Home" />
      <SplitLayout leftPanel={leftPanel} rightPanel={rightPanel} />
    </>
  );
}
