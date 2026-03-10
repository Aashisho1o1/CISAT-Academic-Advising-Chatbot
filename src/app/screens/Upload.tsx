import { useNavigate } from 'react-router';
import { SplitLayout } from '../components/SplitLayout';
import { AIBubble, UserBubble } from '../components/ChatBubbles';
import { UploadZone } from '../components/UploadZone';
import { QuickReplyChip } from '../components/QuickReplyChip';
import { ChatbotButton } from '../components/ChatbotButton';
import { ScreenNavigator } from '../components/ScreenNavigator';

export default function Upload() {
  const navigate = useNavigate();

  // _file is prefixed with _ to satisfy noUnusedParameters while the Zustand
  // store doesn't exist yet. Once global state is wired up, replace this with:
  //   useAdvisingStore.getState().setUploadedFile(file);
  const handleUpload = (_file: File) => {
    navigate('/processing');
  };

  const leftPanel = (
    <div>
      <div className="mb-6">
        <h2 className="mb-2" style={{ color: 'var(--gray-900)' }}>
          Demo Planning Sheet Upload
        </h2>
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          Drop a sample file here to continue through the demo workflow.
        </p>
      </div>
      <UploadZone onUpload={handleUpload} />
    </div>
  );

  const rightPanel = (
    <div>
      <AIBubble>
        <p>Hello! I'm your CISAT advising assistant. This upload flow is a demo preview of a future advising experience.</p>
        <p className="mt-3">
          <strong>To continue the walkthrough, upload any supported file.</strong> The live backend feature today is the chat assistant.
        </p>
        <p className="mt-3">
          This demo screen accepts:
        </p>
        <ul className="mt-2 space-y-1">
          <li>- PDF documents</li>
          <li>- Excel spreadsheets (.xlsx)</li>
          <li>- Word documents (.docx)</li>
        </ul>
      </AIBubble>

      <UserBubble>What information do you need from my planning sheet?</UserBubble>

      <AIBubble>
        <p>Great question! I'll extract:</p>
        <ul className="mt-2 space-y-1">
          <li>- Completed courses and grades</li>
          <li>- Courses currently in progress</li>
          <li>- Any waived or transferred courses</li>
          <li>- Total units earned so far</li>
        </ul>
        <p className="mt-3">
          Then I'll compare this against CGU's CISAT MS requirements to see what you still need for
          graduation.
        </p>
      </AIBubble>

      <div className="flex flex-wrap gap-2">
        <QuickReplyChip>Do you store my data?</QuickReplyChip>
        <QuickReplyChip>How accurate is this?</QuickReplyChip>
        <QuickReplyChip>Can I edit after upload?</QuickReplyChip>
      </div>
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
