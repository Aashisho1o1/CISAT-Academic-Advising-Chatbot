import { useNavigate } from 'react-router';
import { Sparkles } from 'lucide-react';
import { SplitLayout } from '../components/SplitLayout';
import { AIBubble } from '../components/ChatBubbles';
import { HITLBanner } from '../components/HITLBanner';
import { CourseCard } from '../components/CourseCard';
import { ChatbotButton } from '../components/ChatbotButton';
import { ScreenNavigator } from '../components/ScreenNavigator';

export default function Recommendations() {
  const navigate = useNavigate();

  const leftPanel = (
    <div>
      <div className="mb-6">
        <h2 className="mb-2" style={{ color: 'var(--gray-900)' }}>
          Course Recommendations
        </h2>
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          Curated course suggestions based on your profile
        </p>
      </div>

      <div className="space-y-3">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4" style={{ color: 'var(--cgu-red)' }} />
            <span className="text-sm font-semibold" style={{ color: 'var(--gray-700)' }}>
              Top Pick
            </span>
          </div>
          <CourseCard
            code="IST 340"
            title="Artificial Intelligence for Business"
            units={4}
            status="recommended"
            description="Good fit for a student with a strong analytics background."
          />
        </div>

        <div>
          <span className="text-sm font-semibold block mb-2" style={{ color: 'var(--gray-700)' }}>
            Alternative Options
          </span>
          <div className="space-y-2">
            <CourseCard
              code="IST 345"
              title="Blockchain & Web3"
              units={4}
              status="recommended"
              description="Emerging tech course. Aligns with your software development skills."
            />
            <CourseCard
              code="IST 350"
              title="Advanced Data Visualization"
              units={4}
              status="recommended"
              description="Builds on IST 310. Great for your portfolio."
            />
          </div>
        </div>
      </div>

      <div
        className="mt-6 p-4 rounded-lg border"
        style={{
          backgroundColor: 'var(--gray-50)',
          borderColor: 'var(--gray-200)',
        }}
      >
        <p className="text-sm font-medium mb-2" style={{ color: 'var(--gray-900)' }}>
          Why IST 340?
        </p>
        <ul className="text-sm space-y-1" style={{ color: 'var(--gray-600)' }}>
          <li>- Complements your NLP course (IST 330)</li>
          <li>- Builds on recent analytics coursework</li>
          <li>- Useful for a technology-focused portfolio</li>
          <li>- Reasonable elective fit for the sample student</li>
          <li>- Easy to compare with alternative options</li>
        </ul>
      </div>
    </div>
  );

  const rightPanel = (
    <div>
      <AIBubble>
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="w-5 h-5" style={{ color: 'var(--cgu-red)' }} />
          <strong>Here are my recommendations!</strong>
        </div>
        <p>
          Based on your course history and current enrollments, I've identified <strong>3 elective
          courses</strong> that would complete your degree requirements.
        </p>
      </AIBubble>

      <AIBubble>
        <p>
          <strong>My top recommendation is IST 340 (AI for Business)</strong> because:
        </p>
        <ul className="mt-2 space-y-1 text-sm">
          <li>- Pairs perfectly with your current NLP course</li>
          <li>- You earned an A in Data Analytics (IST 310)</li>
          <li>- It is a strong thematic fit for the sample student</li>
          <li>- It keeps the recommendation set easy to explain</li>
        </ul>
      </AIBubble>

      <AIBubble>
        <p>
          I've also included 2 alternative options in case IST 340 doesn't fit your schedule or
          interests.
        </p>
        <p className="mt-3">
          <strong>All 3 courses meet your elective requirement</strong> and would bring you to exactly 36
          units.
        </p>
      </AIBubble>

      <AIBubble>
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          <strong>Next:</strong> In a future version, these recommendations could be sent to an advisor for review.
        </p>
      </AIBubble>
    </div>
  );

  return (
    <>
      <ChatbotButton />
      <ScreenNavigator />
      <HITLBanner checkpoint={2} onContinue={() => navigate('/advisor-confirmation')} />
      <SplitLayout leftPanel={leftPanel} rightPanel={rightPanel} />
    </>
  );
}
