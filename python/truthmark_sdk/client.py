from typing import Optional, Dict, Any
import os
import requests

class TruthMarkClient:
    """
    Official Python SDK for TruthMark API.
    Embed and extract invisible watermarks using the TruthMark cloud engine.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://truthmark-api.onrender.com"):
        """
        Initialize the TruthMark client.
        
        Args:
            api_key: Your API key (currently unused for public beta)
            base_url: URL of the TruthMark API
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}"
        }

    def encode(self, image_path: str, message: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Embed a message into an image via the API.
        
        Args:
            image_path: Path to input image
            message: Text message to embed
            output_path: Optional path to save result
            
        Returns:
            Dictionary with metadata and output path
        """
        if not os.path.exists(image_path):
            raise ValueError(f"Image not found: {image_path}")
            
        url = f"{self.base_url}/v1/encode"
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'message': message}
            
            try:
                response = requests.post(url, files=files, data=data, headers=self.headers)
                response.raise_for_status()
                result = response.json()
                
                # If output path is provided, download the result
                if output_path and 'download_url' in result:
                    self._download_image(result['download_url'], output_path)
                    result['output_path'] = output_path
                    
                return result
                
            except requests.exceptions.RequestException as e:
                raise Exception(f"API Request Failed: {str(e)}")

    def decode(self, image_path: str) -> Dict[str, Any]:
        """
        Extract message from an image via the API.
        
        Args:
            image_path: Path to watermarked image
            
        Returns:
            Dictionary with extracted message and confidence
        """
        if not os.path.exists(image_path):
            raise ValueError(f"Image not found: {image_path}")
            
        url = f"{self.base_url}/v1/decode"
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            
            try:
                response = requests.post(url, files=files, headers=self.headers)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                raise Exception(f"API Request Failed: {str(e)}")

    def _download_image(self, url: str, path: str):
        """Helper to download image from URL"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except Exception as e:
            print(f"Warning: Failed to download result image: {e}")

