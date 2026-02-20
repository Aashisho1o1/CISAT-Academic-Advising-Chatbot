import { Link } from 'react-router';
import { FileQuestion } from 'lucide-react';

export default function NotFound() {
  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center p-8 text-center"
      style={{ backgroundColor: 'var(--gray-50)' }}
    >
      <div
        className="w-20 h-20 rounded-2xl flex items-center justify-center mb-6"
        style={{ backgroundColor: 'var(--gray-100)' }}
      >
        <FileQuestion className="w-10 h-10" style={{ color: 'var(--gray-400)' }} />
      </div>

      <h1 className="mb-3" style={{ color: 'var(--gray-900)' }}>
        Page Not Found
      </h1>

      <p className="text-lg mb-8 max-w-sm" style={{ color: 'var(--gray-600)' }}>
        The page you're looking for doesn't exist or has been moved.
      </p>

      <Link
        to="/"
        className="px-8 py-3 rounded-lg font-semibold text-white transition-all hover:opacity-90"
        style={{ backgroundColor: 'var(--cgu-red)' }}
      >
        Back to Home
      </Link>
    </div>
  );
}
