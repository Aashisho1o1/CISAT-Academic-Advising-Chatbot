import { useState } from 'react';
import { Upload } from 'lucide-react';

interface UploadZoneProps {
  onUpload: (file: File) => void;
}

export function UploadZone({ onUpload }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    // Only clear isDragging when the cursor leaves the component entirely.
    // Without this check, moving over any child element (the icon, the text)
    // fires onDragLeave on the parent, causing a visible border-color flicker.
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setIsDragging(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      onUpload(file);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className="relative border-2 border-dashed rounded-lg p-12 text-center transition-all cursor-pointer hover:border-gray-400"
      style={{
        borderColor: isDragging ? 'var(--cgu-red)' : 'var(--gray-300)',
        backgroundColor: isDragging ? 'var(--gray-50)' : 'white',
      }}
    >
      <input
        type="file"
        onChange={handleFileSelect}
        accept=".pdf,.xlsx,.xls,.docx,.doc"
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />

      <div className="flex flex-col items-center gap-4">
        <div className="w-16 h-16 rounded-full flex items-center justify-center" style={{ backgroundColor: 'var(--gray-100)' }}>
          <Upload className="w-8 h-8" style={{ color: 'var(--gray-600)' }} />
        </div>

        <div>
          <p className="font-medium mb-1" style={{ color: 'var(--gray-900)' }}>
            Drop your planning sheet here
          </p>
          <p className="text-sm" style={{ color: 'var(--gray-600)' }}>
            or click to browse files
          </p>
        </div>

        <p className="text-xs" style={{ color: 'var(--gray-500)' }}>
          Supports PDF, Excel (.xlsx), and Word (.docx) files
        </p>
      </div>
    </div>
  );
}
