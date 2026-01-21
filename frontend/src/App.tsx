import React, { useState } from 'react';
import { ImageUpload } from './components/ImageUpload';
import { LightControls } from './components/LightControls';
import { ResultDisplay } from './components/ResultDisplay';
import { api } from './services/api';
import './App.css';

function App() {
  const [foregroundFile, setForegroundFile] = useState<File | null>(null);
  const [backgroundFile, setBackgroundFile] = useState<File | null>(null);
  const [foregroundPreview, setForegroundPreview] = useState<string | null>(null);
  const [backgroundPreview, setBackgroundPreview] = useState<string | null>(null);
  const [lightAngle, setLightAngle] = useState(45);
  const [lightElevation, setLightElevation] = useState(30);
  const [compositeUrl, setCompositeUrl] = useState<string | null>(null);
  const [shadowOnlyUrl, setShadowOnlyUrl] = useState<string | null>(null);
  const [maskDebugUrl, setMaskDebugUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generateDepth, setGenerateDepth] = useState(false);

  const handleForegroundSelect = (file: File | null) => {
    setForegroundFile(file);
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setForegroundPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setForegroundPreview(null);
    }
  };

  const handleBackgroundSelect = (file: File | null) => {
    setBackgroundFile(file);
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setBackgroundPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setBackgroundPreview(null);
    }
  };

  const handleGenerate = async () => {
    if (!foregroundFile || !backgroundFile) {
      setError('Please upload both foreground and background images');
      return;
    }

    setLoading(true);
    setError(null);
    setCompositeUrl(null);
    setShadowOnlyUrl(null);
    setMaskDebugUrl(null);

    try {
      const response = await api.processImages(
        foregroundFile,
        backgroundFile,
        lightAngle,
        lightElevation,
        undefined,
        generateDepth
      );

      // Construct URLs for the output images
      const compositeUrlFull = api.getOutputUrl('composite.png') + `?t=${Date.now()}`;
      const shadowUrlFull = api.getOutputUrl('shadow_only.png') + `?t=${Date.now()}`;
      const maskUrlFull = api.getOutputUrl('mask_debug.png') + `?t=${Date.now()}`;

      setCompositeUrl(compositeUrlFull);
      setShadowOnlyUrl(shadowUrlFull);
      setMaskDebugUrl(maskUrlFull);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate shadow');
      console.error('Error generating shadow:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🎨 Realistic Shadow Generator</h1>
          <p>Create realistic shadows for your images</p>
        </header>

        <div className="main-content">
          <div className="left-panel">
            <div className="section">
              <ImageUpload
                label="Foreground Image (Subject)"
                onImageSelect={handleForegroundSelect}
                preview={foregroundPreview}
              />
            </div>

            <div className="section">
              <ImageUpload
                label="Background Image"
                onImageSelect={handleBackgroundSelect}
                preview={backgroundPreview}
              />
            </div>

            <div className="section">
              <LightControls
                lightAngle={lightAngle}
                lightElevation={lightElevation}
                onAngleChange={setLightAngle}
                onElevationChange={setLightElevation}
              />
            </div>

            <div className="section">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={generateDepth}
                  onChange={(e) => setGenerateDepth(e.target.checked)}
                />
                <span>Generate depth map automatically</span>
              </label>
            </div>

            <button
              className="generate-button"
              onClick={handleGenerate}
              disabled={loading || !foregroundFile || !backgroundFile}
            >
              {loading ? 'Generating...' : 'Generate Shadow'}
            </button>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
          </div>

          <div className="right-panel">
            <ResultDisplay
              compositeUrl={compositeUrl}
              shadowOnlyUrl={shadowOnlyUrl}
              maskDebugUrl={maskDebugUrl}
              loading={loading}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
