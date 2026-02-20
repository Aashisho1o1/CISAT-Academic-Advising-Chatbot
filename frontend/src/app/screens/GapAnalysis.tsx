import { useNavigate } from 'react-router';
import { CheckCircle2, AlertTriangle, ChevronRight } from 'lucide-react';
import { SplitLayout } from '../components/SplitLayout';
import { AIBubble } from '../components/ChatBubbles';
import { Progress } from '../components/ui/progress';
import { ChatbotButton } from '../components/ChatbotButton';
import { ScreenNavigator } from '../components/ScreenNavigator';

export default function GapAnalysis() {
  const navigate = useNavigate();

  const leftPanel = (
    <div>
      <div className="mb-6">
        <h2 className="mb-2" style={{ color: 'var(--gray-900)' }}>
          Gap Analysis
        </h2>
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          Here's what you need to complete your CISAT MS degree
        </p>
      </div>

      <div
        className="p-5 mb-6 rounded-lg border"
        style={{
          borderColor: 'var(--gray-200)',
          backgroundColor: 'white',
        }}
      >
        <div className="flex items-center justify-between mb-3">
          <span className="font-semibold" style={{ color: 'var(--gray-900)' }}>
            Overall Progress
          </span>
          <span className="font-bold text-lg" style={{ color: 'var(--gray-900)' }}>
            89%
          </span>
        </div>
        <Progress value={89} className="h-3 mb-2" />
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          32 of 36 units completed
        </p>
      </div>

      <div className="space-y-3">
        <h3 className="font-semibold mb-3" style={{ color: 'var(--gray-900)', fontSize: '1rem' }}>
          Requirements Status
        </h3>

        <div
          className="p-4 rounded-lg border"
          style={{
            backgroundColor: 'var(--gray-50)',
            borderColor: 'var(--gray-200)',
          }}
        >
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 mt-0.5 flex-shrink-0" style={{ color: 'var(--success)' }} />
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium" style={{ color: 'var(--gray-900)' }}>
                  Core Requirements
                </span>
                <span className="text-sm font-semibold" style={{ color: 'var(--success)' }}>
                  Complete
                </span>
              </div>
              <p className="text-sm mb-2" style={{ color: 'var(--gray-600)' }}>
                24 of 24 units
              </p>
              <Progress value={100} className="h-1.5" />
            </div>
          </div>
        </div>

        <div
          className="p-4 rounded-lg border"
          style={{
            backgroundColor: 'white',
            borderColor: 'var(--warning)',
          }}
        >
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 mt-0.5 flex-shrink-0" style={{ color: 'var(--warning)' }} />
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium" style={{ color: 'var(--gray-900)' }}>
                  Elective Requirements
                </span>
                <span className="text-sm font-semibold" style={{ color: 'var(--warning)' }}>
                  Incomplete
                </span>
              </div>
              <p className="text-sm mb-2" style={{ color: 'var(--gray-600)' }}>
                8 of 12 units (need 1 more course)
              </p>
              <Progress value={67} className="h-1.5" />
            </div>
          </div>
        </div>

        <div
          className="p-4 rounded-lg border"
          style={{
            backgroundColor: 'var(--gray-50)',
            borderColor: 'var(--gray-200)',
          }}
        >
          <div className="flex items-start gap-3">
            <div className="w-5 h-5 rounded-full border-2 mt-0.5 flex-shrink-0" style={{ borderColor: 'var(--gray-300)' }} />
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium" style={{ color: 'var(--gray-900)' }}>
                  Capstone Project
                </span>
                <span className="text-sm" style={{ color: 'var(--gray-500)' }}>
                  Not Required Yet
                </span>
              </div>
              <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
                Complete after finishing all coursework
              </p>
            </div>
          </div>
        </div>
      </div>

      <button
        onClick={() => navigate('/recommendations')}
        className="w-full mt-6 flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium text-white transition-all hover:opacity-90"
        style={{ backgroundColor: 'var(--cgu-red)' }}
      >
        View Recommendations
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );

  const rightPanel = (
    <div>
      <AIBubble>
        <div className="flex items-center gap-2 mb-2">
          <AlertTriangle className="w-5 h-5" style={{ color: 'var(--warning)' }} />
          <strong>You're almost there!</strong>
        </div>
        <p>
          You've completed <strong>89% of your degree</strong>. Here's what's left:
        </p>
        <div className="mt-4 p-3 rounded-lg" style={{ backgroundColor: 'var(--gray-50)' }}>
          <p className="font-medium mb-2" style={{ color: 'var(--gray-900)' }}>
            Missing Requirements:
          </p>
          <ul className="space-y-1 text-sm">
            <li>- <strong>1 more elective</strong> (4 units)</li>
          </ul>
        </div>
      </AIBubble>

      <AIBubble>
        <p>
          <strong>Good news:</strong> You're currently enrolled in 2 courses (IST 330 and IST 335) that will
          give you 8 units when completed.
        </p>
        <p className="mt-3">
          After those finish, you'll just need <strong>1 more elective course</strong> to reach the 36-unit
          requirement.
        </p>
      </AIBubble>

      <AIBubble>
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          <strong>Next:</strong> I'll recommend specific courses that fit your schedule and interests.
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
