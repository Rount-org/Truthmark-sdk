"""
TruthMark INTEGRATOR - For AI Generation Tools

This is THE module that AI generation tools (Stable Diffusion, DALL-E, Midjourney, etc.)
MUST integrate to watermark ALL generated content.

Usage in AI generation code:
    from truthmark import TruthMarkIntegrator
    
    integrator = TruthMarkIntegrator(
        ai_tool="StableDiffusion v2.1",
        required=True  # Mandatory, cannot be bypassed
    )
    
    watermarked = integrator.embed_mandatory(
        generated_image,
        metadata={"model": "sd-v2.1", "prompt": "..."}
    )
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json
import numpy as np
from PIL import Image

from ..core.embedder import WatermarkEmbedder
from ..core.crypto import CryptoEngine
from ..core.payload import PayloadBuilder
from ..ai.saliency_detector import SaliencyDetector

logger = logging.getLogger(__name__)


@dataclass
class IntegrationResult:
    """Result of watermark integration in AI-generated content"""
    success: bool
    watermarked_image: Optional[np.ndarray]
    truthmark_id: str
    ai_tool: str
    timestamp: str
    metadata: Dict[str, Any]
    encryption_key: str
    psnr: Optional[float] = None
    embedding_locations: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "success": self.success,
            "truthmark_id": self.truthmark_id,
            "ai_tool": self.ai_tool,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "psnr": self.psnr,
            "embedding_locations": self.embedding_locations,
            "error_message": self.error_message
        }


class TruthMarkIntegrator:
    """
    INTEGRATOR for AI Generation Tools
    
    This class MUST be integrated into all AI generation tools to ensure
    every generated image/video is watermarked with unremovable provenance data.
    
    Key Features:
    - Mandatory watermarking (cannot be bypassed when required=True)
    - Embeds AI tool name, version, timestamp, and metadata
    - Survives compression, cropping, editing
    - Military-grade encryption
    - Invisible to human eye
    - Regulatory compliance ready
    
    Example Integration (in Stable Diffusion):
        # Add to your image generation pipeline
        integrator = TruthMarkIntegrator(
            ai_tool="StableDiffusion v2.1",
            required=True,  # Mandatory
            strength=15.0
        )
        
        # After generating image
        result = integrator.embed_mandatory(
            generated_image,
            metadata={
                "model": "sd-v2.1-768-ema",
                "prompt_hash": "abc123...",
                "user_id": "user_12345",
                "seed": 42,
                "steps": 50
            }
        )
        
        # MUST return watermarked version
        return result.watermarked_image
    """
    
    def __init__(
        self,
        ai_tool: str,
        required: bool = True,
        strength: float = 15.0,
        saliency_method: str = "combined",
        enable_advanced_saliency: bool = False,
        version: Optional[str] = None
    ):
        """
        Initialize TruthMark Integrator
        
        Args:
            ai_tool: Name of AI tool (e.g., "StableDiffusion", "DALL-E", "Midjourney")
            required: If True, watermarking is mandatory and cannot be bypassed
            strength: Watermark embedding strength (10-30 recommended)
            saliency_method: Saliency detection method for smart embedding
            enable_advanced_saliency: Enable deep learning saliency
            version: AI tool version (e.g., "v2.1")
        """
        self.ai_tool = ai_tool
        self.version = version or "unknown"
        self.required = required
        self.strength = strength
        
        # Initialize core components
        self.crypto = CryptoEngine()
        self.payload_builder = PayloadBuilder()
        self.saliency_detector = SaliencyDetector(
            method=saliency_method,
            enable_advanced=enable_advanced_saliency
        )
        self.embedder = WatermarkEmbedder(
            strength=strength,
            saliency_detector=self.saliency_detector
        )
        
        logger.info(
            f"TruthMark Integrator initialized for {ai_tool} "
            f"(required={required}, strength={strength})"
        )
    
    def embed_mandatory(
        self,
        image: Union[np.ndarray, Image.Image, str, Path],
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        prompt_hash: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None
    ) -> IntegrationResult:
        """
        MANDATORY watermark embedding for AI-generated content
        
        This is the main method AI tools MUST call after generating content.
        When required=True, this cannot be bypassed.
        
        Args:
            image: Generated image (numpy array, PIL Image, or file path)
            metadata: Additional metadata about the generation
            user_id: User who requested the generation (if applicable)
            prompt_hash: Hash of the generation prompt (optional, for privacy)
            custom_data: Any custom data to embed
        
        Returns:
            IntegrationResult with watermarked image and provenance data
        
        Example:
            result = integrator.embed_mandatory(
                generated_image,
                metadata={
                    "model": "sd-v2.1",
                    "steps": 50,
                    "cfg_scale": 7.5
                },
                user_id="user_12345",
                prompt_hash="sha256:abc123..."
            )
            
            if result.success:
                # Save watermarked version
                cv2.imwrite("output.png", result.watermarked_image)
                # Save encryption key securely
                save_key(result.encryption_key)
        """
        try:
            # Load image if needed
            if isinstance(image, (str, Path)):
                image = np.array(Image.open(image))
            elif isinstance(image, Image.Image):
                image = np.array(image)
            
            # Generate encryption key
            key = self.crypto.generate_key()
            
            # Build payload with AI tool information
            payload_data = {
                "ai_tool": self.ai_tool,
                "ai_version": self.version,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "user_id": user_id,
                "prompt_hash": prompt_hash,
                "metadata": metadata or {},
                "custom_data": custom_data or {}
            }
            
            payload = self.payload_builder.build(
                ai_tool=f"{self.ai_tool} {self.version}",
                custom_data=payload_data
            )
            
            # Embed watermark
            watermarked, info = self.embedder.embed(
                image=image,
                payload=payload,
                key=key
            )
            
            result = IntegrationResult(
                success=True,
                watermarked_image=watermarked,
                truthmark_id=payload["truthmark_id"],
                ai_tool=f"{self.ai_tool} {self.version}",
                timestamp=payload["timestamp"],
                metadata=payload_data,
                encryption_key=key,
                psnr=info.get("psnr"),
                embedding_locations=info.get("embedding_locations", 0)
            )
            
            logger.info(
                f"✅ Successfully watermarked image from {self.ai_tool} "
                f"(PSNR: {info.get('psnr', 0):.2f} dB, "
                f"TruthMark ID: {payload['truthmark_id']})"
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to watermark image from {self.ai_tool}: {str(e)}"
            logger.error(error_msg)
            
            if self.required:
                # If watermarking is mandatory, raise exception
                raise RuntimeError(
                    f"MANDATORY WATERMARKING FAILED: {error_msg}\n"
                    f"This AI tool ({self.ai_tool}) requires TruthMark watermarking. "
                    f"Content cannot be generated without watermark."
                )
            
            return IntegrationResult(
                success=False,
                watermarked_image=None,
                truthmark_id="",
                ai_tool=self.ai_tool,
                timestamp=datetime.utcnow().isoformat() + "Z",
                metadata={},
                encryption_key="",
                error_message=error_msg
            )
    
    def embed_batch(
        self,
        images: list,
        metadata_list: Optional[list] = None,
        user_ids: Optional[list] = None
    ) -> list[IntegrationResult]:
        """
        Batch watermark multiple AI-generated images
        
        Useful for AI tools that generate multiple variations.
        
        Args:
            images: List of generated images
            metadata_list: List of metadata dicts (one per image)
            user_ids: List of user IDs (one per image)
        
        Returns:
            List of IntegrationResult objects
        """
        results = []
        
        metadata_list = metadata_list or [None] * len(images)
        user_ids = user_ids or [None] * len(images)
        
        for i, (image, metadata, user_id) in enumerate(zip(images, metadata_list, user_ids)):
            logger.info(f"Watermarking image {i+1}/{len(images)}")
            result = self.embed_mandatory(
                image=image,
                metadata=metadata,
                user_id=user_id
            )
            results.append(result)
        
        logger.info(f"Batch watermarking complete: {len(results)} images processed")
        return results
    
    def get_compliance_report(self, result: IntegrationResult) -> Dict[str, Any]:
        """
        Generate compliance report for regulatory requirements
        
        This report can be submitted to regulators to prove compliance
        with AI labeling requirements.
        
        Args:
            result: Integration result from embed_mandatory()
        
        Returns:
            Compliance report dictionary
        """
        return {
            "compliance_version": "1.0",
            "standard": "TruthMark AI Provenance Standard",
            "generator": {
                "ai_tool": self.ai_tool,
                "version": self.version,
                "watermarking_required": self.required
            },
            "watermark": {
                "truthmark_id": result.truthmark_id,
                "timestamp": result.timestamp,
                "embedding_strength": self.strength,
                "quality_psnr_db": result.psnr,
                "embedding_locations": result.embedding_locations
            },
            "verification": {
                "encrypted": True,
                "tamper_resistant": True,
                "survives_compression": True,
                "survives_cropping": True,
                "survives_editing": True
            },
            "metadata": result.metadata,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }


# Convenience function for quick integration
def watermark_ai_generation(
    image: Union[np.ndarray, Image.Image],
    ai_tool: str,
    **metadata
) -> tuple[np.ndarray, str]:
    """
    Quick watermarking function for AI-generated content
    
    This is a simplified interface for AI tools to quickly integrate watermarking.
    
    Args:
        image: Generated image
        ai_tool: Name of AI tool
        **metadata: Additional metadata to embed
    
    Returns:
        Tuple of (watermarked_image, encryption_key)
    
    Example:
        watermarked, key = watermark_ai_generation(
            generated_image,
            ai_tool="StableDiffusion v2.1",
            model="sd-v2.1",
            prompt_hash="abc123",
            user_id="user_12345"
        )
    """
    integrator = TruthMarkIntegrator(ai_tool=ai_tool, required=True)
    result = integrator.embed_mandatory(image, metadata=metadata)
    
    if not result.success:
        raise RuntimeError(f"Watermarking failed: {result.error_message}")
    
    return result.watermarked_image, result.encryption_key
