import { useNavigate } from 'react-router';
import { useState } from 'react';
import { CheckCircle2, Edit } from 'lucide-react';
import { SplitLayout } from '../components/SplitLayout';
import { AIBubble } from '../components/ChatBubbles';
import { CourseCard } from '../components/CourseCard';
import { HITLBanner } from '../components/HITLBanner';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Progress } from '../components/ui/progress';
import { ChatbotButton } from '../components/ChatbotButton';
import { ScreenNavigator } from '../components/ScreenNavigator';

export default function CourseHistory() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('completed');

  const leftPanel = (
    <div>
      <div className="mb-6">
        <h2 className="mb-2" style={{ color: 'var(--gray-900)' }}>
          Your Course History
        </h2>
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          Review the courses I found. Make edits if anything looks wrong.
        </p>
      </div>

      <div
        className="p-4 mb-6 rounded-lg border"
        style={{
          borderColor: 'var(--gray-200)',
          backgroundColor: 'var(--gray-50)',
        }}
      >
        <div className="flex items-center justify-between mb-2">
          <span className="font-medium" style={{ color: 'var(--gray-900)' }}>
            Progress Toward Degree
          </span>
          <span className="font-bold" style={{ color: 'var(--gray-900)' }}>
            32 / 36 units
          </span>
        </div>
        <Progress value={89} className="h-2" />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="w-full mb-4">
          <TabsTrigger value="completed" className="flex-1">
            Completed (8)
          </TabsTrigger>
          <TabsTrigger value="in-progress" className="flex-1">
            In Progress (2)
          </TabsTrigger>
          <TabsTrigger value="waived" className="flex-1">
            Waived (1)
          </TabsTrigger>
        </TabsList>

        <TabsContent value="completed" className="space-y-2">
          <CourseCard code="IST 302" title="Databases" units={4} status="completed" grade="A" />
          <CourseCard code="IST 303" title="Software Development" units={4} status="completed" grade="A-" />
          <CourseCard
            code="IST 304"
            title="Communications & Networking"
            units={4}
            status="completed"
            grade="B+"
          />
          <CourseCard
            code="IST 305"
            title="Management of IT in Complex Times"
            units={4}
            status="completed"
            grade="A"
          />
          <CourseCard code="IST 310" title="Data Analytics" units={4} status="completed" grade="A" />
          <CourseCard code="IST 315" title="Information Security" units={4} status="completed" grade="B+" />
          <CourseCard code="IST 320" title="User Experience Design" units={4} status="completed" grade="A-" />
          <CourseCard
            code="IST 321"
            title="Leading Digital Business Transformation"
            units={4}
            status="completed"
            grade="A"
          />
        </TabsContent>

        <TabsContent value="in-progress" className="space-y-2">
          <CourseCard code="IST 330" title="Natural Language Processing" units={4} status="in-progress" />
          <CourseCard code="IST 335" title="Cloud Computing" units={4} status="in-progress" />
        </TabsContent>

        <TabsContent value="waived" className="space-y-2">
          <CourseCard code="IST 301" title="Programming Fundamentals" units={4} status="waived" />
        </TabsContent>
      </Tabs>

      <button
        className="w-full mt-6 flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium border transition-all hover:bg-gray-50"
        style={{ borderColor: 'var(--gray-300)', color: 'var(--gray-700)' }}
      >
        <Edit className="w-4 h-4" />
        Make Corrections
      </button>
    </div>
  );

  const rightPanel = (
    <div>
      <AIBubble>
        <div className="flex items-center gap-2 mb-2">
          <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--success)' }} />
          <strong>Found your courses!</strong>
        </div>
        <p>
          I extracted <strong>11 courses</strong> from your planning sheet:
        </p>
        <ul className="mt-3 space-y-1">
          <li>- <strong>8 completed</strong> (32 units)</li>
          <li>- <strong>2 in progress</strong> (8 units)</li>
          <li>- <strong>1 waived</strong></li>
        </ul>
        <p className="mt-3">
          Please double-check on the left. If anything looks wrong, click{' '}
          <strong>"Make Corrections"</strong> to edit.
        </p>
      </AIBubble>

      <AIBubble>
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          <strong>Next:</strong> I'll compare this with CGU's CISAT requirements to see what you still need
          for graduation.
        </p>
      </AIBubble>
    </div>
  );

  return (
    <>
      <ChatbotButton />
      <ScreenNavigator />
      <HITLBanner checkpoint={1} onContinue={() => navigate('/gap-analysis')} />
      <SplitLayout leftPanel={leftPanel} rightPanel={rightPanel} />
    </>
  );
}
