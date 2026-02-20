import { Link, useLocation } from 'react-router';

interface TopNavProps {
  showNavigation?: boolean;
}

export function TopNav({ showNavigation = true }: TopNavProps) {
  const location = useLocation();

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
            <span className="text-white font-bold text-lg">CGU</span>
          </div>
          <span className="font-semibold" style={{ color: 'var(--gray-900)', fontSize: '15px' }}>
            CISAT Advising
          </span>
        </Link>

        {showNavigation && (
          <div className="flex gap-1 text-sm">
            <Link
              to="/components"
              className="px-3 py-2 rounded transition-colors"
              style={{
                color: location.pathname === '/components' ? 'var(--gray-900)' : 'var(--gray-600)',
                backgroundColor: location.pathname === '/components' ? 'var(--gray-100)' : 'transparent',
              }}
            >
              Components
            </Link>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={() =>
            window.alert(
              'This would open a contact form or email client to reach your advisor (Prof. Rachel Zhang at rzhang@cgu.edu)',
            )
          }
          className="px-5 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-90"
          style={{
            backgroundColor: 'var(--cgu-red)',
            color: 'white',
          }}
        >
          Contact Advisor
        </button>
        <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: 'var(--gray-900)' }}>
          <span className="text-white font-semibold text-sm">JS</span>
        </div>
      </div>
    </nav>
  );
}
