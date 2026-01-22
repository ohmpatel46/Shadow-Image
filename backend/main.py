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
from services.shadow_generator import ShadowGenerator

app = FastAPI(title="Shadow Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

subject_extractor = SubjectExtractor()
shadow_generator = ShadowGenerator()

os.makedirs("outputs", exist_ok=True)


@app.get("/")
async def root():
    return {"message": "Shadow Generator API"}


@app.post("/api/process")
async def process_images(
    foreground: UploadFile = File(...),
    background: UploadFile = File(...),
    light_angle: float = Form(45.0),
    light_elevation: float = Form(30.0),
    depth_map: Optional[UploadFile] = File(None)
):
    """
    Process images to generate shadow composite.
    
    Args:
        foreground: Foreground image with subject
        background: Background image
        light_angle: Light direction angle (0-360 degrees)
        light_elevation: Light elevation angle (0-90 degrees)
        depth_map: Optional depth map image for shadow warping
        
    Returns:
        JSON with paths to output images
    """
    try:
        light_angle = max(0, min(360, light_angle))
        light_elevation = max(0, min(90, light_elevation))
        
        foreground_bytes = await foreground.read()
        background_bytes = await background.read()
        
        background_image = Image.open(io.BytesIO(background_bytes)).convert('RGB')
        bg_width, bg_height = background_image.size
        
        subject_image, subject_mask = subject_extractor.extract_subject_from_bytes(foreground_bytes)
        
        # Process depth map if provided
        depth_map_array = None
        if depth_map:
            depth_map_bytes = await depth_map.read()
            depth_image = Image.open(io.BytesIO(depth_map_bytes)).convert('L')
            # Resize depth map to match background
            depth_image = depth_image.resize((bg_width, bg_height), Image.LANCZOS)
            depth_map_array = np.array(depth_image)
        
        mask_height, mask_width = subject_mask.shape
        
        # Position subject (center horizontally, near top)
        subject_x = (bg_width - mask_width) // 2
        subject_y = 50
        
        shadow = shadow_generator.generate_shadow(
            subject_mask=subject_mask,
            background_size=(bg_width, bg_height),
            light_angle=light_angle,
            light_elevation=light_elevation,
            depth_map=depth_map_array,
            subject_x=subject_x,
            subject_y=subject_y
        )
        
        composite = shadow_generator.composite_images(
            foreground=subject_image,
            background=background_image,
            shadow=shadow,
            subject_x=subject_x,
            subject_y=subject_y
        )
        
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
    file_path = f"outputs/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
