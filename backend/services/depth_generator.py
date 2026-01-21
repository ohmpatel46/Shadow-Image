"""
Depth map generation service using MiDaS model.
"""
import numpy as np
from PIL import Image
import torch
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
from typing import Optional
import io


class DepthGenerator:
    """Generates depth maps from images using MiDaS model."""
    
    def __init__(self):
        """Initialize the depth generator with MiDaS model."""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = None
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load MiDaS model and processor."""
        try:
            # Use a smaller, faster model for better performance
            model_name = "Intel/dpt-depth-estimation"
            self.processor = AutoImageProcessor.from_pretrained(model_name)
            self.model = AutoModelForDepthEstimation.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"Warning: Could not load MiDaS model: {e}")
            print("Depth generation will be disabled. Install transformers and torch to enable.")
            self.model = None
    
    def generate_depth_map(self, image: Image.Image) -> Optional[np.ndarray]:
        """
        Generate depth map from image.
        
        Args:
            image: PIL Image (RGB)
            
        Returns:
            Depth map as numpy array (0-255 grayscale) or None if model not available
        """
        if self.model is None:
            return None
        
        # Convert PIL to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Prepare inputs
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate depth
        with torch.no_grad():
            outputs = self.model(**inputs)
            predicted_depth = outputs.predicted_depth
        
        # Convert to numpy and normalize to 0-255
        depth = predicted_depth.cpu().numpy()[0, 0]  # Remove batch and channel dims
        
        # Normalize to 0-255 range
        depth_min = depth.min()
        depth_max = depth.max()
        if depth_max > depth_min:
            depth_normalized = ((depth - depth_min) / (depth_max - depth_min) * 255).astype(np.uint8)
        else:
            depth_normalized = np.zeros_like(depth, dtype=np.uint8)
        
        return depth_normalized
    
    def generate_depth_map_from_path(self, image_path: str) -> Optional[np.ndarray]:
        """
        Generate depth map from image file path.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Depth map as numpy array (0-255 grayscale) or None if model not available
        """
        image = Image.open(image_path).convert('RGB')
        return self.generate_depth_map(image)
    
    def generate_depth_map_from_bytes(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Generate depth map from image bytes.
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Depth map as numpy array (0-255 grayscale) or None if model not available
        """
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        return self.generate_depth_map(image)
