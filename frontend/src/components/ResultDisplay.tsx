import React from 'react';

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
        <p>Processing...</p>
        <style>{styles}</style>
      </div>
    );
  }

  if (!compositeUrl) {
    return (
      <div className="result-display empty">
        <div className="empty-icon">🖼️</div>
        <p>Upload images and generate to see results</p>
        <style>{styles}</style>
      </div>
    );
  }

  return (
    <div className="result-display has-results">
      <h3 className="results-title">Results</h3>
      
      <div className="main-result">
        <div className="result-header">
          <span>Composite</span>
          <button
            className="download-btn"
            onClick={() => handleDownload(compositeUrl, 'composite.png')}
          >
            ⬇ Download
          </button>
        </div>
        <img src={compositeUrl} alt="Composite" className="result-image main" />
      </div>

      <div className="secondary-results">
        <div className="result-item">
          <div className="result-header">
            <span>Shadow</span>
            <button
              className="download-btn small"
              onClick={() => shadowOnlyUrl && handleDownload(shadowOnlyUrl, 'shadow_only.png')}
            >
              ⬇
            </button>
          </div>
          <img src={shadowOnlyUrl || ''} alt="Shadow" className="result-image" />
        </div>

        <div className="result-item">
          <div className="result-header">
            <span>Mask</span>
            <button
              className="download-btn small"
              onClick={() => maskDebugUrl && handleDownload(maskDebugUrl, 'mask_debug.png')}
            >
              ⬇
            </button>
          </div>
          <img src={maskDebugUrl || ''} alt="Mask" className="result-image" />
        </div>
      </div>

      <style>{styles}</style>
    </div>
  );
};

const styles = `
  .result-display {
    background: rgba(255, 255, 255, 0.1);
    padding: 16px;
    border-radius: 8px;
    backdrop-filter: blur(10px);
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  .result-display.loading,
  .result-display.empty {
    align-items: center;
    justify-content: center;
    min-height: 300px;
  }
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255, 255, 255, 0.2);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  .result-display.loading p,
  .result-display.empty p {
    color: rgba(255, 255, 255, 0.7);
    margin-top: 12px;
    font-size: 14px;
  }
  .empty-icon {
    font-size: 48px;
    opacity: 0.5;
  }
  .results-title {
    color: white;
    margin: 0 0 12px 0;
    font-size: 16px;
    font-weight: 600;
  }
  .main-result {
    margin-bottom: 12px;
  }
  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }
  .result-header span {
    color: white;
    font-size: 13px;
    font-weight: 500;
  }
  .result-image {
    width: 100%;
    object-fit: contain;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 6px;
  }
  .result-image.main {
    max-height: calc(100vh - 400px);
    min-height: 200px;
  }
  .secondary-results {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .result-item .result-image {
    max-height: 120px;
  }
  .download-btn {
    padding: 4px 10px;
    background: rgba(59, 130, 246, 0.8);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    transition: background 0.2s;
  }
  .download-btn:hover {
    background: rgba(59, 130, 246, 1);
  }
  .download-btn.small {
    padding: 3px 8px;
    font-size: 11px;
  }
`;
