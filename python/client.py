from typing import Optional, Dict, Any, Tuple
import numpy as np
import cv2
from truthmark.ai.neural import NeuralWatermarker
from truthmark.core.ledger import TruthChainLedger

class TruthMarkClient:
    """
    Simple SDK wrapper for TruthMark Core.
    Provides easy-to-use methods for embedding and extracting watermarks.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.watermarker = NeuralWatermarker(model_path=model_path)
        self.ledger = TruthChainLedger()

    def encode(self, image_path: str, message: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Embed a message into an image.
        
        Args:
            image_path: Path to input image
            message: Text message to embed
            output_path: Optional path to save result
            
        Returns:
            Dictionary with metadata and output path
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Embed
        payload = message.encode('utf-8')
        watermarked, meta = self.watermarker.embed(image_rgb, payload)
        
        # Save if requested
        if output_path:
            output_bgr = cv2.cvtColor(watermarked, cv2.COLOR_RGB2BGR)
            cv2.imwrite(output_path, output_bgr)
            
        return {
            "status": "success",
            "bits_embedded": meta.get("bits_embedded"),
            "psnr": meta.get("psnr_db"),
            "output_path": output_path
        }

    def decode(self, image_path: str) -> Dict[str, Any]:
        """
        Extract message from an image.
        
        Args:
            image_path: Path to watermarked image
            
        Returns:
            Dictionary with extracted message and confidence
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        payload, confidence = self.watermarker.extract(image_rgb)
        
        if payload:
            try:
                message = payload.decode('utf-8')
            except:
                message = str(payload)
                
            return {
                "found": True,
                "message": message,
                "confidence": confidence
            }
        else:
            return {
                "found": False,
                "message": None,
                "confidence": 0.0
            }
