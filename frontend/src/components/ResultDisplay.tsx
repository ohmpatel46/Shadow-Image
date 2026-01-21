import React from 'react';
import { api } from '../services/api';

interface ResultDisplayProps {
  compositeUrl?: string | null;
  shadowOnlyUrl?: string | null;
  maskDebugUrl?: string | null;
  loading?: boolean;
}

export const ResultDisplay: React.FC<ResultDisplayProps> = ({
  compositeUrl,
  shadowOnlyUrl,
  maskDebugUrl,
  loading,
}) => {
  const handleDownload = (url: string, filename: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="result-display loading">
        <div className="spinner"></div>
        <p>Processing images...</p>
        <style>{`
          .result-display.loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 60px 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            backdrop-filter: blur(10px);
          }
          .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
          .result-display.loading p {
            color: white;
            margin-top: 20px;
            font-size: 16px;
          }
        `}</style>
      </div>
    );
  }

  if (!compositeUrl) {
    return (
      <div className="result-display empty">
        <p>Upload images and click "Generate Shadow" to see results</p>
        <style>{`
          .result-display.empty {
            padding: 60px 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            backdrop-filter: blur(10px);
            text-align: center;
          }
          .result-display.empty p {
            color: rgba(255, 255, 255, 0.7);
            font-size: 16px;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="result-display">
      <h3 className="results-title">Results</h3>
      
      <div className="result-grid">
        <div className="result-item">
          <h4>Composite</h4>
          <img src={compositeUrl} alt="Composite" className="result-image" />
          <button
            className="download-button"
            onClick={() => handleDownload(compositeUrl, 'composite.png')}
          >
            Download
          </button>
        </div>

        <div className="result-item">
          <h4>Shadow Only</h4>
          <img src={shadowOnlyUrl || ''} alt="Shadow Only" className="result-image" />
          <button
            className="download-button"
            onClick={() => shadowOnlyUrl && handleDownload(shadowOnlyUrl, 'shadow_only.png')}
            disabled={!shadowOnlyUrl}
          >
            Download
          </button>
        </div>

        <div className="result-item">
          <h4>Mask Debug</h4>
          <img src={maskDebugUrl || ''} alt="Mask Debug" className="result-image" />
          <button
            className="download-button"
            onClick={() => maskDebugUrl && handleDownload(maskDebugUrl, 'mask_debug.png')}
            disabled={!maskDebugUrl}
          >
            Download
          </button>
        </div>
      </div>

      <style>{`
        .result-display {
          background: rgba(255, 255, 255, 0.1);
          padding: 20px;
          border-radius: 8px;
          backdrop-filter: blur(10px);
        }
        .results-title {
          color: white;
          margin-bottom: 20px;
          font-size: 18px;
        }
        .result-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
        }
        .result-item {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .result-item h4 {
          color: white;
          font-size: 14px;
          font-weight: 600;
        }
        .result-image {
          width: 100%;
          max-height: 300px;
          object-fit: contain;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 4px;
        }
        .download-button {
          padding: 8px 16px;
          background: rgba(59, 130, 246, 0.8);
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: background 0.2s;
        }
        .download-button:hover:not(:disabled) {
          background: rgba(59, 130, 246, 1);
        }
        .download-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};
