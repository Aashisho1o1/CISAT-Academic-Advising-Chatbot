import React from 'react';

const Chatbot: React.FC = () => {
  // Hardcoded chatbot link - no need for user input
  const CHATBOT_LINK = 'https://chatgpt.com/g/g-68f72859a0288191afe57daa9afecd90-cisat-advising-assistant';

  // Function to open chatbot in new tab
  const handleOpenChatbot = () => {
    // window.open(url, '_blank') opens a new browser tab
    window.open(CHATBOT_LINK, '_blank');
  };

  return (
    <div style={{ padding: '40px', maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
      <h2>🤖 CISAT Advising Assistant</h2>
      <p>Get instant answers about courses, requirements, and graduation planning.</p>

      {/* THE MAIN BUTTON - Opens chatbot in new tab */}
      <button
        onClick={handleOpenChatbot}
        style={{
          marginTop: '40px',
          padding: '20px 40px',
          fontSize: '18px',
          fontWeight: 'bold',
          backgroundColor: '#28a745',
          color: 'white',
          border: 'none',
          borderRadius: '12px',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(40, 167, 69, 0.3)',
          transition: 'all 0.3s ease',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 6px 16px rgba(40, 167, 69, 0.4)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(40, 167, 69, 0.3)';
        }}
      >
        💬 Talk with Your Academic Advising Assistant
      </button>

      {/* Small text below button */}
      <p style={{ marginTop: '15px', color: '#666', fontSize: '14px' }}>
        Click to open your AI advisor in a new tab
      </p>

      {/* Info box */}
      <div
        style={{
          marginTop: '60px',
          padding: '20px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          borderLeft: '4px solid #28a745',
          textAlign: 'left',
        }}
      >
        <strong>💡 Suggested questions:</strong>
        <ul style={{ marginTop: '10px', paddingLeft: '20px' }}>
          <li>What are the MSIS graduation requirements?</li>
          <li>How do I register for courses at CGU?</li>
          <li>What are the prerequisites for a specific course?</li>
          <li>Which courses are required for my program?</li>
        </ul>
      </div>
    </div>
  );
};

export default Chatbot;
