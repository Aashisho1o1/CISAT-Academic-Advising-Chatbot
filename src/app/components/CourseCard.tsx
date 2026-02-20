import { CheckCircle2, Clock, Ban, Sparkles } from 'lucide-react';

interface CourseCardProps {
  code: string;
  title: string;
  units: number;
  status: 'completed' | 'in-progress' | 'waived' | 'recommended';
  grade?: string;
  description?: string;
}

export function CourseCard({ code, title, units, status, grade, description }: CourseCardProps) {
  const getStatusConfig = () => {
    switch (status) {
      case 'completed':
        return {
          icon: <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--success)' }} />,
          label: 'Completed',
          labelColor: 'var(--success)',
          bgColor: 'white',
          borderColor: 'var(--gray-200)',
        };
      case 'in-progress':
        return {
          icon: <Clock className="w-5 h-5" style={{ color: 'var(--info)' }} />,
          label: 'In Progress',
          labelColor: 'var(--info)',
          bgColor: 'white',
          borderColor: 'var(--info)',
        };
      case 'waived':
        return {
          icon: <Ban className="w-5 h-5" style={{ color: 'var(--gray-400)' }} />,
          label: 'Waived',
          labelColor: 'var(--gray-500)',
          bgColor: 'var(--gray-50)',
          borderColor: 'var(--gray-200)',
        };
      case 'recommended':
        return {
          icon: <Sparkles className="w-5 h-5" style={{ color: 'var(--cgu-red)' }} />,
          label: 'Recommended',
          labelColor: 'var(--cgu-red)',
          bgColor: 'white',
          borderColor: 'var(--cgu-red)',
        };
    }
  };

  const config = getStatusConfig();

  return (
    <div className="p-4 rounded-lg border" style={{ backgroundColor: config.bgColor, borderColor: config.borderColor }}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">{config.icon}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <div>
              <h3 className="font-semibold" style={{ color: 'var(--gray-900)', fontSize: '15px' }}>
                {code}
              </h3>
              <p className="text-sm" style={{ color: 'var(--gray-700)' }}>
                {title}
              </p>
            </div>
            {grade && (
              <span
                className="px-2 py-1 rounded text-xs font-semibold"
                style={{
                  backgroundColor: 'var(--gray-100)',
                  color: 'var(--gray-700)',
                }}
              >
                {grade}
              </span>
            )}
          </div>
          <div className="flex items-center gap-3 mt-2">
            <span className="text-xs" style={{ color: config.labelColor }}>
              {config.label}
            </span>
            <span className="text-xs" style={{ color: 'var(--gray-500)' }}>
              {units} units
            </span>
          </div>
          {description && (
            <p className="text-xs mt-2" style={{ color: 'var(--gray-600)' }}>
              {description}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
