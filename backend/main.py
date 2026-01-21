"""
FastAPI server for shadow generation.
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image
import numpy as np
import io
import os
from typing import Optional

from services.subject_extractor import SubjectExtractor
from services.depth_generator import DepthGenerator
from services.shadow_generator import ShadowGenerator

app = FastAPI(title="Shadow Generator API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
subject_extractor = SubjectExtractor()
depth_generator = DepthGenerator()
shadow_generator = ShadowGenerator()

# Create outputs directory
os.makedirs("outputs", exist_ok=True)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Shadow Generator API"}


@app.post("/api/generate-depth")
async def generate_depth(file: UploadFile = File(...)):
    """
    Generate depth map from an image.
    
    Args:
        file: Image file
        
    Returns:
        Depth map image
    """
    try:
        # Read image
        image_bytes = await file.read()
        depth_map = depth_generator.generate_depth_map_from_bytes(image_bytes)
        
        if depth_map is None:
            raise HTTPException(
                status_code=503,
                detail="Depth generation not available. Please install torch and transformers."
            )
        
        # Convert to PIL Image
        depth_image = Image.fromarray(depth_map, mode='L')
        
        # Save to bytes
        output = io.BytesIO()
        depth_image.save(output, format='PNG')
        output.seek(0)
        
        return FileResponse(
            io.BytesIO(output.read()),
            media_type="image/png",
            filename="depth_map.png"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process")
async def process_images(
    foreground: UploadFile = File(...),
    background: UploadFile = File(...),
    light_angle: float = Form(45.0),
    light_elevation: float = Form(30.0),
    depth_map: Optional[UploadFile] = File(None),
    generate_depth: bool = Form(False)
):
    """
    Process images to generate shadow composite.
    
    Args:
        foreground: Foreground image with subject
        background: Background image
        light_angle: Light direction angle (0-360 degrees)
        light_elevation: Light elevation angle (0-90 degrees)
        depth_map: Optional depth map image
        generate_depth: Whether to generate depth map automatically
        
    Returns:
        JSON with paths to output images
    """
    try:
        # Validate light parameters
        light_angle = max(0, min(360, light_angle))
        light_elevation = max(0, min(90, light_elevation))
        
        # Read images
        foreground_bytes = await foreground.read()
        background_bytes = await background.read()
        
        # Load background
        background_image = Image.open(io.BytesIO(background_bytes)).convert('RGB')
        bg_width, bg_height = background_image.size
        
        # Extract subject
        subject_image, subject_mask = subject_extractor.extract_subject_from_bytes(foreground_bytes)
        
        # Get or generate depth map
        depth_map_array = None
        if depth_map:
            depth_map_bytes = await depth_map.read()
            depth_image = Image.open(io.BytesIO(depth_map_bytes)).convert('L')
            depth_map_array = np.array(depth_image)
        elif generate_depth:
            depth_map_array = depth_generator.generate_depth_map(background_image)
        
        # Resize subject mask to match background if needed
        # For now, we'll use the mask as-is and position subject appropriately
        mask_height, mask_width = subject_mask.shape
        
        # Position subject (center horizontally, near top)
        subject_x = (bg_width - mask_width) // 2
        subject_y = 50  # Place near top with some margin
        
        # Generate shadow (with subject position)
        shadow = shadow_generator.generate_shadow(
            subject_mask=subject_mask,
            background_size=(bg_width, bg_height),
            light_angle=light_angle,
            light_elevation=light_elevation,
            depth_map=depth_map_array,
            subject_x=subject_x,
            subject_y=subject_y
        )
        
        # Create composite
        composite = shadow_generator.composite_images(
            foreground=subject_image,
            background=background_image,
            shadow=shadow,
            subject_x=subject_x,
            subject_y=subject_y
        )
        
        # Create mask debug image
        mask_debug = subject_extractor.get_mask_debug_image(subject_mask)
        
        # Save outputs
        composite_path = "outputs/composite.png"
        shadow_path = "outputs/shadow_only.png"
        mask_path = "outputs/mask_debug.png"
        
        composite.save(composite_path)
        Image.fromarray(shadow, mode='L').save(shadow_path)
        mask_debug.save(mask_path)
        
        return JSONResponse({
            "composite": composite_path,
            "shadow_only": shadow_path,
            "mask_debug": mask_path,
            "message": "Processing complete"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/outputs/{filename}")
async def get_output(filename: str):
    """
    Get output file.
    
    Args:
        filename: Name of the output file
        
    Returns:
        File response
    """
    file_path = f"outputs/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
