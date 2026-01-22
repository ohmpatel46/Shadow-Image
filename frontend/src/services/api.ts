import axios from 'axios';

const API_BASE_URL = '/api';

export interface ProcessResponse {
  composite: string;
  shadow_only: string;
  mask_debug: string;
  message: string;
}

export const api = {
  async processImages(
    foreground: File,
    background: File,
    lightAngle: number,
    lightElevation: number,
    depthMap?: File
  ): Promise<ProcessResponse> {
    const formData = new FormData();
    formData.append('foreground', foreground);
    formData.append('background', background);
    formData.append('light_angle', lightAngle.toString());
    formData.append('light_elevation', lightElevation.toString());
    
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

  getOutputUrl(filename: string): string {
    return `${API_BASE_URL}/outputs/${filename}`;
  },
};
