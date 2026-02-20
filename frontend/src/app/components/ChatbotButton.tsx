import { MessageCircle } from 'lucide-react';

export function ChatbotButton() {
  const handleClick = () => {
    window.open('https://chatgpt.com/g/g-68f72859a0288191afe57daa9afecd90-cisat-advising-assistant', '_blank');
  };

  return (
    <button
      onClick={handleClick}
      className="fixed bottom-6 right-6 w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all hover:scale-110 z-50"
      style={{
        backgroundColor: 'var(--cgu-red)',
        color: 'white',
      }}
      title="Try CISAT Chatbot"
    >
      <MessageCircle className="w-6 h-6" />
    </button>
  );
}
