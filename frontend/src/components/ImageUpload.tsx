import React, { useRef, useState } from 'react';

interface ImageUploadProps {
  label: string;
  onImageSelect: (file: File | null) => void;
  preview?: string | null;
  compact?: boolean;
  small?: boolean;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({
  label,
  onImageSelect,
  preview,
  compact,
  small,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileSelect = (file: File | null) => {
    if (file && file.type.startsWith('image/')) {
      onImageSelect(file);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file || null);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    handleFileSelect(file);
  };

  const minHeight = small ? '120px' : compact ? '160px' : '200px';
  const maxImgHeight = small ? '100px' : compact ? '140px' : '300px';

  return (
    <div className="image-upload">
      <div className="image-upload-header">
        <label className="image-upload-label">{label}</label>
        {preview && (
          <button
            className="clear-button"
            onClick={(e) => {
              e.stopPropagation();
              onImageSelect(null);
            }}
          >
            ✕
          </button>
        )}
      </div>
      <div
        className={`image-upload-area ${isDragging ? 'dragging' : ''} ${preview ? 'has-preview' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
        style={{ minHeight: preview ? 'auto' : minHeight }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        {preview ? (
          <img src={preview} alt={label} className="preview-image" style={{ maxHeight: maxImgHeight }} />
        ) : (
          <div className="upload-placeholder">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <p>{small ? 'Upload' : 'Click or drag to upload'}</p>
          </div>
        )}
      </div>
      <style>{`
        .image-upload {
          display: flex;
          flex-direction: column;
          gap: 6px;
          height: 100%;
        }
        .image-upload-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .image-upload-label {
          font-weight: 600;
          color: white;
          font-size: 13px;
        }
        .image-upload-area {
          flex: 1;
          width: 100%;
          border: 2px dashed rgba(255, 255, 255, 0.4);
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s;
          background: rgba(255, 255, 255, 0.08);
          overflow: hidden;
        }
        .image-upload-area:hover {
          border-color: rgba(255, 255, 255, 0.7);
          background: rgba(255, 255, 255, 0.12);
        }
        .image-upload-area.dragging {
          border-color: #4ade80;
          background: rgba(74, 222, 128, 0.15);
        }
        .image-upload-area.has-preview {
          border-style: solid;
          border-color: rgba(255, 255, 255, 0.2);
        }
        .upload-placeholder {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
          color: rgba(255, 255, 255, 0.6);
          font-size: 13px;
        }
        .upload-placeholder p {
          margin: 0;
        }
        .preview-image {
          max-width: 100%;
          object-fit: contain;
        }
        .clear-button {
          padding: 2px 8px;
          background: rgba(239, 68, 68, 0.7);
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 11px;
          transition: background 0.2s;
        }
        .clear-button:hover {
          background: rgba(239, 68, 68, 1);
        }
      `}</style>
    </div>
  );
};
