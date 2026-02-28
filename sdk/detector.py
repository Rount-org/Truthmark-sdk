"""
TruthMark Detector - Unified SDK
Complete watermark detection with sync template, spread-spectrum extraction,
and mode-based result building (social media, copyright, AI compliance).
"""

import numpy as np
import cv2
from PIL import Image
from pathlib import Path
from typing import Union, Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import json
import logging

from truthmark.core.crypto import CryptoEngine
from truthmark.core.extractor import WatermarkExtractor
from truthmark.core.error_correction import ErrorCorrection
from truthmark.core.payload import PayloadBuilder
from truthmark.core.config import TruthMarkConfig, get_config

logger = logging.getLogger(__name__)


@dataclass
class DetectResult:
    """Complete detection result with all information."""

    detected: bool
    confidence: float = 0.0
    payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    extraction_info: Optional[Dict[str, Any]] = None

    # Payload fields (convenience accessors)
    copyright: Optional[str] = None
    author: Optional[str] = None
    ai_tool: Optional[str] = None
    ai_generated: bool = False
    truthmark_id: Optional[str] = None
    timestamp: Optional[str] = None

    # Social media specific
    is_ai_generated: bool = False
    requires_label: bool = False
    suggested_label: Optional[str] = None

    def __str__(self) -> str:
        if self.detected:
            parts = [f"Watermark detected (confidence: {self.confidence:.1%})"]
            if self.copyright:
                parts.append(f"  Copyright: {self.copyright}")
            if self.author:
                parts.append(f"  Author: {self.author}")
            if self.ai_tool:
                parts.append(f"  AI Tool: {self.ai_tool}")
            if self.truthmark_id:
                parts.append(f"  TruthMark ID: {self.truthmark_id}")
            if self.timestamp:
                parts.append(f"  Timestamp: {self.timestamp}")
            if self.is_ai_generated:
                parts.append("  AI Generated Content")
                if self.suggested_label:
                    parts.append(f"  Label: {self.suggested_label}")
            return "\n".join(parts)
        return f"No watermark detected: {self.error_message or 'Unknown reason'}"


