import { Link } from 'react-router';

// Welcome passes showNavigation={false}; we use it to switch home-page branding text.
interface TopNavProps {
  showNavigation?: boolean;
}

export function TopNav({ showNavigation = true }: TopNavProps) {
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

      <div className="flex items-center gap-4">
        {/* mailto: is the correct lightweight solution for a demo.
            Replace with a modal or support ticket form in production. */}
        <a
          href="mailto:advisor@cgu.edu"
          className="px-5 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-90"
          style={{
            backgroundColor: 'var(--cgu-red)',
            color: 'white',
          }}
        >
          Contact Advisor
        </a>
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center"
          style={{ backgroundColor: 'var(--gray-900)' }}
          aria-label="Student profile"
        >
          <span className="text-white font-semibold text-sm">JS</span>
        </div>
      </div>
    </nav>
  );
}
