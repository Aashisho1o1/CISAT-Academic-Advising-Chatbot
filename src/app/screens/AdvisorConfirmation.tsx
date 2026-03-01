import { useNavigate } from 'react-router';
import { Mail, CheckCircle2, Clock } from 'lucide-react';
import { SplitLayout } from '../components/SplitLayout';
import { AIBubble } from '../components/ChatBubbles';
import { ChatbotButton } from '../components/ChatbotButton';
import { ScreenNavigator } from '../components/ScreenNavigator';

export default function AdvisorConfirmation() {
  const navigate = useNavigate();

  const leftPanel = (
    <div>
      <div className="mb-6">
        <h2 className="mb-2" style={{ color: 'var(--gray-900)' }}>
          Advisor Confirmation
        </h2>
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          Your recommendations are being reviewed by faculty
        </p>
      </div>

      <div
        className="p-5 rounded-lg border mb-6"
        style={{
          backgroundColor: 'white',
          borderColor: 'var(--gray-200)',
        }}
      >
        <div className="flex items-start gap-3 mb-4">
          <Mail className="w-5 h-5 mt-0.5" style={{ color: 'var(--cgu-red)' }} />
          <div className="flex-1">
            <h3 className="font-semibold mb-1" style={{ color: 'var(--gray-900)' }}>
              Email Sent to Advisor
            </h3>
            <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
              Your Program Advisor
            </p>
          </div>
        </div>

        <div
          className="p-4 rounded text-sm space-y-3"
          style={{
            backgroundColor: 'var(--gray-50)',
            fontFamily: 'monospace',
          }}
        >
          <p style={{ color: 'var(--gray-700)' }}>
            <strong>Subject:</strong> Course Recommendation Approval Needed - [Student Name]
          </p>
          <div style={{ color: 'var(--gray-600)' }}>
            <p className="mb-2">Hi [Advisor Name],</p>
            <p className="mb-2">
              The CISAT Advising Assistant has generated course recommendations for [Student Name] (MS
              CISAT).
            </p>
            <p className="mb-2">
              <strong>Student Status:</strong>
              <br />- 32/36 units completed (89%)
              <br />- Needs: 1 elective course (4 units)
            </p>
            <p className="mb-2">
              <strong>Top Recommendation:</strong>
              <br />IST 340 - Artificial Intelligence for Business
            </p>
            <p>Please review and approve at: [approval link]</p>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--success)' }} />
          <div>
            <p className="text-sm font-medium" style={{ color: 'var(--gray-900)' }}>
              Analysis Complete
            </p>
            <p className="text-xs" style={{ color: 'var(--gray-500)' }}>
              2 minutes ago
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--success)' }} />
          <div>
            <p className="text-sm font-medium" style={{ color: 'var(--gray-900)' }}>
              Email Sent to Advisor
            </p>
            <p className="text-xs" style={{ color: 'var(--gray-500)' }}>
              Just now
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Clock className="w-5 h-5" style={{ color: 'var(--gray-400)' }} />
          <div>
            <p className="text-sm font-medium" style={{ color: 'var(--gray-600)' }}>
              Awaiting Advisor Approval
            </p>
            <p className="text-xs" style={{ color: 'var(--gray-500)' }}>
              Usually within 24-48 hours
            </p>
          </div>
        </div>
      </div>

      {import.meta.env.DEV && (
        <button
          onClick={() => navigate('/complete')}
          className="w-full mt-6 px-6 py-3 rounded-lg font-medium text-white transition-all hover:opacity-90"
          style={{ backgroundColor: 'var(--cgu-red)' }}
        >
          Simulate Advisor Approval (Demo)
        </button>
      )}
    </div>
  );

  const rightPanel = (
    <div>
      <AIBubble>
        <div className="flex items-center gap-2 mb-2">
          <Mail className="w-5 h-5" style={{ color: 'var(--cgu-red)' }} />
          <strong>Sent to your advisor!</strong>
        </div>
        <p>I've emailed <strong>your advisor</strong> with:</p>
        <ul className="mt-3 space-y-1">
          <li>- Your complete course history</li>
          <li>- Gap analysis results</li>
          <li>- My course recommendations</li>
          <li>- Reasoning for each suggestion</li>
        </ul>
      </AIBubble>

      <AIBubble>
        <p>
          <strong>What happens next?</strong>
        </p>
        <ol className="mt-3 space-y-2 text-sm">
          <li>1. Prof. Zhang reviews the recommendations</li>
          <li>2. She can approve, modify, or request changes</li>
          <li>3. You'll get an email when she responds</li>
          <li>4. We'll create your final action plan</li>
        </ol>
      </AIBubble>

      <AIBubble>
        <p>
          This usually takes <strong>24-48 hours</strong>. You'll receive an email notification
          when your advisor responds.
        </p>
        <p className="mt-3 text-sm" style={{ color: 'var(--gray-600)' }}>
          <em>(For this demo, click "Simulate Advisor Approval" to continue)</em>
        </p>
      </AIBubble>
    </div>
  );

  return (
    <>
      <ChatbotButton />
      <ScreenNavigator />
      <SplitLayout leftPanel={leftPanel} rightPanel={rightPanel} />
    </>
  );
}
