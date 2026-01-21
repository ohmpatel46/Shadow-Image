# Realistic Shadow Generator

A full-stack application for generating realistic shadows that composite foreground subjects onto background images. Features directional light control, contact shadows, soft shadow falloff, and depth map-based shadow warping.

## Features

✅ **Directional Light Control**
- Light angle (0-360°)
- Light elevation (0-90°)

✅ **Contact Shadow**
- Dark and sharp near the feet/contact area
- Exponential falloff with distance

✅ **Soft Shadow Falloff**
- Progressive blur increases with distance
- Opacity decreases with distance

✅ **Silhouette Matching**
- Shadow matches exact subject shape
- No generic oval shadows

⭐ **Bonus: Depth Map Warping**
- Automatic depth map generation using MiDaS
- Shadow bends/warps based on surface depth for realistic behavior on uneven surfaces

## Project Structure

```
Shadow-Image/
├── backend/              # Python FastAPI server
│   ├── services/         # Core processing services
│   ├── main.py          # API endpoints
│   └── requirements.txt
├── frontend/            # React + TypeScript web app
│   ├── src/
│   │   ├── components/  # UI components
│   │   └── services/    # API client
│   └── package.json
├── assets/              # Input images
└── outputs/             # Generated results
    ├── composite.png
    ├── shadow_only.png
    └── mask_debug.png
```

## Quick Start

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
python main.py
```

The API will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Usage

1. **Upload Images**
   - Upload a foreground image (subject)
   - Upload a background image

2. **Adjust Light Direction**
   - Use the angle slider (0-360°) to set horizontal light direction
   - Use the elevation slider (0-90°) to set light height
   - Lower elevation = longer shadows

3. **Generate Shadow**
   - Click "Generate Shadow" to process
   - Optionally enable "Generate depth map automatically" for depth-based warping

4. **Download Results**
   - View the composite image
   - Download `composite.png`, `shadow_only.png`, and `mask_debug.png`

## API Documentation

### POST /api/process

Process images to generate shadow composite.

**Request:**
- `foreground`: Image file (multipart/form-data)
- `background`: Image file (multipart/form-data)
- `light_angle`: Float (0-360, default: 45)
- `light_elevation`: Float (0-90, default: 30)
- `generate_depth`: Boolean (default: false)

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

**Request:**
- `file`: Image file (multipart/form-data)

**Response:** PNG image file

## Technical Details

### Shadow Generation Algorithm

1. **Subject Extraction**: Uses `rembg` library for automatic background removal
2. **Light Projection**: Converts angle/elevation to 3D direction vector and projects shadow
3. **Contact Shadow**: Identifies contact points and applies high-intensity shadow with exponential falloff
4. **Soft Falloff**: Calculates distance from subject and applies progressive blur and opacity reduction
5. **Depth Warping**: Samples depth map to adjust shadow position based on surface height

### Technologies

**Backend:**
- FastAPI (API framework)
- Pillow, NumPy, OpenCV (image processing)
- rembg (subject extraction)
- PyTorch, Transformers (depth estimation)

**Frontend:**
- React + TypeScript
- Vite (build tool)
- Axios (HTTP client)

## Deliverables

- ✅ `composite.png` - Final composite image
- ✅ `shadow_only.png` - Shadow layer only (debug)
- ✅ `mask_debug.png` - Subject mask visualization
- ✅ Source code (backend + frontend)
- ✅ Comprehensive README

## Testing with Provided Assets

The project includes test assets:
- `25_1107O_11974 PB + 1 - Photo Calendar B_Lamborghini HAS.JPG` - Subject (child)
- `B_Child Room.JPG` - Background option 1
- `B_Lamborghini Red.JPG` - Background option 2

Upload these images through the web interface or use the API directly.

## Notes

- Depth map generation requires PyTorch and will download the model on first use (~150MB)
- Processing time depends on image size and whether depth generation is enabled
- For best results, use images with clear subject-background separation

## License

This project is a technical demonstration for evaluation purposes.