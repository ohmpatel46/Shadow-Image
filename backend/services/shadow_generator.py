"""Shadow generation service for creating realistic shadows."""
import numpy as np
from PIL import Image
import cv2
from typing import Tuple, Optional
from scipy.ndimage import distance_transform_edt
import math


class ShadowGenerator:
    """Generates realistic shadows with contact shadow and soft falloff."""
    
    def generate_shadow(
        self,
        subject_mask: np.ndarray,
        background_size: Tuple[int, int],
        light_angle: float,
        light_elevation: float,
        depth_map: Optional[np.ndarray] = None,
        subject_x: int = 0,
        subject_y: int = 0,
        max_shadow_distance: float = 300.0,
        base_intensity: float = 0.95,
        max_opacity: float = 0.85
    ) -> np.ndarray:
        """
        Generate realistic shadow from subject mask.
        
        Shadow projection uses cotangent of elevation angle:
        - 0° elevation = very long shadows (horizontal light)
        - 45° elevation = shadow length equals object height  
        - 90° elevation = no shadow (overhead light)
        """
        bg_width, bg_height = background_size
        mask_height, mask_width = subject_mask.shape
        
        mask_binary = (subject_mask > 127).astype(np.uint8)
        
        subject_x = max(0, min(subject_x, bg_width - mask_width))
        subject_y = max(0, min(subject_y, bg_height - mask_height))
        
        # Calculate light direction
        angle_rad = math.radians(light_angle)
        elevation_rad = math.radians(light_elevation)
        
        light_dx = math.cos(angle_rad)
        light_dy = math.sin(angle_rad)
        
        # Shadow length = cot(elevation) = cos/sin
        elevation_sin = max(0.05, math.sin(elevation_rad))
        elevation_cos = math.cos(elevation_rad)
        projection_scale = min(elevation_cos / elevation_sin, 5.0)
        
        # Shadow direction is opposite to light direction
        shadow_dir_x = -light_dx
        shadow_dir_y = -light_dy
        
        # Normalized direction for depth warping
        light_dz = elevation_sin
        norm = math.sqrt(light_dx**2 + light_dy**2 + light_dz**2)
        shadow_dx = light_dx / norm if norm > 0 else light_dx
        shadow_dy = light_dy / norm if norm > 0 else light_dy
        
        estimated_subject_height = mask_height * 0.5
        
        shadow = np.zeros((bg_height, bg_width), dtype=np.float32)
        shadow_silhouette = np.zeros((bg_height, bg_width), dtype=np.uint8)
        
        # Find ground level (bottom of mask)
        bottom_y = mask_height - 1
        for y in range(mask_height - 1, -1, -1):
            if np.any(mask_binary[y, :] > 0):
                bottom_y = y
                break
        
        ground_y_bg = subject_y + bottom_y
        
        # Project each mask point - higher points cast shadows further
        for y in range(mask_height):
            for x in range(mask_width):
                if mask_binary[y, x] > 0:
                    height_from_ground = max(0, (bottom_y - y) / max(1, bottom_y))
                    shadow_offset = height_from_ground * projection_scale * estimated_subject_height
                    
                    bg_x = x + subject_x
                    proj_x = bg_x + shadow_dir_x * shadow_offset
                    proj_y = ground_y_bg + shadow_dir_y * shadow_offset
                    
                    if 0 <= proj_x < bg_width and 0 <= proj_y < bg_height:
                        shadow_silhouette[int(proj_y), int(proj_x)] = 255
        
        # Fill gaps in shadow silhouette
        kernel = np.ones((5, 5), np.uint8)
        shadow_silhouette = cv2.dilate(shadow_silhouette, kernel, iterations=2)
        shadow_silhouette = cv2.erode(shadow_silhouette, kernel, iterations=1)
        
        # Find contact points (bottom edge of subject)
        contact_points = self._find_contact_points(mask_binary)
        
        # Create contact shadow (darkest near feet)
        contact_shadow = np.zeros((bg_height, bg_width), dtype=np.float32)
        contact_radius = 25
        
        for y, x in contact_points:
            bg_x = x + subject_x
            bg_y = y + subject_y
            
            for dy in range(-contact_radius, contact_radius + 5):
                for dx in range(-contact_radius, contact_radius + 5):
                    px = int(bg_x + dx + shadow_dir_x * 5)
                    py = int(bg_y + dy + shadow_dir_y * 5)
                    
                    if 0 <= px < bg_width and 0 <= py < bg_height:
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist < contact_radius:
                            intensity = 0.98 * math.exp(-dist / (contact_radius * 0.4))
                            contact_shadow[py, px] = max(contact_shadow[py, px], intensity * 255)
        
        if np.any(contact_shadow > 0):
            contact_shadow = cv2.GaussianBlur(contact_shadow, (7, 7), 2)
        
        shadow = np.maximum(shadow, contact_shadow)
        
        # Create distance map from contact line
        distance_map = self._create_distance_map(
            mask_binary, shadow_silhouette, bg_width, bg_height,
            subject_x, subject_y, contact_points
        )
        
        # Apply soft shadow falloff
        soft_shadow = self._apply_soft_falloff(distance_map, max_shadow_distance, max_opacity)
        
        # Only apply soft shadow where shadow silhouette exists
        shadow_mask = (shadow_silhouette > 0).astype(np.float32)
        soft_shadow = soft_shadow * shadow_mask
        
        # Fallback if no shadow silhouette was created
        if np.sum(shadow_silhouette > 0) == 0:
            offset_x = int(shadow_dir_x * projection_scale * estimated_subject_height * 0.3)
            offset_y = int(shadow_dir_y * projection_scale * estimated_subject_height * 0.3)
            for y in range(mask_height):
                for x in range(mask_width):
                    if mask_binary[y, x] > 0:
                        proj_x = x + subject_x + offset_x
                        proj_y = y + subject_y + offset_y
                        if 0 <= proj_x < bg_width and 0 <= proj_y < bg_height:
                            shadow_silhouette[int(proj_y), int(proj_x)] = 255
                            soft_shadow[int(proj_y), int(proj_x)] = max_opacity * 200
        
        shadow = np.maximum(shadow, soft_shadow)
        
        # Fallback if shadow is still mostly empty
        if np.sum(shadow > 10) < 100:
            offset_x = int(shadow_dir_x * projection_scale * estimated_subject_height * 0.5)
            offset_y = int(shadow_dir_y * projection_scale * estimated_subject_height * 0.5)
            for y in range(mask_height):
                for x in range(mask_width):
                    if mask_binary[y, x] > 0:
                        proj_x = x + subject_x + offset_x
                        proj_y = y + subject_y + offset_y
                        if 0 <= proj_x < bg_width and 0 <= proj_y < bg_height:
                            shadow[int(proj_y), int(proj_x)] = max(
                                shadow[int(proj_y), int(proj_x)],
                                max_opacity * 200
                            )
        
        # Apply depth warping if depth map provided
        if depth_map is not None:
            shadow = self._apply_depth_warping(shadow, depth_map, shadow_dx, shadow_dy)
        
        # Apply progressive blur
        shadow = self._apply_progressive_blur(shadow, distance_map, max_shadow_distance)
        
        # Remove shadow where subject is
        full_mask = np.zeros((bg_height, bg_width), dtype=np.uint8)
        if subject_y + mask_height <= bg_height and subject_x + mask_width <= bg_width:
            full_mask[subject_y:subject_y+mask_height, subject_x:subject_x+mask_width] = mask_binary
        shadow[full_mask > 0] = 0
        
        return np.clip(shadow, 0, 255).astype(np.uint8)
    
    def _find_contact_points(self, mask: np.ndarray) -> list:
        """Find bottom edge points of subject."""
        contact_points = []
        height, width = mask.shape
        for x in range(width):
            for y in range(height - 1, -1, -1):
                if mask[y, x] > 0:
                    contact_points.append((y, x))
                    break
        return contact_points
    
    def _create_distance_map(
        self, mask: np.ndarray, shadow_silhouette: np.ndarray,
        bg_width: int, bg_height: int, subject_x: int, subject_y: int,
        contact_points: list
    ) -> np.ndarray:
        """Create distance map from contact line for shadow gradient."""
        mask_height, mask_width = mask.shape
        distance_map = np.full((bg_height, bg_width), float('inf'), dtype=np.float32)
        
        # Create contact line mask
        contact_mask = np.zeros((bg_height, bg_width), dtype=np.uint8)
        if contact_points:
            for y, x in contact_points:
                bg_x = x + subject_x
                bg_y = y + subject_y
                if 0 <= bg_x < bg_width and 0 <= bg_y < bg_height:
                    for dy in range(-3, 4):
                        if 0 <= bg_y + dy < bg_height:
                            contact_mask[bg_y + dy, bg_x] = 255
        
        dist_from_contact = distance_transform_edt(~contact_mask.astype(bool))
        
        shadow_pixels = shadow_silhouette > 0
        if np.any(shadow_pixels):
            distance_map[shadow_pixels] = dist_from_contact[shadow_pixels]
        
        # Fill infinite values
        max_dist = 300.0
        if np.any(shadow_pixels):
            valid_dists = dist_from_contact[shadow_pixels]
            if len(valid_dists) > 0:
                max_dist = np.max(valid_dists)
        distance_map[distance_map == float('inf')] = max_dist
        
        return distance_map
    
    def _apply_soft_falloff(
        self, distance_map: np.ndarray, max_distance: float, max_opacity: float
    ) -> np.ndarray:
        """Apply opacity falloff - darkest at contact, lighter with distance."""
        normalized_dist = np.clip(distance_map / max_distance, 0, 1)
        
        # Dark near contact, fading with distance
        opacity = max_opacity * (1.0 - normalized_dist * 0.7)
        contact_boost = np.exp(-normalized_dist * 3) * 0.3
        opacity = np.clip(opacity + contact_boost, 0.1, 1.0)
        
        return (opacity * 255).astype(np.float32)
    
    def _apply_progressive_blur(
        self, shadow: np.ndarray, distance_map: np.ndarray, max_distance: float
    ) -> np.ndarray:
        """Apply increasing blur with distance from subject."""
        normalized_dist = np.clip(distance_map / max_distance, 0, 1)
        shadow_float = shadow.astype(np.float32)
        
        blur_levels = [0, 3, 6, 9, 12, 15]
        blurred = []
        for b in blur_levels:
            if b == 0:
                blurred.append(shadow_float.copy())
            else:
                blurred.append(cv2.GaussianBlur(shadow_float, (b*2+1, b*2+1), b))
        
        result = shadow_float.copy()
        
        for i in range(len(blur_levels)):
            low = i / len(blur_levels)
            high = (i + 1) / len(blur_levels)
            mask = (normalized_dist >= low) & (normalized_dist < high)
            
            if np.any(mask):
                if i < len(blur_levels) - 1:
                    t = np.clip((normalized_dist[mask] - low) / (high - low), 0, 1)
                    result[mask] = blurred[i][mask] * (1 - t) + blurred[min(i+1, len(blurred)-1)][mask] * t
                else:
                    result[mask] = blurred[i][mask]
        
        # Handle remaining pixels
        remaining = normalized_dist >= 1.0
        if np.any(remaining):
            result[remaining] = blurred[-1][remaining]
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def _apply_depth_warping(
        self, shadow: np.ndarray, depth_map: np.ndarray,
        shadow_dx: float, shadow_dy: float
    ) -> np.ndarray:
        """Warp shadow based on depth map - higher surfaces offset shadow more."""
        height, width = shadow.shape
        
        # Resize depth map if needed
        if depth_map.shape != shadow.shape:
            depth_img = Image.fromarray(depth_map, mode='L')
            depth_img = depth_img.resize((width, height), Image.LANCZOS)
            depth_map = np.array(depth_img)
        
        # Invert: higher depth values = higher surfaces
        depth_norm = (255 - depth_map.astype(np.float32)) / 255.0
        
        warped = np.zeros_like(shadow, dtype=np.float32)
        
        for y in range(height):
            for x in range(width):
                if shadow[y, x] > 0:
                    offset = depth_norm[y, x] * 10
                    new_x = int(x + shadow_dx * offset)
                    new_y = int(y + shadow_dy * offset)
                    
                    if 0 <= new_x < width and 0 <= new_y < height:
                        warped[new_y, new_x] = max(warped[new_y, new_x], shadow[y, x])
                    else:
                        warped[y, x] = max(warped[y, x], shadow[y, x])
        
        return np.clip(warped, 0, 255).astype(np.uint8)
    
    def composite_images(
        self, foreground: Image.Image, background: Image.Image,
        shadow: np.ndarray, subject_x: int = 0, subject_y: int = 0
    ) -> Image.Image:
        """Composite foreground, shadow, and background."""
        bg_array = np.array(background.convert('RGB'))
        fg_array = np.array(foreground.convert('RGBA'))
        
        fg_height, fg_width = fg_array.shape[:2]
        bg_height, bg_width = bg_array.shape[:2]
        
        subject_x = max(0, min(subject_x, bg_width - 1))
        subject_y = max(0, min(subject_y, bg_height - 1))
        fg_width = min(fg_width, bg_width - subject_x)
        fg_height = min(fg_height, bg_height - subject_y)
        
        composite = bg_array.copy().astype(np.float32)
        
        # Ensure shadow has correct dimensions
        if len(shadow.shape) != 2:
            raise ValueError(f"Shadow must be 2D, got shape {shadow.shape}")
        
        if shadow.shape != (bg_height, bg_width):
            shadow_img = Image.fromarray(shadow, mode='L')
            shadow_img = shadow_img.resize((bg_width, bg_height), Image.LANCZOS)
            shadow = np.array(shadow_img)
        
        # Apply shadow (darken background)
        if np.any(shadow > 0):
            shadow_intensity = shadow.astype(np.float32) / 255.0
            shadow_factor = 1 - shadow_intensity[:, :, np.newaxis] * 0.7
            composite = composite * shadow_factor
        
        # Composite foreground
        if subject_x >= 0 and subject_y >= 0 and fg_width > 0 and fg_height > 0:
            fg_region = fg_array[:fg_height, :fg_width]
            alpha = fg_region[:, :, 3:4].astype(np.float32) / 255.0
            
            bg_region = composite[subject_y:subject_y+fg_height, subject_x:subject_x+fg_width]
            composite[subject_y:subject_y+fg_height, subject_x:subject_x+fg_width] = (
                bg_region * (1 - alpha) + fg_region[:, :, :3] * alpha
            )
        
        return Image.fromarray(np.clip(composite, 0, 255).astype(np.uint8))
