import React, { useState } from 'react';
import { ImageUpload } from './components/ImageUpload';
import { LightControls } from './components/LightControls';
import { ResultDisplay } from './components/ResultDisplay';
import { api } from './services/api';
import './App.css';

function App() {
  const [foregroundFile, setForegroundFile] = useState<File | null>(null);
  const [backgroundFile, setBackgroundFile] = useState<File | null>(null);
  const [depthMapFile, setDepthMapFile] = useState<File | null>(null);
  const [foregroundPreview, setForegroundPreview] = useState<string | null>(null);
  const [backgroundPreview, setBackgroundPreview] = useState<string | null>(null);
  const [depthMapPreview, setDepthMapPreview] = useState<string | null>(null);
  const [lightAngle, setLightAngle] = useState(45);
  const [lightElevation, setLightElevation] = useState(30);
  const [compositeUrl, setCompositeUrl] = useState<string | null>(null);
  const [shadowOnlyUrl, setShadowOnlyUrl] = useState<string | null>(null);
  const [maskDebugUrl, setMaskDebugUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (
    setter: React.Dispatch<React.SetStateAction<File | null>>,
    previewSetter: React.Dispatch<React.SetStateAction<string | null>>
  ) => (file: File | null) => {
    setter(file);
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => previewSetter(e.target?.result as string);
      reader.readAsDataURL(file);
    } else {
      previewSetter(null);
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
      await api.processImages(
        foregroundFile,
        backgroundFile,
        lightAngle,
        lightElevation,
        depthMapFile || undefined
      );

      const timestamp = Date.now();
      setCompositeUrl(api.getOutputUrl('composite.png') + `?t=${timestamp}`);
      setShadowOnlyUrl(api.getOutputUrl('shadow_only.png') + `?t=${timestamp}`);
      setMaskDebugUrl(api.getOutputUrl('mask_debug.png') + `?t=${timestamp}`);
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
            <div className="upload-row">
              <ImageUpload
                label="Foreground (Subject)"
                onImageSelect={handleFileSelect(setForegroundFile, setForegroundPreview)}
                preview={foregroundPreview}
                compact
              />
              <ImageUpload
                label="Background"
                onImageSelect={handleFileSelect(setBackgroundFile, setBackgroundPreview)}
                preview={backgroundPreview}
                compact
              />
            </div>

            <div className="controls-row">
              <ImageUpload
                label="Depth Map (Optional)"
                onImageSelect={handleFileSelect(setDepthMapFile, setDepthMapPreview)}
                preview={depthMapPreview}
                compact
                small
              />
              <LightControls
                lightAngle={lightAngle}
                lightElevation={lightElevation}
                onAngleChange={setLightAngle}
                onElevationChange={setLightElevation}
              />
            </div>

            <div className="action-row">
              <button
                className="generate-button"
                onClick={handleGenerate}
                disabled={loading || !foregroundFile || !backgroundFile}
              >
                {loading ? 'Generating...' : '✨ Generate Shadow'}
              </button>
              {error && <div className="error-message">{error}</div>}
            </div>
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
