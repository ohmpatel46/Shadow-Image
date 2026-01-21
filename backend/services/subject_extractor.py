"""
Subject extraction service using rembg for automatic background removal.
"""
import numpy as np
from PIL import Image
from rembg import remove
from typing import Tuple
import io


class SubjectExtractor:
    """Extracts subject from background using rembg library."""
    
    def __init__(self):
        """Initialize the subject extractor."""
        pass
    
    def extract_subject(self, image_path: str) -> Tuple[Image.Image, np.ndarray]:
        """
        Extract subject from image and return RGBA image and mask.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Tuple of (RGBA image with transparent background, binary mask as numpy array)
        """
        # Read the image
        with open(image_path, 'rb') as f:
            input_data = f.read()
        
        # Remove background using rembg
        output_data = remove(input_data)
        
        # Convert to PIL Image
        subject_image = Image.open(io.BytesIO(output_data)).convert('RGBA')
        
        # Extract alpha channel as mask
        mask = np.array(subject_image.split()[3])  # Alpha channel
        mask = (mask > 0).astype(np.uint8) * 255  # Binary mask
        
        return subject_image, mask
    
    def extract_subject_from_bytes(self, image_bytes: bytes) -> Tuple[Image.Image, np.ndarray]:
        """
        Extract subject from image bytes and return RGBA image and mask.
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Tuple of (RGBA image with transparent background, binary mask as numpy array)
        """
        # Remove background using rembg
        output_data = remove(image_bytes)
        
        # Convert to PIL Image
        subject_image = Image.open(io.BytesIO(output_data)).convert('RGBA')
        
        # Extract alpha channel as mask
        mask = np.array(subject_image.split()[3])  # Alpha channel
        mask = (mask > 0).astype(np.uint8) * 255  # Binary mask
        
        return subject_image, mask
    
    def get_mask_debug_image(self, mask: np.ndarray) -> Image.Image:
        """
        Create a debug visualization of the mask.
        
        Args:
            mask: Binary mask array
            
        Returns:
            PIL Image for debugging
        """
        # Create RGB image with mask as red overlay
        debug_image = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
        debug_image[:, :, 0] = mask  # Red channel
        return Image.fromarray(debug_image)
