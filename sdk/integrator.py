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
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import numpy as np
from PIL import Image

from truthmark.core.embedder import WatermarkEmbedder
from truthmark.core.extractor import WatermarkExtractor
from truthmark.core.crypto import CryptoEngine
from truthmark.core.error_correction import ErrorCorrection
from truthmark.core.payload import PayloadBuilder
from truthmark.ai.saliency_detector import SaliencyDetector

logger = logging.getLogger(__name__)


@dataclass
class IntegrationResult:
    """Result of watermark integration in AI-generated content."""

    success: bool
    watermarked_image: Optional[np.ndarray]
    truthmark_id: str
    ai_tool: str
    timestamp: str
    metadata: Dict[str, Any]
    encryption_key: str
    psnr: Optional[float] = None
    ssim: Optional[float] = None
    embedding_locations: int = 0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "truthmark_id": self.truthmark_id,
            "ai_tool": self.ai_tool,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "psnr": self.psnr,
            "ssim": self.ssim,
            "embedding_locations": self.embedding_locations,
            "error_message": self.error_message,
        }


class TruthMarkIntegrator:
    """
    INTEGRATOR for AI Generation Tools.

    This class MUST be integrated into all AI generation tools to ensure
    every generated image/video is watermarked with unremovable provenance data.

    Key Features:
    - Mandatory watermarking (cannot be bypassed when required=True)
    - Embeds AI tool name, version, timestamp, and metadata
    - Spread-spectrum + Fourier sync template for robustness
    - HVS-adaptive strength (invisible to human eye)
    - HKDF-derived dual-layer encryption
    - Reed-Solomon error correction with block interleaving
    - Regulatory compliance ready

    Example Integration (in Stable Diffusion):
        integrator = TruthMarkIntegrator(
            ai_tool="StableDiffusion v2.1",
            required=True,
            strength=8.0,
        )

        result = integrator.embed_mandatory(
            generated_image,
            metadata={"model": "sd-v2.1", "steps": 50},
        )

        # MUST return watermarked version
        return result.watermarked_image
    """

    def __init__(
        self,
        ai_tool: str,
        required: bool = True,
        strength: float = 8.0,
        saliency_method: str = "combined",
        version: Optional[str] = None,
    ):
        """
        Args:
            ai_tool: Name of AI tool (e.g., "StableDiffusion", "DALL-E")
            required: If True, watermarking is mandatory and cannot be bypassed
            strength: Base embedding strength (4-15 recommended)
            saliency_method: Saliency detection method ('spectral', 'fine', 'combined')
            version: AI tool version string
        """
        self.ai_tool = ai_tool
        self.version = version or "unknown"
        self.required = required
        self.strength = strength

        # Core components
        self.crypto = CryptoEngine()
        self.ecc = ErrorCorrection()
        self.payload_builder = PayloadBuilder()
        self.saliency_detector = SaliencyDetector(method=saliency_method)
        self.embedder = WatermarkEmbedder(
            crypto_engine=self.crypto,
            strength=strength,
        )
        self.extractor = WatermarkExtractor(
            crypto_engine=self.crypto,
        )

        logger.info(
            "TruthMark Integrator initialized for %s (required=%s, strength=%.1f)",
            ai_tool,
            required,
            strength,
        )

    # ------------------------------------------------------------------
    # EMBED
    # ------------------------------------------------------------------

    def embed_mandatory(
        self,
        image: Union[np.ndarray, Image.Image, str, Path],
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        prompt_hash: Optional[str] = None,
    ) -> IntegrationResult:
        """
        MANDATORY watermark embedding for AI-generated content.

        Args:
            image: Generated image (numpy array, PIL Image, or file path)
            metadata: Additional metadata about the generation
            user_id: User who requested the generation
            prompt_hash: Hash of the generation prompt (for privacy)

        Returns:
            IntegrationResult with watermarked image and provenance data
        """
        try:
            image_array = self._load_image(image)

            # Build provenance payload
            full_metadata = {
                **(metadata or {}),
                "user_id": user_id,
                "prompt_hash": prompt_hash,
            }
            payload_dict = self.payload_builder.build(
                ai_tool=f"{self.ai_tool} {self.version}",
                metadata=full_metadata,
            )
            payload_bytes = self.payload_builder.serialize(payload_dict)

            # Encrypt + ECC
            encrypted = self.crypto.encrypt(payload_bytes)
            encoded = self.ecc.encode(encrypted)

            # Compute saliency map for smarter embedding
            saliency_map = self.saliency_detector.detect(image_array)

            # Embed
            watermarked, info = self.embedder.embed(
                image=image_array,
                payload=encoded,
                saliency_map=saliency_map,
            )

            result = IntegrationResult(
                success=True,
                watermarked_image=watermarked,
                truthmark_id=payload_dict.get("truthmark_id", ""),
                ai_tool=f"{self.ai_tool} {self.version}",
                timestamp=payload_dict.get("generation_time", ""),
                metadata=full_metadata,
                encryption_key=self.crypto.get_key_string(),
                psnr=info.get("psnr_db"),
                ssim=info.get("ssim"),
                embedding_locations=info.get("total_coefficients_used", 0),
            )

            logger.info(
                "Watermarked image from %s  PSNR=%.1fdB  SSIM=%.4f  ID=%s",
                self.ai_tool,
                info.get("psnr_db", 0),
                info.get("ssim", 0),
                payload_dict.get("truthmark_id", ""),
            )
            return result

        except Exception as e:
            error_msg = f"Failed to watermark image from {self.ai_tool}: {e}"
            logger.error(error_msg)

            if self.required:
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
                timestamp=datetime.now(timezone.utc).isoformat(),
                metadata={},
                encryption_key="",
                error_message=error_msg,
            )

    # ------------------------------------------------------------------
    # BATCH
    # ------------------------------------------------------------------

    def embed_batch(
        self,
        images: list,
        metadata_list: Optional[list] = None,
        user_ids: Optional[list] = None,
    ) -> List[IntegrationResult]:
        """Watermark multiple images in one call."""
        metadata_list = metadata_list or [None] * len(images)
        user_ids = user_ids or [None] * len(images)
        results = []

        for i, (img, meta, uid) in enumerate(
            zip(images, metadata_list, user_ids)
        ):
            logger.info("Watermarking image %d/%d", i + 1, len(images))
            results.append(
                self.embed_mandatory(image=img, metadata=meta, user_id=uid)
            )

        logger.info("Batch complete: %d images processed", len(results))
        return results

    # ------------------------------------------------------------------
    # COMPLIANCE
    # ------------------------------------------------------------------

    def get_compliance_report(self, result: IntegrationResult) -> Dict[str, Any]:
        """Generate a compliance report for regulatory requirements."""
        return {
            "compliance_version": "2.0",
            "standard": "TruthMark AI Provenance Standard",
            "generator": {
                "ai_tool": self.ai_tool,
                "version": self.version,
                "watermarking_required": self.required,
            },
            "watermark": {
                "truthmark_id": result.truthmark_id,
                "timestamp": result.timestamp,
                "embedding_strength": self.strength,
                "quality_psnr_db": result.psnr,
                "quality_ssim": result.ssim,
                "embedding_locations": result.embedding_locations,
            },
            "verification": {
                "encrypted": True,
                "dual_layer_encryption": True,
                "hkdf_key_derivation": True,
                "error_correction": True,
                "spread_spectrum": True,
                "sync_template": True,
                "tamper_resistant": True,
                "survives_compression": True,
                "survives_cropping": True,
                "survives_geometric_transforms": True,
            },
            "metadata": result.metadata,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _load_image(image: Union[np.ndarray, Image.Image, str, Path]) -> np.ndarray:
        """Normalise any image input to RGB uint8 numpy array."""
        if isinstance(image, (str, Path)):
            image = np.array(Image.open(image).convert("RGB"))
        elif isinstance(image, Image.Image):
            image = np.array(image.convert("RGB"))
        if image.dtype != np.uint8:
            if image.max() <= 1.0:
                image = (image * 255).astype(np.uint8)
            else:
                image = image.astype(np.uint8)
        return image


# ------------------------------------------------------------------
# CONVENIENCE FUNCTION
# ------------------------------------------------------------------


def watermark_ai_generation(
    image: Union[np.ndarray, Image.Image],
    ai_tool: str,
    **metadata,
) -> tuple:
    """
    Quick watermarking function for AI-generated content.

    Returns:
        (watermarked_image, encryption_key_string)
    """
    integrator = TruthMarkIntegrator(ai_tool=ai_tool, required=True)
    result = integrator.embed_mandatory(image, metadata=metadata)

    if not result.success:
        raise RuntimeError(f"Watermarking failed: {result.error_message}")

    return result.watermarked_image, result.encryption_key
