# Shadow Generator Backend

FastAPI backend for generating realistic shadows from foreground and background images.

## Setup

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Note: For depth map generation, you'll need PyTorch. The model will be downloaded automatically on first use.

## Running the Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /api/process
Main endpoint for processing images and generating shadows.

**Parameters:**
- `foreground`: Image file (subject)
- `background`: Image file (background)
- `light_angle`: Light direction angle (0-360 degrees, default: 45)
- `light_elevation`: Light elevation angle (0-90 degrees, default: 30)
- `depth_map`: Optional depth map image file
- `generate_depth`: Boolean to auto-generate depth map (default: false)

**Response:**
```json
{
  "composite": "outputs/composite.png",
  "shadow_only": "outputs/shadow_only.png",
  "mask_debug": "outputs/mask_debug.png",
  "message": "Processing complete"
}
```

### POST /api/generate-depth
Generate depth map from an image.

**Parameters:**
- `file`: Image file

**Response:** PNG image file

### GET /api/outputs/{filename}
Get output file by filename.

## Services

- **SubjectExtractor**: Uses rembg to extract subject from background
- **DepthGenerator**: Uses MiDaS model for depth estimation
- **ShadowGenerator**: Creates realistic shadows with contact shadow and soft falloff
