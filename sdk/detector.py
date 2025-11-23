"""
TruthMark Detector - Unified SDK
Complete watermark detection with ALL features in ONE place
"""

import numpy as np
import cv2
from PIL import Image
from pathlib import Path
from typing import Union, Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import json

from ..core.crypto import CryptoEngine
from ..core.extractor import WatermarkExtractor
from ..core.payload import PayloadBuilder
from ..core.config import TruthMarkConfig, get_config


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
            result = [
                f"✓ Watermark detected (confidence: {self.confidence:.1%})"
            ]
            
            if self.payload:
                if self.copyright:
                    result.append(f"  Copyright: {self.copyright}")
                if self.author:
                    result.append(f"  Author: {self.author}")
                if self.ai_tool:
                    result.append(f"  AI Tool: {self.ai_tool}")
                if self.truthmark_id:
                    result.append(f"  TruthMark ID: {self.truthmark_id}")
                if self.timestamp:
                    result.append(f"  Timestamp: {self.timestamp}")
            
            if self.is_ai_generated:
                result.append(f"  ⚠️ AI Generated Content")
                if self.suggested_label:
                    result.append(f"  Label: {self.suggested_label}")
            
            return "\n".join(result)
        else:
            return f"✗ No watermark detected: {self.error_message or 'Unknown reason'}"


