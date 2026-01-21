"""
Shadow generation service for creating realistic shadows.
"""
import numpy as np
from PIL import Image
import cv2
from typing import Tuple, Optional
from scipy.ndimage import gaussian_filter, distance_transform_edt
import math


class ShadowGenerator:
    """Generates realistic shadows with contact shadow and soft falloff."""
    
    def __init__(self):
        """Initialize the shadow generator."""
        pass
    
    def generate_shadow(
        self,
        subject_mask: np.ndarray,
        background_size: Tuple[int, int],
        light_angle: float,
        light_elevation: float,
        depth_map: Optional[np.ndarray] = None,
        subject_x: int = 0,
        subject_y: int = 0,
        contact_fade_distance: float = 50.0,
        max_shadow_distance: float = 300.0,
        base_intensity: float = 0.8,
        max_opacity: float = 0.6
    ) -> np.ndarray:
        """
        Generate realistic shadow from subject mask.
        
        Args:
            subject_mask: Binary mask of the subject (0-255)
            background_size: (width, height) of the background image
            light_angle: Light direction angle in degrees (0-360)
            light_elevation: Light elevation angle in degrees (0-90)
            depth_map: Optional depth map for warping (0-255 grayscale)
            contact_fade_distance: Distance for contact shadow fade
            max_shadow_distance: Maximum shadow projection distance
            base_intensity: Base intensity of contact shadow (0-1)
            max_opacity: Maximum opacity of soft shadow (0-1)
            
        Returns:
            Shadow as grayscale image (0-255)
        """
        bg_width, bg_height = background_size
        mask_height, mask_width = subject_mask.shape
        
        # Convert mask to binary
        mask_binary = (subject_mask > 127).astype(np.uint8)
        
        # Adjust subject position to ensure it fits
        subject_x = max(0, min(subject_x, bg_width - mask_width))
        subject_y = max(0, min(subject_y, bg_height - mask_height))
        
        # Calculate shadow direction vector
        angle_rad = math.radians(light_angle)
        elevation_rad = math.radians(light_elevation)
        
        # 3D direction vector (x, y, z)
        # x: horizontal component (cos of angle)
        # y: vertical component (sin of angle)
        # z: height component (tan of elevation)
        shadow_dx = math.cos(angle_rad) * math.cos(elevation_rad)
        shadow_dy = math.sin(angle_rad) * math.cos(elevation_rad)
        shadow_dz = math.sin(elevation_rad)
        
        # Project shadow onto ground plane
        # Scale factor based on elevation (lower elevation = longer shadow)
        if shadow_dz > 0.01:  # Avoid division by zero
            scale_factor = shadow_dz
        else:
            scale_factor = 0.01
        
        # Calculate projection distance
        shadow_length = max_shadow_distance / scale_factor
        
        # Calculate offset for shadow projection
        offset_x = int(shadow_dx * shadow_length)
        offset_y = int(shadow_dy * shadow_length)
        
        # Create shadow canvas
        shadow = np.zeros((bg_height, bg_width), dtype=np.float32)
        
        # Find contact points (bottom edge of subject)
        contact_points = self._find_contact_points(mask_binary)
        
        # Project each contact point
        for y, x in contact_points:
            # Adjust coordinates to background space
            bg_x = x + subject_x
            bg_y = y + subject_y
            
            # Project this point along shadow direction
            proj_x = bg_x + offset_x
            proj_y = bg_y + offset_y
            
            # Check bounds
            if 0 <= proj_x < bg_width and 0 <= proj_y < bg_height:
                # Calculate distance from contact point
                distance = math.sqrt(offset_x**2 + offset_y**2)
                
                # Contact shadow intensity (exponential falloff)
                contact_intensity = base_intensity * math.exp(-distance / contact_fade_distance)
                
                # Add contact shadow (sharp, dark)
                shadow[int(proj_y), int(proj_x)] = max(
                    shadow[int(proj_y), int(proj_x)],
                    contact_intensity * 255
                )
        
        # Project entire mask for soft shadow
        # Create distance map from subject
        distance_map = self._create_distance_map(mask_binary, offset_x, offset_y, bg_width, bg_height, subject_x, subject_y)
        
        # Apply soft shadow falloff
        soft_shadow = self._apply_soft_falloff(
            distance_map,
            max_shadow_distance,
            max_opacity
        )
        
        # Combine contact shadow and soft shadow
        shadow = np.maximum(shadow, soft_shadow)
        
        # Apply depth warping if depth map provided
        if depth_map is not None:
            shadow = self._apply_depth_warping(shadow, depth_map, shadow_dx, shadow_dy, shadow_dz)
        
        # Apply progressive blur based on distance
        shadow = self._apply_progressive_blur(shadow, distance_map, max_shadow_distance)
        
        # Ensure shadow matches subject silhouette (no shadow where subject is)
        # Create full-size mask at subject position
        full_mask = np.zeros((bg_height, bg_width), dtype=np.uint8)
        if subject_y + mask_height <= bg_height and subject_x + mask_width <= bg_width:
            full_mask[subject_y:subject_y+mask_height, 
                     subject_x:subject_x+mask_width] = mask_binary
        
        # Remove shadow where subject is
        shadow[full_mask > 0] = 0
        
        # Clip to valid range
        shadow = np.clip(shadow, 0, 255).astype(np.uint8)
        
        return shadow
    
    def _find_contact_points(self, mask: np.ndarray) -> list:
        """
        Find contact points (bottom edge) of the subject.
        
        Args:
            mask: Binary mask
            
        Returns:
            List of (y, x) contact point coordinates
        """
        contact_points = []
        height, width = mask.shape
        
        # For each column, find the bottommost point
        for x in range(width):
            for y in range(height - 1, -1, -1):
                if mask[y, x] > 0:
                    contact_points.append((y, x))
                    break
        
        return contact_points
    
    def _create_distance_map(
        self,
        mask: np.ndarray,
        offset_x: int,
        offset_y: int,
        bg_width: int,
        bg_height: int,
        subject_x: int = 0,
        subject_y: int = 0
    ) -> np.ndarray:
        """
        Create distance map from subject to shadow projection points.
        
        Args:
            mask: Subject mask
            offset_x: Shadow offset in x direction
            offset_y: Shadow offset in y direction
            bg_width: Background width
            bg_height: Background height
            
        Returns:
            Distance map
        """
        mask_height, mask_width = mask.shape
        
        # Create full-size canvas
        distance_map = np.full((bg_height, bg_width), float('inf'), dtype=np.float32)
        
        # Project mask
        for y in range(mask_height):
            for x in range(mask_width):
                if mask[y, x] > 0:
                    # Adjust coordinates to background space
                    bg_x = x + subject_x
                    bg_y = y + subject_y
                    
                    proj_x = bg_x + offset_x
                    proj_y = bg_y + offset_y
                    
                    if 0 <= proj_x < bg_width and 0 <= proj_y < bg_height:
                        # Calculate distance from original point
                        distance = math.sqrt(offset_x**2 + offset_y**2)
                        if distance_map[proj_y, proj_x] > distance:
                            distance_map[proj_y, proj_x] = distance
        
        # Fill infinite values with max distance
        max_dist = math.sqrt(offset_x**2 + offset_y**2)
        distance_map[distance_map == float('inf')] = max_dist
        
        return distance_map
    
    def _apply_soft_falloff(
        self,
        distance_map: np.ndarray,
        max_distance: float,
        max_opacity: float
    ) -> np.ndarray:
        """
        Apply soft shadow falloff based on distance.
        
        Args:
            distance_map: Distance from subject
            max_distance: Maximum shadow distance
            max_opacity: Maximum shadow opacity
            
        Returns:
            Soft shadow image
        """
        # Normalize distance
        normalized_distance = np.clip(distance_map / max_distance, 0, 1)
        
        # Exponential falloff
        opacity = max_opacity * np.exp(-normalized_distance * 3)
        
        # Convert to 0-255
        shadow = (opacity * 255).astype(np.uint8)
        
        return shadow
    
    def _apply_progressive_blur(
        self,
        shadow: np.ndarray,
        distance_map: np.ndarray,
        max_distance: float
    ) -> np.ndarray:
        """
        Apply progressive blur based on distance from subject.
        
        Args:
            shadow: Shadow image
            distance_map: Distance from subject
            max_distance: Maximum shadow distance
            
        Returns:
            Blurred shadow image
        """
        # Normalize distance
        normalized_distance = np.clip(distance_map / max_distance, 0, 1)
        
        # Calculate blur radius (0 to 15 pixels)
        blur_radius = normalized_distance * 15
        
        # Apply variable blur
        # We'll use a simplified approach: apply different blur levels to different regions
        shadow_float = shadow.astype(np.float32)
        
        # Create blur levels
        blur_levels = [0, 3, 6, 9, 12, 15]
        blurred_shadows = []
        
        for blur_level in blur_levels:
            if blur_level == 0:
                blurred_shadows.append(shadow_float)
            else:
                blurred = cv2.GaussianBlur(shadow_float, (blur_level*2+1, blur_level*2+1), blur_level)
                blurred_shadows.append(blurred)
        
        # Blend based on distance
        result = np.zeros_like(shadow_float)
        for i, blur_level in enumerate(blur_levels):
            if i < len(blur_levels) - 1:
                threshold_low = i / len(blur_levels)
                threshold_high = (i + 1) / len(blur_levels)
                mask = (normalized_distance >= threshold_low) & (normalized_distance < threshold_high)
                
                if i < len(blur_levels) - 1:
                    # Interpolate between blur levels
                    t = (normalized_distance - threshold_low) / (threshold_high - threshold_low)
                    blended = blurred_shadows[i] * (1 - t) + blurred_shadows[i + 1] * t
                    result[mask] = blended[mask]
                else:
                    result[mask] = blurred_shadows[i][mask]
            else:
                mask = normalized_distance >= threshold_low
                result[mask] = blurred_shadows[i][mask]
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def _apply_depth_warping(
        self,
        shadow: np.ndarray,
        depth_map: np.ndarray,
        shadow_dx: float,
        shadow_dy: float,
        shadow_dz: float
    ) -> np.ndarray:
        """
        Apply depth-based warping to shadow.
        
        Args:
            shadow: Shadow image
            depth_map: Depth map (0-255, higher = closer)
            shadow_dx: Shadow direction x component
            shadow_dy: Shadow direction y component
            shadow_dz: Shadow direction z component
            
        Returns:
            Warped shadow image
        """
        height, width = shadow.shape
        
        # Normalize depth map to 0-1 (invert so higher values = higher surfaces)
        depth_normalized = (255 - depth_map.astype(np.float32)) / 255.0
        
        # Create warped shadow
        warped_shadow = np.zeros_like(shadow, dtype=np.float32)
        
        # Sample depth and adjust shadow position
        for y in range(height):
            for x in range(width):
                if shadow[y, x] > 0:
                    # Get depth at this point
                    depth = depth_normalized[y, x]
                    
                    # Adjust shadow position based on depth
                    # Higher surfaces cast shadows that are offset
                    offset_factor = depth * 10  # Adjust this multiplier for effect strength
                    
                    new_x = int(x + shadow_dx * offset_factor)
                    new_y = int(y + shadow_dy * offset_factor)
                    
                    if 0 <= new_x < width and 0 <= new_y < height:
                        # Blend with existing shadow
                        warped_shadow[new_y, new_x] = max(
                            warped_shadow[new_y, new_x],
                            shadow[y, x]
                        )
                    else:
                        # Keep original if out of bounds
                        warped_shadow[y, x] = max(warped_shadow[y, x], shadow[y, x])
        
        return np.clip(warped_shadow, 0, 255).astype(np.uint8)
    
    def composite_images(
        self,
        foreground: Image.Image,
        background: Image.Image,
        shadow: np.ndarray,
        subject_x: int = 0,
        subject_y: int = 0
    ) -> Image.Image:
        """
        Composite foreground, shadow, and background images.
        
        Args:
            foreground: Foreground image with alpha channel
            background: Background image
            shadow: Shadow as numpy array
            
        Returns:
            Composite image
        """
        # Convert to numpy arrays
        bg_array = np.array(background.convert('RGB'))
        fg_array = np.array(foreground.convert('RGBA'))
        shadow_3d = np.stack([shadow, shadow, shadow], axis=2)  # Convert to RGB
        
        # Place foreground at specified position
        fg_height, fg_width = fg_array.shape[:2]
        bg_height, bg_width = bg_array.shape[:2]
        
        # Ensure foreground fits
        if subject_x + fg_width > bg_width:
            fg_width = bg_width - subject_x
        if subject_y + fg_height > bg_height:
            fg_height = bg_height - subject_y
        
        # Create composite
        composite = bg_array.copy().astype(np.float32)
        
        # Apply shadow (darken background)
        shadow_mask = shadow > 0
        shadow_intensity = shadow.astype(np.float32) / 255.0
        composite[shadow_mask] = composite[shadow_mask] * (1 - shadow_intensity[shadow_mask, np.newaxis] * 0.7)
        
        # Composite foreground
        if subject_x >= 0 and subject_y >= 0:
            fg_region = fg_array[:fg_height, :fg_width]
            alpha = fg_region[:, :, 3:4].astype(np.float32) / 255.0
            
            composite[subject_y:subject_y+fg_height, subject_x:subject_x+fg_width] = (
                composite[subject_y:subject_y+fg_height, subject_x:subject_x+fg_width] * (1 - alpha) +
                fg_region[:, :, :3] * alpha
            )
        
        return Image.fromarray(np.clip(composite, 0, 255).astype(np.uint8))
