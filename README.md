# Realistic Shadow Generator

A web app that generates realistic shadows for a foreground subject placed on a background image.

## Core Logic

### Shadow Projection
The shadow is projected using the **cotangent of the light elevation angle**:
- `shadow_length = object_height × cot(elevation)`
- **0° elevation** → Very long shadows (horizontal light)
- **45° elevation** → Shadow length equals object height
- **90° elevation** → No shadow (overhead light)

Each pixel of the subject is projected based on its height from the ground - higher points cast shadows further away.

### Contact Shadow
A dark, sharp shadow rendered near the subject's feet that fades quickly with distance. This creates the appearance of the subject being grounded on the surface.

### Soft Shadow Falloff
- Shadow opacity decreases with distance from contact point
- Blur increases progressively with distance
- Creates realistic penumbra effect

### Depth Map Warping (Optional)
If a depth map is provided, the shadow bends/warps based on surface height variations - higher surfaces offset the shadow more.

## Quick Start

### 1. Setup Backend
```bash
# Create and activate conda environment
conda create -n shadow-image python=3.10 -y
conda activate shadow-image

# Install dependencies
cd backend
pip install -r requirements.txt

# Start server
python main.py
```

### 2. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Use the App
1. Open `http://localhost:3000` in your browser
2. Upload a **foreground image** (subject will be auto-extracted)
3. Upload a **background image**
4. Optionally upload a **depth map** (grayscale) for shadow warping
5. Adjust light **angle** (0-360°) and **elevation** (0-90°)
6. Click **Generate Shadow**

## Output Files
- `composite.png` - Final composited image
- `shadow_only.png` - Shadow mask for debugging
- `mask_debug.png` - Subject extraction mask

## Tech Stack
- **Backend**: FastAPI, OpenCV, NumPy, rembg (background removal)
- **Frontend**: React, TypeScript, Vite