class TruthMarkDetector:
    """
    Unified TruthMark watermark detector with ALL features.
    
    Features:
    - Basic watermark detection
    - Social media platform integration
    - AI content detection
    - Batch processing
    - Multiple extraction methods
    - Copyright verification
    - Legal compliance mode
    
    Modes:
    - standard: Basic detection
    - social_media: For Instagram, TikTok, X, Facebook
    - copyright: For copyright enforcement (Getty, Adobe, etc.)
    - ai_compliance: For EU AI Act compliance
    
    Example:
        >>> # Simple detection
        >>> detector = TruthMarkDetector(key)
        >>> result = detector.detect("watermarked.jpg")
        
        >>> # Social media usage
        >>> detector = TruthMarkDetector(mode="social_media")
        >>> result = detector.scan_upload(uploaded_image)
        >>> if result.is_ai_generated:
        >>>     post.add_label(result.suggested_label)
        
        >>> # Enterprise usage
        >>> detector = TruthMarkDetector(
        >>>     mode="copyright",
        >>>     config=TruthMarkConfig.from_preset("enterprise")
        >>> )
        >>> result = detector.detect("suspicious_image.jpg")
    """
    
    def __init__(
        self,
        key: Optional[str] = None,
        mode: str = "standard",
        config: Optional[TruthMarkConfig] = None,
        universal: bool = False,  # Backward compatibility
    ):
        """
        Initialize TruthMark detector.
        
        Args:
            key: Decryption key (base64). None = try universal detection
            mode: Detection mode ("standard", "social_media", "copyright", "ai_compliance")
            config: TruthMarkConfig object. None = use balanced preset
            universal: Deprecated. Use mode="social_media" instead
        """
        # Handle universal mode (deprecated)
        if universal and mode == "standard":
            mode = "social_media"
        
        self.mode = mode
        
        # Use provided config or create default
        if config is None:
            config = get_config("balanced")
        self.config = config
        
        # Initialize crypto engine if key provided
        self.crypto = None
        self.key = key
        if key:
            self.crypto = CryptoEngine(key)
    
    def detect(
        self,
        input_path: Union[str, Path, np.ndarray],
        key: Optional[str] = None
    ) -> DetectResult:
        """
        Detect watermark in image.
        
        Args:
            input_path: Path to image or numpy array
            key: Override decryption key for this detection
            
        Returns:
            DetectResult with all information
        """
        try:
            # Load image
            if isinstance(input_path, np.ndarray):
                img_array = input_path
            else:
                input_path = Path(input_path)
                img = Image.open(input_path)
                img_array = np.array(img.convert('RGB'))
            
            # Use provided key or instance key
            crypto = self.crypto
            if key and key != self.key:
                crypto = CryptoEngine(key)
            
            if not crypto:
                return DetectResult(
                    detected=False,
                    error_message="No decryption key provided. Cannot detect watermark without key.",
                    confidence=0.0
                )
            
            # Try to detect watermark by trying different payload sizes
            # We'll use the same deterministic location algorithm as the embedder
            from ..core.embedder import WatermarkEmbedder
            
            height, width = img_array.shape[:2]
            
            # Try common payload sizes (in bytes)
            # We try extracting different total embedded sizes (encrypted + hash)
            # Start with fine-grained search from small to large sizes
            embedded_sizes_to_try = list(range(100, 500, 4)) + list(range(500, 1000, 20)) + list(range(1000, 2000, 50))
            
            for embedded_size_bytes in embedded_sizes_to_try:
                bits_needed = embedded_size_bytes * 8
                
                # Check if image is large enough
                blocks_h = height // 8
                blocks_w = width // 8
                max_bits = blocks_h * blocks_w * 15  # 15 mid-freq coefficients per block
                
                if bits_needed > max_bits:
                    continue
                
                try:
                    # Recompute embedding locations using same algorithm
                    embedding_locations = WatermarkEmbedder._select_embedding_locations(
                        height, width, bits_needed, saliency_map=None, block_size=8
                    )
                    
                    # Extract raw bits (without ECC or decryption)
                    ycrcb = cv2.cvtColor(img_array, cv2.COLOR_RGB2YCrCb)
                    y_channel = ycrcb[:, :, 0].astype(np.float32)
                    
                    # Extract bits from DCT coefficients
                    extracted_bits = self._extract_bits_from_dct(y_channel, embedding_locations[:bits_needed])
                    
                    # Convert bits to bytes
                    extracted_data = WatermarkExtractor._bits_to_bytes(extracted_bits)
                    
                    # Try to decrypt (encrypted_data is last N bytes, hash is last 32)
                    if len(extracted_data) < 32:
                        continue  # Too short to contain hash
                    
                    encrypted_payload = extracted_data[:-32]
                    integrity_hash = extracted_data[-32:]
                    
                    try:
                        # Decrypt first
                        decrypted = crypto.decrypt(encrypted_payload, integrity_hash)
                        
                        # Apply error correction AFTER decryption
                        # (matches embedder flow: ECC → Encrypt, so decrypt → ECC decode)
                        if self.config.use_error_correction:
                            from ..core.error_correction import ErrorCorrection
                            ecc = ErrorCorrection(ecc_symbols=self.config.get_ecc_symbols())
                            decrypted, errors_corrected = ecc.decode(decrypted)
                        
                        # Try to parse as JSON
                        payload_json = decrypted.decode('utf-8')
                        payload = json.loads(payload_json)
                        
                        # Success! We found the watermark
                        extract_info = {
                            "bits_extracted": bits_needed,
                            "payload_size": len(decrypted),
                            "confidence": 1.0
                        }
                        return self._build_result(payload, extract_info)
                        
                    except Exception:
                        # Decryption/ECC/JSON failed, try next size
                        continue
                        
                except Exception:
                    # Extraction failed, try next size
                    continue
            
            # No watermark detected with any payload size
            return DetectResult(
                detected=False,
                error_message="No watermark detected or decryption failed",
                confidence=0.0,
                payload=None,
                extraction_info=None
            )
            
            if extracted_payload is None:
                return DetectResult(
                    detected=False,
                    error_message="No watermark found or decryption failed"
                )
            
            # Apply error correction if enabled
            if self.config.use_error_correction:
                from ..core.error_correction import ErrorCorrection
                ecc = ErrorCorrection(ecc_symbols=self.config.get_ecc_symbols())
                try:
                    extracted_payload = ecc.decode(extracted_payload)
                except Exception as e:
                    return DetectResult(
                        detected=False,
                        error_message=f"Error correction failed: {e}"
                    )
            
            # Decrypt payload
            if crypto:
                try:
                    decrypted = crypto.decrypt(extracted_payload)
                    payload_json = decrypted.decode('utf-8')
                    payload = json.loads(payload_json)
                except Exception as e:
                    return DetectResult(
                        detected=False,
                        error_message=f"Decryption failed: {e}"
                    )
            else:
                # No key provided - raw payload
                try:
                    payload_json = extracted_payload.decode('utf-8')
                    payload = json.loads(payload_json)
                except Exception:
                    return DetectResult(
                        detected=False,
                        error_message="No decryption key provided"
                    )
            
            # Build result based on mode
            return self._build_result(payload, extract_info)
            
        except Exception as e:
            return DetectResult(
                detected=False,
                error_message=str(e)
            )
    
    def _build_result(
        self,
        payload: Dict[str, Any],
        extract_info: Dict[str, Any]
    ) -> DetectResult:
        """Build detection result based on mode and payload."""
        
        # Extract common fields
        copyright_text = payload.get("copyright")
        author = payload.get("author")
        ai_tool = payload.get("ai_tool")
        ai_generated = payload.get("ai_generated", False)
        truthmark_id = payload.get("truthmark_id")
        timestamp = payload.get("timestamp")
        
        # Calculate confidence (0.0-1.0)
        confidence = extract_info.get("confidence", 0.8)
        
        # Build result
        result = DetectResult(
            detected=True,
            confidence=confidence,
            payload=payload,
            extraction_info=extract_info,
            copyright=copyright_text,
            author=author,
            ai_tool=ai_tool,
            ai_generated=ai_generated,
            truthmark_id=truthmark_id,
            timestamp=timestamp
        )
        
        # Mode-specific processing
        if self.mode == "social_media":
            result.is_ai_generated = ai_generated
            result.requires_label = ai_generated
            
            if ai_generated and ai_tool:
                result.suggested_label = f"⚠️ AI Generated by {ai_tool}"
            elif ai_generated:
                result.suggested_label = "⚠️ AI Generated Content"
        
        elif self.mode == "ai_compliance":
            # EU AI Act compliance
            result.is_ai_generated = ai_generated
            eu_compliance = payload.get("ai_compliance", {})
            result.requires_label = eu_compliance.get("synthetic_content", False)
        
        elif self.mode == "copyright":
            # Copyright enforcement mode
            # Additional verification can be added here
            pass
        
        return result
    
    def scan_upload(
        self,
        image: Union[str, Path, np.ndarray],
        key: Optional[str] = None
    ) -> DetectResult:
        """
        Scan uploaded image (for social media platforms).
        
        This is the main method social media platforms should use
        in their upload pipeline.
        
        Args:
            image: Uploaded image (path or array)
            key: Decryption key. None = try universal detection
            
        Returns:
            DetectResult with is_ai_generated and suggested_label
            
        Example:
            >>> detector = TruthMarkDetector(mode="social_media")
            >>> result = detector.scan_upload(uploaded_file)
            >>> 
            >>> if result.is_ai_generated:
            >>>     # Auto-label the post
            >>>     post.add_label(result.suggested_label)
            >>>     post.mark_as_synthetic_media()
        """
        return self.detect(image, key)
    
    def verify_copyright(
        self,
        image: Union[str, Path, np.ndarray],
        expected_owner: str,
        key: str
    ) -> Dict[str, Any]:
        """
        Verify copyright ownership.
        
        Args:
            image: Image to verify
            expected_owner: Expected copyright owner
            key: Decryption key
            
        Returns:
            Verification result with match status
            
        Example:
            >>> detector = TruthMarkDetector(mode="copyright")
            >>> result = detector.verify_copyright(
            >>>     "image.jpg",
            >>>     expected_owner="Getty Images",
            >>>     key=decryption_key
            >>> )
            >>> if result["verified"]:
            >>>     print("Copyright verified!")
        """
        result = self.detect(image, key)
        
        if not result.detected:
            return {
                "verified": False,
                "reason": "No watermark detected",
                "confidence": 0.0
            }
        
        # Check owner match
        actual_owner = ""
        if result.payload:
            actual_owner = (
                result.payload.get("owner") or
                result.payload.get("author") or
                result.payload.get("copyright", "")
            )
        
        owner_match = expected_owner.lower() in actual_owner.lower()
        
        return {
            "verified": owner_match,
            "expected_owner": expected_owner,
            "actual_owner": actual_owner,
            "confidence": result.confidence,
            "truthmark_id": result.truthmark_id,
            "timestamp": result.timestamp,
            "full_payload": result.payload
        }
    
    def detect_batch(
        self,
        image_paths: List[Union[str, Path]],
        keys: Optional[Union[str, List[str]]] = None
    ) -> List[DetectResult]:
        """
        Batch detect watermarks in multiple images.
        
        Args:
            image_paths: List of image paths
            keys: Single key for all, list of keys, or None
            
        Returns:
            List of DetectResult for each image
        """
        results = []
        
        # Handle single key for all images
        keys_list: List[Optional[str]] = []
        if isinstance(keys, str):
            keys_list = [keys] * len(image_paths)
        elif keys is None:
            keys_list = [None] * len(image_paths)
        else:
            keys_list = [k for k in keys]  # Convert List[str] to List[Optional[str]]
        
        for img_path, key in zip(image_paths, keys_list):
            result = self.detect(img_path, key)
            results.append(result)
        
        return results
    
    def check_ai_compliance(
        self,
        image: Union[str, Path, np.ndarray],
        key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check EU AI Act compliance.
        
        Args:
            image: Image to check
            key: Decryption key
            
        Returns:
            Compliance status
            
        Example:
            >>> detector = TruthMarkDetector(mode="ai_compliance")
            >>> compliance = detector.check_ai_compliance("ai_image.jpg", key)
            >>> if compliance["compliant"]:
            >>>     print("✓ EU AI Act compliant")
        """
        result = self.detect(image, key)
        
        if not result.detected:
            return {
                "compliant": False,
                "reason": "No AI watermark detected",
                "ai_generated": False
            }
        
        ai_compliance = result.payload.get("ai_compliance", {}) if result.payload else {}
        
        return {
            "compliant": ai_compliance.get("eu_ai_act", False),
            "ai_generated": result.ai_generated,
            "ai_tool": result.ai_tool,
            "model_provider": ai_compliance.get("model_provider"),
            "synthetic_content": ai_compliance.get("synthetic_content", False),
            "timestamp": result.timestamp,
            "full_payload": result.payload
        }
    
    def _extract_bits_from_dct(
        self,
        channel: np.ndarray,
        locations: List[Tuple[int, int, int, int]]
    ) -> List[int]:
        """
        Extract bits from DCT coefficients.
        
        Args:
            channel: Image channel (Y channel)
            locations: List of embedding locations (block_y, block_x, coef_y, coef_x)
            
        Returns:
            List of extracted bits (0 or 1)
        """
        BLOCK_SIZE = 8
        bits = []
        
        for block_y, block_x, coef_y, coef_x in locations:
            # Extract DCT block
            y_start = block_y * BLOCK_SIZE
            x_start = block_x * BLOCK_SIZE
            block = channel[y_start:y_start + BLOCK_SIZE,
                           x_start:x_start + BLOCK_SIZE]
            
            # Apply DCT
            dct_block = cv2.dct(block)
            
            # Extract bit based on coefficient value
            # Positive modification -> bit 1, negative -> bit 0
            coefficient = dct_block[coef_y, coef_x]
            bit = 1 if coefficient > 0 else 0
            bits.append(bit)
        
        return bits


# Convenience aliases
SocialDetector = TruthMarkDetector  # Backward compatibility
CopyrightDetector = TruthMarkDetector
AIComplianceDetector = TruthMarkDetector
