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
          <h2 style={{ color: 'var(--gray-900)' }}>Demo Complete State</h2>
        </div>
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          This is an example of the final approved-plan screen.
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
          Example Action Plan
        </h3>

        <div className="space-y-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Calendar className="w-4 h-4" style={{ color: 'var(--info)' }} />
              <span className="text-sm font-semibold" style={{ color: 'var(--gray-700)' }}>
                Current Term
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
                Next Term
              </span>
            </div>
            <div className="pl-6 space-y-1 text-sm">
              <p style={{ color: 'var(--gray-900)' }}>
                <strong>- IST 340 - AI for Business (4 units)</strong>
              </p>
              <p className="text-xs" style={{ color: 'var(--gray-500)' }}>
                Check the live academic calendar before registering
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
              <p>Expected: after the final elective is complete</p>
              <p className="text-xs" style={{ color: 'var(--gray-500)' }}>
                Confirm the official graduation deadline with CGU
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
          Download Demo Report
        </button>

        <button
          className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium border transition-all hover:bg-gray-50"
          style={{ borderColor: 'var(--gray-300)', color: 'var(--gray-700)' }}
        >
          <Mail className="w-4 h-4" />
          Email Demo Report
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
          <strong>Example approved-plan view</strong>
        </div>
        <p>Here is a sample advisor note for the demo flow:</p>
        <div className="mt-3 p-3 rounded-lg" style={{ backgroundColor: 'var(--gray-50)' }}>
          <p className="text-sm" style={{ color: 'var(--gray-700)' }}>
            <em>
              "IST 340 is a reasonable example recommendation for a student with strong analytics coursework."
            </em>
          </p>
          <p className="text-xs mt-2" style={{ color: 'var(--gray-500)' }}>
            - Sample advisor feedback
          </p>
        </div>
      </AIBubble>

      <AIBubble>
        <p>
          <strong>What you need to do:</strong>
        </p>
        <ol className="mt-3 space-y-2">
          <li>1. Finish the current courses</li>
          <li>2. Check the academic calendar before registration opens</li>
          <li>3. Complete the final elective</li>
          <li>4. Confirm graduation deadlines with the program team</li>
        </ol>
      </AIBubble>

      <AIBubble>
        <p>
          <strong>This is a demo summary, not a saved student record.</strong>
        </p>
        <p className="mt-3 text-sm" style={{ color: 'var(--gray-600)' }}>
          The current MVP does not save plans to a portal yet. The live backend feature today is the chat assistant.
        </p>
      </AIBubble>

      <AIBubble>
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          <strong>Need help?</strong> Use the chat assistant for general questions and verify official deadlines with CGU.
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
