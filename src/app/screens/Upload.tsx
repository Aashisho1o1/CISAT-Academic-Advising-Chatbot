import { useNavigate } from 'react-router';
import { SplitLayout } from '../components/SplitLayout';
import { AIBubble, UserBubble } from '../components/ChatBubbles';
import { UploadZone } from '../components/UploadZone';
import { QuickReplyChip } from '../components/QuickReplyChip';
import { ChatbotButton } from '../components/ChatbotButton';
import { ScreenNavigator } from '../components/ScreenNavigator';
import { useState } from 'react';
import { API_URL } from '../../config';
import { useAdvisingStore } from '../store';
export default function Upload() {
  const navigate = useNavigate();
  const setSession = useAdvisingStore((state) => state.setSession);
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch(`${API_URL}/api/upload-plan`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload plan');
      }

      const data = await response.json();
      setSession(data.thread_id, data.file_id);
      navigate('/processing');
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload the file. Please ensure the backend is running.');
    } finally {
      setIsUploading(false);
    }
  };

  const leftPanel = (
    <div>
      <div className="mb-6">
        <h2 className="mb-2" style={{ color: 'var(--gray-900)' }}>
          Planning Sheet Upload
        </h2>
        <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
          Drop your file here to continue through the advising workflow.
        </p>
      </div>
      {isUploading ? (
        <div className="p-8 text-center" style={{ backgroundColor: 'var(--gray-50)', borderRadius: '1rem', border: '1px solid var(--gray-200)' }}>
          <p style={{ color: 'var(--cgu-red)' }}><strong>Uploading securely...</strong></p>
          <p className="text-sm mt-2 text-gray-500">Creating OpenAI Thread and uploading file via Assistants API.</p>
        </div>
      ) : (
        <UploadZone onUpload={handleUpload} />
      )}
    </div>
  );

  const rightPanel = (
    <div>
      <AIBubble>
        <p>Hello! I'm your CISAT advising assistant. Welcome to your personalized advising experience.</p>
        <p className="mt-3">
          <strong>To continue, upload any supported file.</strong>
        </p>
        <p className="mt-3">
          We accept:
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
