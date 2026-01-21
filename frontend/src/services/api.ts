/**
 * API service for communicating with the backend.
 */
import axios from 'axios';

const API_BASE_URL = '/api';

export interface ProcessResponse {
  composite: string;
  shadow_only: string;
  mask_debug: string;
  message: string;
}

export const api = {
  /**
   * Process images to generate shadow composite.
   */
  async processImages(
    foreground: File,
    background: File,
    lightAngle: number,
    lightElevation: number,
    depthMap?: File,
    generateDepth: boolean = false
  ): Promise<ProcessResponse> {
    const formData = new FormData();
    formData.append('foreground', foreground);
    formData.append('background', background);
    formData.append('light_angle', lightAngle.toString());
    formData.append('light_elevation', lightElevation.toString());
    formData.append('generate_depth', generateDepth.toString());
    
    if (depthMap) {
      formData.append('depth_map', depthMap);
    }

    const response = await axios.post<ProcessResponse>(
      `${API_BASE_URL}/process`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  },

  /**
   * Generate depth map from an image.
   */
  async generateDepth(image: File): Promise<Blob> {
    const formData = new FormData();
    formData.append('file', image);

    const response = await axios.post(
      `${API_BASE_URL}/generate-depth`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      }
    );

    return response.data;
  },

  /**
   * Get output file URL.
   */
  getOutputUrl(filename: string): string {
    return `${API_BASE_URL}/outputs/${filename}`;
  },
};
