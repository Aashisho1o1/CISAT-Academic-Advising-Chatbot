import { Info } from 'lucide-react';

interface WorkflowAnnotationProps {
  step: number;
  title: string;
  description: string;
}

export function WorkflowAnnotation({ step, title, description }: WorkflowAnnotationProps) {
  return (
    <div
      className="p-4 rounded-lg border flex items-start gap-3"
      style={{
        backgroundColor: 'var(--info)',
        borderColor: 'var(--info)',
        color: 'white',
      }}
    >
      <Info className="w-5 h-5 flex-shrink-0 mt-0.5" />
      <div>
        <p className="font-semibold text-sm mb-1">
          Step {step}: {title}
        </p>
        <p className="text-xs opacity-90">{description}</p>
      </div>
    </div>
  );
}
