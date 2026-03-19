import { useEffect, useState } from 'react';
import { Link } from 'react-router';

// Welcome passes showNavigation={false}; we use it to switch home-page branding text.
interface TopNavProps {
  showNavigation?: boolean;
}

export function TopNav({ showNavigation = true }: TopNavProps) {
  const advisorEmail = 'advisor@cgu.edu';
  const [contactCopied, setContactCopied] = useState(false);
  const [showProfilePanel, setShowProfilePanel] = useState(false);

  useEffect(() => {
    if (!contactCopied) return;
    const timeoutId = window.setTimeout(() => setContactCopied(false), 2000);
    return () => window.clearTimeout(timeoutId);
  }, [contactCopied]);

  const handleContactAdvisor = async () => {
    try {
      await navigator.clipboard.writeText(advisorEmail);
      setContactCopied(true);
    } catch {
      setContactCopied(false);
    }

    window.location.href = `mailto:${advisorEmail}`;
  };

  return (
    <nav
      className="h-16 border-b flex items-center justify-between px-8"
      style={{
        backgroundColor: 'white',
        borderColor: 'var(--gray-200)',
      }}
    >
      <div className="flex items-center gap-8">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded flex items-center justify-center" style={{ backgroundColor: 'var(--gray-900)' }}>
            <span className={`text-white font-bold ${showNavigation ? 'text-lg' : 'text-[10px] tracking-wide'}`}>
              {showNavigation ? 'CGU' : 'CISAT'}
            </span>
          </div>
          <span className="font-semibold" style={{ color: 'var(--gray-900)', fontSize: '15px' }}>
            CISAT Advising
          </span>
        </Link>
      </div>

      <div className="relative flex items-center gap-4">
        <button
          type="button"
          onClick={handleContactAdvisor}
          className="px-5 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-90"
          style={{
            backgroundColor: 'var(--cgu-red)',
            color: 'white',
          }}
          title={`Email ${advisorEmail}`}
        >
          {contactCopied ? 'Email Copied' : 'Contact Advisor'}
        </button>
        <button
          type="button"
          onClick={() => setShowProfilePanel(prev => !prev)}
          className="w-10 h-10 rounded-full flex items-center justify-center"
          style={{ backgroundColor: 'var(--gray-900)' }}
          aria-label="Open student profile"
        >
          <span className="text-white font-semibold text-sm">JS</span>
        </button>
        {showProfilePanel && (
          <div
            className="absolute right-0 top-14 w-64 rounded-lg border p-4 shadow-lg"
            style={{
              backgroundColor: 'white',
              borderColor: 'var(--gray-200)',
            }}
          >
            <p className="text-sm font-semibold mb-1" style={{ color: 'var(--gray-900)' }}>
              Student profile
            </p>
            <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
              This MVP does not have real account, settings, or profile features yet.
            </p>
          </div>
        )}
      </div>
    </nav>
  );
}
