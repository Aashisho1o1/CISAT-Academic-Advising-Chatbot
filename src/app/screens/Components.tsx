import { Sparkles, CheckCircle2, AlertTriangle, Info } from 'lucide-react';
import { TopNav } from '../components/TopNav';
import { AIBubble, UserBubble } from '../components/ChatBubbles';
import { CourseCard } from '../components/CourseCard';
import { QuickReplyChip } from '../components/QuickReplyChip';
import { UploadZone } from '../components/UploadZone';
import { HITLBanner } from '../components/HITLBanner';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { ChatbotButton } from '../components/ChatbotButton';

export default function Components() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--gray-50)' }}>
      <ChatbotButton />
      <TopNav />

      <main className="max-w-6xl mx-auto p-8">
        <div className="mb-8">
          <h1 className="mb-2" style={{ color: 'var(--gray-900)' }}>
            Component Library
          </h1>
          <p style={{ color: 'var(--gray-600)' }}>Reusable components for the CISAT Academic Advising Chatbot</p>
        </div>

        <section className="mb-12">
          <h2 className="mb-4" style={{ color: 'var(--gray-900)' }}>
            Chat Bubbles
          </h2>
          <div className="space-y-4 max-w-2xl">
            <AIBubble>
              <p>
                This is an AI message bubble. It has a light background and appears on the right side of
                the chat interface.
              </p>
            </AIBubble>
            <UserBubble>
              This is a user message bubble. It has the CGU red background and white text.
            </UserBubble>
            <AIBubble>
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--success)' }} />
                <strong>AI bubbles can have icons and rich content</strong>
              </div>
              <p>They support multiple paragraphs, lists, and other HTML elements.</p>
            </AIBubble>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="mb-4" style={{ color: 'var(--gray-900)' }}>
            Course Cards
          </h2>
          <div className="grid gap-3 max-w-2xl">
            <CourseCard code="IST 302" title="Databases" units={4} status="completed" grade="A" />
            <CourseCard code="IST 330" title="Natural Language Processing" units={4} status="in-progress" />
            <CourseCard code="IST 301" title="Programming Fundamentals" units={4} status="waived" />
            <CourseCard
              code="IST 340"
              title="Artificial Intelligence for Business"
              units={4}
              status="recommended"
              description="Sample next-term elective for the demo workflow."
            />
          </div>
        </section>

        <section className="mb-12">
          <h2 className="mb-4" style={{ color: 'var(--gray-900)' }}>
            Quick Reply Chips
          </h2>
          <div className="flex flex-wrap gap-2 max-w-2xl">
            <QuickReplyChip>Tell me more</QuickReplyChip>
            <QuickReplyChip>What's next?</QuickReplyChip>
            <QuickReplyChip>How does this work?</QuickReplyChip>
            <QuickReplyChip>Can I make changes?</QuickReplyChip>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="mb-4" style={{ color: 'var(--gray-900)' }}>
            Upload Zone
          </h2>
          <div className="max-w-2xl">
            <UploadZone onUpload={() => {}} />
          </div>
        </section>

        <section className="mb-12">
          <h2 className="mb-4" style={{ color: 'var(--gray-900)' }}>
            Progress Indicators
          </h2>
          <div className="space-y-4 max-w-2xl">
            <div>
              <div className="flex justify-between mb-2 text-sm">
                <span style={{ color: 'var(--gray-700)' }}>Overall Progress</span>
                <span style={{ color: 'var(--gray-900)' }} className="font-semibold">
                  89%
                </span>
              </div>
              <Progress value={89} className="h-2" />
            </div>
            <div>
              <div className="flex justify-between mb-2 text-sm">
                <span style={{ color: 'var(--gray-700)' }}>Core Requirements</span>
                <span style={{ color: 'var(--success)' }} className="font-semibold">
                  100%
                </span>
              </div>
              <Progress value={100} className="h-2" />
            </div>
            <div>
              <div className="flex justify-between mb-2 text-sm">
                <span style={{ color: 'var(--gray-700)' }}>Electives</span>
                <span style={{ color: 'var(--warning)' }} className="font-semibold">
                  67%
                </span>
              </div>
              <Progress value={67} className="h-2" />
            </div>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="mb-4" style={{ color: 'var(--gray-900)' }}>
            Status Badges
          </h2>
          <div className="flex flex-wrap gap-2">
            <Badge variant="default">Default</Badge>
            <Badge variant="secondary">Secondary</Badge>
            <Badge variant="outline">Outline</Badge>
            <Badge variant="destructive">Destructive</Badge>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="mb-4" style={{ color: 'var(--gray-900)' }}>
            Buttons
          </h2>
          <div className="flex flex-wrap gap-3">
            <Button className="text-white" style={{ backgroundColor: 'var(--cgu-red)' }}>
              Primary Action
            </Button>
            <Button variant="outline">Secondary Action</Button>
            <Button variant="ghost">Ghost Button</Button>
            <Button variant="link">Link Button</Button>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="mb-4" style={{ color: 'var(--gray-900)' }}>
            Status Icons
          </h2>
          <div className="flex gap-6">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-6 h-6" style={{ color: 'var(--success)' }} />
              <span className="text-sm">Success</span>
            </div>
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-6 h-6" style={{ color: 'var(--warning)' }} />
              <span className="text-sm">Warning</span>
            </div>
            <div className="flex items-center gap-2">
              <Info className="w-6 h-6" style={{ color: 'var(--info)' }} />
              <span className="text-sm">Info</span>
            </div>
            <div className="flex items-center gap-2">
              <Sparkles className="w-6 h-6" style={{ color: 'var(--cgu-red)' }} />
              <span className="text-sm">AI/Featured</span>
            </div>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="mb-4" style={{ color: 'var(--gray-900)' }}>
            Human-in-the-Loop Banner
          </h2>
          <HITLBanner checkpoint={1} onContinue={() => {}} />
        </section>
      </main>
    </div>
  );
}
