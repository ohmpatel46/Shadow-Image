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
      <h3 className="controls-title">Light Direction</h3>
      
      <div className="control-group">
        <label className="control-label">
          Angle: {Math.round(lightAngle)}°
        </label>
        <input
          type="range"
          min="0"
          max="360"
          value={lightAngle}
          onChange={(e) => onAngleChange(parseFloat(e.target.value))}
          className="slider"
        />
        <div className="angle-visualization">
          <div
            className="angle-indicator"
            style={{
              transform: `rotate(${lightAngle}deg)`,
            }}
          >
            <div className="light-ray"></div>
          </div>
        </div>
      </div>

      <div className="control-group">
        <label className="control-label">
          Elevation: {Math.round(lightElevation)}°
        </label>
        <input
          type="range"
          min="0"
          max="90"
          value={lightElevation}
          onChange={(e) => onElevationChange(parseFloat(e.target.value))}
          className="slider"
        />
        <div className="elevation-visualization">
          <div className="elevation-bar">
            <div
              className="elevation-fill"
              style={{
                height: `${(lightElevation / 90) * 100}%`,
              }}
            ></div>
          </div>
        </div>
      </div>

      <style>{`
        .light-controls {
          background: rgba(255, 255, 255, 0.1);
          padding: 20px;
          border-radius: 8px;
          backdrop-filter: blur(10px);
        }
        .controls-title {
          color: white;
          margin-bottom: 20px;
          font-size: 18px;
        }
        .control-group {
          margin-bottom: 24px;
        }
        .control-label {
          display: block;
          color: white;
          margin-bottom: 8px;
          font-weight: 500;
        }
        .slider {
          width: 100%;
          height: 6px;
          border-radius: 3px;
          background: rgba(255, 255, 255, 0.3);
          outline: none;
          -webkit-appearance: none;
        }
        .slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
        }
        .slider::-moz-range-thumb {
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: white;
          cursor: pointer;
          border: none;
        }
        .angle-visualization {
          margin-top: 12px;
          display: flex;
          justify-content: center;
          align-items: center;
          height: 80px;
          position: relative;
        }
        .angle-indicator {
          width: 60px;
          height: 60px;
          position: relative;
          transition: transform 0.2s;
        }
        .light-ray {
          position: absolute;
          top: 50%;
          left: 50%;
          width: 40px;
          height: 2px;
          background: linear-gradient(to right, #fbbf24, transparent);
          transform-origin: left center;
          box-shadow: 0 0 10px #fbbf24;
        }
        .elevation-visualization {
          margin-top: 12px;
          display: flex;
          justify-content: center;
          align-items: flex-end;
          height: 60px;
        }
        .elevation-bar {
          width: 20px;
          height: 50px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 10px;
          position: relative;
          overflow: hidden;
        }
        .elevation-fill {
          position: absolute;
          bottom: 0;
          width: 100%;
          background: linear-gradient(to top, #fbbf24, #f59e0b);
          transition: height 0.2s;
          border-radius: 10px;
        }
      `}</style>
    </div>
  );
};