class TruthMarkDetector:
    """
    Unified TruthMark watermark detector.

    Uses the new spread-spectrum extractor with sync template detection.
    No longer brute-forces payload sizes — reads the embedded length header.

    Modes:
      - standard: Basic detection
      - social_media: For platform upload scanning
      - copyright: For ownership enforcement
      - ai_compliance: For EU AI Act compliance
    """

    def __init__(
        self,
        key: Optional[str] = None,
        mode: str = "standard",
        config: Optional[TruthMarkConfig] = None,
        universal: bool = False,
    ):
        if universal and mode == "standard":
            mode = "social_media"

        self.mode = mode
        self.config = config or get_config("balanced")
        self.key = key
        self.crypto = CryptoEngine(key) if key else None

    # ------------------------------------------------------------------
    # PRIMARY DETECTION
    # ------------------------------------------------------------------

    def detect(
        self,
        input_path: Union[str, Path, np.ndarray],
        key: Optional[str] = None,
    ) -> DetectResult:
        """
        Detect watermark in an image.

        Args:
            input_path: Path to image file or numpy RGB array.
            key: Override decryption key for this detection.

        Returns:
            DetectResult with detection status, confidence, and payload.
        """
        try:
            img_array = self._load_image(input_path)

            # Resolve crypto engine
            crypto = self.crypto
            if key and key != self.key:
                crypto = CryptoEngine(key)

            # Extract using the new autonomous extractor
            extractor = WatermarkExtractor(crypto_engine=crypto)
            raw_bytes, info = extractor.extract(img_array)

            if not info.get("sync_detected", False) or not raw_bytes:
                return DetectResult(
                    detected=False,
                    confidence=info.get("confidence", 0.0),
                    error_message=info.get("error", "No watermark detected"),
                    extraction_info=info,
                )

            # Attempt ECC decode
            ecc = ErrorCorrection(
                ecc_symbols=self.config.get_ecc_symbols()
                if hasattr(self.config, "get_ecc_symbols")
                else 30
            )
            try:
                decoded, _ = ecc.decode(raw_bytes)
            except ValueError:
                decoded = raw_bytes
                errors_corrected = -1

            # Attempt decryption
            payload = None
            if crypto:
                try:
                    decrypted = crypto.decrypt(decoded)
                    payload = json.loads(decrypted.decode("utf-8"))
                except Exception:
                    pass

            # If decryption failed or no key, try raw JSON parse
            if payload is None:
                try:
                    payload = json.loads(decoded.decode("utf-8"))
                except Exception:
                    pass

            if payload is None:
                return DetectResult(
                    detected=info.get("sync_detected", False),
                    confidence=info.get("confidence", 0.0),
                    error_message="Watermark detected but payload could not be decoded",
                    extraction_info=info,
                )

            return self._build_result(payload, info)

        except Exception as e:
            logger.exception("Detection error")
            return DetectResult(detected=False, error_message=str(e))

    # ------------------------------------------------------------------
    # MODE-SPECIFIC SCANNING
    # ------------------------------------------------------------------

    def scan_upload(
        self,
        image: Union[str, Path, np.ndarray],
        key: Optional[str] = None,
    ) -> DetectResult:
        """Scan an uploaded image for watermarks (social media platforms)."""
        return self.detect(image, key)

    def verify_copyright(
        self,
        image: Union[str, Path, np.ndarray],
        expected_owner: str,
        key: str,
    ) -> Dict[str, Any]:
        """Verify copyright ownership against expected owner."""
        result = self.detect(image, key)
        if not result.detected:
            return {
                "verified": False,
                "reason": "No watermark detected",
                "confidence": 0.0,
            }
        actual_owner = ""
        if result.payload:
            actual_owner = (
                result.payload.get("owner")
                or result.payload.get("author")
                or result.payload.get("copyright", "")
            )
        owner_match = expected_owner.lower() in actual_owner.lower()
        return {
            "verified": owner_match,
            "expected_owner": expected_owner,
            "actual_owner": actual_owner,
            "confidence": result.confidence,
            "truthmark_id": result.truthmark_id,
            "timestamp": result.timestamp,
            "full_payload": result.payload,
        }

    def detect_batch(
        self,
        image_paths: List[Union[str, Path]],
        keys: Optional[Union[str, List[str]]] = None,
    ) -> List[DetectResult]:
        """Batch detect watermarks in multiple images."""
        if isinstance(keys, str):
            keys_list: List[Optional[str]] = [keys] * len(image_paths)
        elif keys is None:
            keys_list = [None] * len(image_paths)
        else:
            keys_list = list(keys)

        return [self.detect(p, k) for p, k in zip(image_paths, keys_list)]

    def check_ai_compliance(
        self,
        image: Union[str, Path, np.ndarray],
        key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Check EU AI Act compliance."""
        result = self.detect(image, key)
        if not result.detected:
            return {
                "compliant": False,
                "reason": "No AI watermark detected",
                "ai_generated": False,
            }
        ai_compliance = (
            result.payload.get("ai_compliance", {}) if result.payload else {}
        )
        return {
            "compliant": ai_compliance.get("eu_ai_act", False),
            "ai_generated": result.ai_generated,
            "ai_tool": result.ai_tool,
            "model_provider": ai_compliance.get("model_provider"),
            "synthetic_content": ai_compliance.get("synthetic_content", False),
            "timestamp": result.timestamp,
            "full_payload": result.payload,
        }

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------

    def _build_result(
        self, payload: Dict[str, Any], extract_info: Dict[str, Any]
    ) -> DetectResult:
        """Build detection result based on mode and payload."""
        ai_tool = payload.get("ai_tool")
        ai_generated = payload.get("ai_generated", bool(ai_tool))

        result = DetectResult(
            detected=True,
            confidence=extract_info.get("confidence", 0.8),
            payload=payload,
            extraction_info=extract_info,
            copyright=payload.get("copyright"),
            author=payload.get("author"),
            ai_tool=ai_tool,
            ai_generated=ai_generated,
            truthmark_id=payload.get("truthmark_id"),
            timestamp=payload.get("generation_time") or payload.get("timestamp"),
        )

        if self.mode == "social_media":
            result.is_ai_generated = ai_generated
            result.requires_label = ai_generated
            if ai_generated and ai_tool:
                result.suggested_label = f"AI Generated by {ai_tool}"
            elif ai_generated:
                result.suggested_label = "AI Generated Content"

        elif self.mode == "ai_compliance":
            result.is_ai_generated = ai_generated
            eu_compliance = payload.get("ai_compliance", {})
            result.requires_label = eu_compliance.get("synthetic_content", False)

        return result

    @staticmethod
    def _load_image(
        input_path: Union[str, Path, np.ndarray],
    ) -> np.ndarray:
        if isinstance(input_path, np.ndarray):
            img = input_path
        else:
            img = np.array(Image.open(input_path).convert("RGB"))
        if img.dtype != np.uint8:
            if img.max() <= 1.0:
                img = (img * 255).astype(np.uint8)
            else:
                img = img.astype(np.uint8)
        return img


# Backward-compatible aliases
SocialDetector = TruthMarkDetector
CopyrightDetector = TruthMarkDetector
AIComplianceDetector = TruthMarkDetector
