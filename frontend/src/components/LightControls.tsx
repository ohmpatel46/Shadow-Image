import React from 'react';

interface LightControlsProps {
  lightAngle: number;
  lightElevation: number;
  onAngleChange: (angle: number) => void;
  onElevationChange: (elevation: number) => void;
}

export const LightControls: React.FC<LightControlsProps> = ({
  lightAngle,
  lightElevation,
  onAngleChange,
  onElevationChange,
}) => {
  return (
    <div className="light-controls">
      <h3 className="controls-title">💡 Light Direction</h3>
      
      <div className="controls-grid">
        <div className="angle-section">
          <div className="angle-visualization">
            <div className="angle-circle">
              <div className="subject-dot"></div>
              <div
                className="light-source"
                style={{ transform: `rotate(${lightAngle}deg) translateX(28px)` }}
              >
                ☀️
              </div>
              <div
                className="light-ray"
                style={{ transform: `rotate(${lightAngle}deg)` }}
              />
            </div>
            <div className="angle-labels">
              <span className="label top">270°</span>
              <span className="label right">0°</span>
              <span className="label bottom">90°</span>
              <span className="label left">180°</span>
            </div>
          </div>
          <div className="slider-row">
            <span className="slider-label">Angle</span>
            <input
              type="range"
              min="0"
              max="360"
              value={lightAngle}
              onChange={(e) => onAngleChange(parseFloat(e.target.value))}
              className="slider"
            />
            <span className="slider-value">{Math.round(lightAngle)}°</span>
          </div>
        </div>

        <div className="elevation-section">
          <div className="elevation-visualization">
            <div className="elevation-arc">
              <div
                className="elevation-indicator"
                style={{
                  transform: `rotate(${-lightElevation}deg)`,
                }}
              >
                <span className="elevation-sun">☀️</span>
              </div>
              <div className="ground-line" />
              <div className="subject-icon">🧍</div>
            </div>
          </div>
          <div className="slider-row">
            <span className="slider-label">Elev</span>
            <input
              type="range"
              min="0"
              max="90"
              value={lightElevation}
              onChange={(e) => onElevationChange(parseFloat(e.target.value))}
              className="slider"
            />
            <span className="slider-value">{Math.round(lightElevation)}°</span>
          </div>
        </div>
      </div>

      <style>{`
        .light-controls {
          background: rgba(255, 255, 255, 0.1);
          padding: 14px;
          border-radius: 8px;
          backdrop-filter: blur(10px);
          height: 100%;
          display: flex;
          flex-direction: column;
        }
        .controls-title {
          color: white;
          margin: 0 0 12px 0;
          font-size: 14px;
          font-weight: 600;
        }
        .controls-grid {
          display: flex;
          gap: 16px;
          flex: 1;
        }
        .angle-section, .elevation-section {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .angle-visualization {
          position: relative;
          display: flex;
          justify-content: center;
          align-items: center;
          flex: 1;
          min-height: 90px;
        }
        .angle-circle {
          width: 70px;
          height: 70px;
          border: 2px solid rgba(255, 255, 255, 0.25);
          border-radius: 50%;
          position: relative;
          display: flex;
          justify-content: center;
          align-items: center;
        }
        .subject-dot {
          width: 8px;
          height: 8px;
          background: #60a5fa;
          border-radius: 50%;
          box-shadow: 0 0 6px #60a5fa;
        }
        .light-source {
          position: absolute;
          top: 50%;
          left: 50%;
          margin: -10px 0 0 -10px;
          font-size: 16px;
          transform-origin: 10px 10px;
          filter: drop-shadow(0 0 4px #fbbf24);
          transition: transform 0.15s;
        }
        .light-ray {
          position: absolute;
          top: 50%;
          left: 50%;
          width: 28px;
          height: 2px;
          background: linear-gradient(to right, rgba(251, 191, 36, 0.2), #fbbf24);
          transform-origin: left center;
          transition: transform 0.15s;
        }
        .angle-labels {
          position: absolute;
          width: 100px;
          height: 100px;
          pointer-events: none;
        }
        .angle-labels .label {
          position: absolute;
          font-size: 9px;
          color: rgba(255, 255, 255, 0.4);
        }
        .angle-labels .top { top: -2px; left: 50%; transform: translateX(-50%); }
        .angle-labels .right { right: -2px; top: 50%; transform: translateY(-50%); }
        .angle-labels .bottom { bottom: -2px; left: 50%; transform: translateX(-50%); }
        .angle-labels .left { left: -2px; top: 50%; transform: translateY(-50%); }

        .elevation-visualization {
          flex: 1;
          display: flex;
          justify-content: center;
          align-items: flex-end;
          min-height: 90px;
          padding-bottom: 8px;
        }
        .elevation-arc {
          position: relative;
          width: 80px;
          height: 50px;
        }
        .ground-line {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          height: 2px;
          background: rgba(255, 255, 255, 0.3);
        }
        .subject-icon {
          position: absolute;
          bottom: 2px;
          left: 50%;
          transform: translateX(-50%);
          font-size: 20px;
        }
        .elevation-indicator {
          position: absolute;
          bottom: 0;
          left: 50%;
          width: 45px;
          height: 2px;
          background: linear-gradient(to right, rgba(251, 191, 36, 0.3), #fbbf24);
          transform-origin: left center;
          transition: transform 0.15s;
        }
        .elevation-sun {
          position: absolute;
          right: -12px;
          top: -8px;
          font-size: 14px;
          filter: drop-shadow(0 0 4px #fbbf24);
        }

        .slider-row {
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .slider-label {
          color: rgba(255, 255, 255, 0.7);
          font-size: 11px;
          width: 32px;
        }
        .slider-value {
          color: white;
          font-size: 11px;
          width: 30px;
          text-align: right;
          font-weight: 500;
        }
        .slider {
          flex: 1;
          height: 4px;
          border-radius: 2px;
          background: rgba(255, 255, 255, 0.2);
          outline: none;
          -webkit-appearance: none;
        }
        .slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
          box-shadow: 0 1px 4px rgba(0,0,0,0.3);
        }
        .slider::-moz-range-thumb {
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
          border: none;
        }
      `}</style>
    </div>
  );
};
