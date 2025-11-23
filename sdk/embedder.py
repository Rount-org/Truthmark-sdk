"""
TruthMark Embedder - Unified SDK
Complete watermark embedding with ALL features in ONE place
"""

import os
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Union, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import json

from ..core.crypto import CryptoEngine
from ..core.embedder import WatermarkEmbedder
from ..core.payload import PayloadBuilder
from ..core.config import TruthMarkConfig, get_config
from ..ai.saliency_detector import SaliencyDetector


@dataclass
class EmbedResult:
    """Complete embedding result with all information."""
    success: bool
    key: str
    output_path: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    embedding_info: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    image: Optional[np.ndarray] = None
    
    # Format preservation info
    format_preserved: bool = False
    size_match: float = 0.0  # Ratio of output/input size
    original_format: Optional[str] = None
    output_format: Optional[str] = None
    original_size: Optional[int] = None
    output_size: Optional[int] = None
    
    def __str__(self) -> str:
        if self.success:
            psnr = self.embedding_info.get('psnr_db', 0) if self.embedding_info else 0
            bits = self.embedding_info.get('bits_embedded', 0) if self.embedding_info else 0
            
            result = [
                "✓ Watermark embedded successfully",
                f"  Encryption Key: {self.key}",
                f"  Output: {self.output_path}",
                f"  PSNR: {psnr:.2f} dB",
                f"  Bits Embedded: {bits}"
            ]
            
            if self.format_preserved:
                result.append(f"  Format: {self.original_format} → {self.output_format} ✓")
            if self.size_match > 0:
                size_diff = abs(1.0 - self.size_match) * 100
                result.append(f"  Size Match: {self.size_match:.3f} (±{size_diff:.1f}%)")
            
            return "\n".join(result)
        else:
            return f"✗ Embedding failed: {self.error_message}"


class TruthMarkEmbedder:
    """
    Unified TruthMark watermark embedder with ALL features.
    
    Features:
    - Basic watermarking
    - Format preservation (JPG→JPG, PNG→PNG)
    - Size matching (±1-5%)
    - AI-powered saliency detection
    - Adaptive strength for target PSNR
    - Batch processing
    - Multiple embedding domains (DCT, DWT, SVD, Hybrid)
    - Error correction (Reed-Solomon)
    - Legal compliance mode
    - EU AI Act compliance
    
    Example:
        >>> # Simple usage (auto preset)
        >>> embedder = TruthMarkEmbedder()
        >>> result = embedder.embed("image.jpg", copyright_info)
        
        >>> # With custom config
        >>> config = TruthMarkConfig.from_preset("high_quality")
        >>> embedder = TruthMarkEmbedder(config=config)
        >>> result = embedder.embed("image.jpg", copyright_info)
        
        >>> # Enterprise usage
        >>> config = TruthMarkConfig.from_preset("enterprise")
        >>> embedder = TruthMarkEmbedder(config=config)
        >>> for image in millions_of_images:
        >>>     result = embedder.embed(image, copyright_info)
    """
    
    def __init__(
        self,
        key: Optional[str] = None,
        config: Optional[TruthMarkConfig] = None,
        # Backward compatibility - deprecated
        strength: Optional[float] = None,
        target_psnr: Optional[float] = None,
        use_ai_saliency: Optional[bool] = None,
    ):
        """
        Initialize TruthMark embedder.
        
        Args:
            key: Encryption key (base64). None = auto-generate
            config: TruthMarkConfig object. None = use balanced preset
            
            # Deprecated parameters (use config instead):
            strength: Embedding strength (use config.strength)
            target_psnr: Target PSNR (use config.target_psnr)
            use_ai_saliency: Use AI (use config.use_ai_saliency)
        """
        # Use provided config or create default
        if config is None:
            config = get_config("balanced")
        
        # Backward compatibility - override config if legacy params provided
        if strength is not None:
            config.strength = strength
        if target_psnr is not None:
            config.target_psnr = target_psnr
        if use_ai_saliency is not None:
            config.use_ai_saliency = use_ai_saliency
        
        self.config = config
        
        # Validate configuration
        warnings = self.config.validate()
        if warnings and self.config.show_warnings:
            for warning in warnings:
                print(warning)
        
        # Apply priority optimizations
        self.config.optimize_for_priority()
        
        # Initialize crypto engine
        if key:
            self.crypto = CryptoEngine(key)
            self.key = key
        elif config.encryption_key:
            self.crypto = CryptoEngine(config.encryption_key)
            self.key = config.encryption_key
        else:
            self.crypto = CryptoEngine()
            self.key = self.crypto.get_key_string()
        
        # Initialize AI saliency detector if enabled
        self.saliency_detector = None
        if self.config.use_ai_saliency:
            if self.config.saliency_method == "deep_learning":
                # TODO: Implement deep learning saliency
                self.saliency_detector = SaliencyDetector()
            else:
                self.saliency_detector = SaliencyDetector()
        
        # Initialize core embedder
        self.embedder = WatermarkEmbedder(
            crypto_engine=self.crypto,
            strength=self.config.strength,
            use_error_correction=self.config.use_error_correction
        )
    
    def embed(
        self,
        input_path: Union[str, Path],
        copyright_info: Union[str, Dict[str, Any]],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> EmbedResult:
        """
        Embed watermark into image with ALL features.
        
        Args:
            input_path: Path to input image
            copyright_info: Copyright information (string or dict)
            output_path: Path for output. None = auto-generate
            **kwargs: Override config settings for this embed
        
        Returns:
            EmbedResult with all information
        """
        try:
            input_path = Path(input_path)
            
            # Load original image
            original_img = Image.open(input_path)
            original_format = original_img.format
            original_size = os.path.getsize(input_path)
            
            # Get format-specific settings if preserving
            format_settings = None
            if self.config.preserve_format:
                format_settings = self._detect_format_settings(input_path, original_img)
            
            # Convert to RGB array
            img_array = np.array(original_img.convert('RGB'))
            
            # Build payload
            payload_builder = PayloadBuilder()
            
            payload_dict: Dict[str, Any]
            if isinstance(copyright_info, dict):
                payload_dict = copyright_info.copy()
            else:
                payload_dict = {"copyright": copyright_info}
            
            # Add optional metadata based on config
            if self.config.include_timestamp:
                from datetime import datetime
                payload_dict["timestamp"] = datetime.now().isoformat()
            
            if self.config.include_truthmark_id:
                import uuid
                payload_dict["truthmark_id"] = str(uuid.uuid4())
            
            if self.config.include_fingerprint:
                import hashlib
                payload_dict["image_hash"] = hashlib.sha256(img_array.tobytes()).hexdigest()[:16]
            
            # Add EU AI Act compliance if needed
            if self.config.ai_act_compliance:
                payload_dict.setdefault("ai_compliance", {})
                payload_dict["ai_compliance"]["eu_ai_act"] = True
                payload_dict["ai_compliance"]["synthetic_content"] = payload_dict.get("ai_generated", False)
            
            # Add custom metadata
            if self.config.custom_metadata:
                payload_dict.update(self.config.custom_metadata)
            
            # Create payload bytes
            payload_json = json.dumps(payload_dict, separators=(',', ':'))
            payload_bytes = payload_json.encode('utf-8')
            
            # Apply error correction if enabled
            if self.config.use_error_correction:
                from ..core.error_correction import ErrorCorrection
                ecc = ErrorCorrection(ecc_symbols=self.config.get_ecc_symbols())
                payload_bytes = ecc.encode(payload_bytes)
            
            # Encrypt payload
            encrypted_data, integrity_hash = self.crypto.encrypt(payload_bytes)
            # Combine encrypted data and hash for embedding
            encrypted_payload = encrypted_data + integrity_hash
            
            # Compute saliency map if AI enabled
            saliency_map = None
            if self.saliency_detector:
                saliency_map = self.saliency_detector.detect(img_array)
            
            # Adaptive strength to meet target PSNR
            current_strength = self.config.strength
            if self.config.adaptive_strength:
                current_strength = self._find_optimal_strength(
                    img_array,
                    encrypted_payload,
                    saliency_map,
                    self.config.target_psnr
                )
            
            # Embed watermark
            watermarked_array, embed_info = self.embedder.embed(
                image=img_array,
                payload=encrypted_payload,
                saliency_map=saliency_map
            )
            
            # Convert back to PIL Image
            watermarked_img = Image.fromarray(watermarked_array.astype(np.uint8))
            
            # Generate output path if not provided
            if output_path is None:
                output_path = input_path.parent / f"{input_path.stem}_watermarked{input_path.suffix}"
            else:
                output_path = Path(output_path)
            
            # Save with format preservation
            format_preserved = False
            size_match = 0.0
            
            if self.config.preserve_format and format_settings and original_format:
                self._save_with_format_preservation(
                    watermarked_img,
                    output_path,
                    original_format,
                    format_settings,
                    original_size if self.config.preserve_size else None
                )
                format_preserved = True
            else:
                # Simple save
                watermarked_img.save(str(output_path))
            
            # Calculate size match
            output_size = os.path.getsize(output_path)
            size_match = output_size / original_size if original_size > 0 else 0.0
            
            # Return result
            return EmbedResult(
                success=True,
                key=self.key,
                output_path=str(output_path),
                payload=payload_dict,
                embedding_info=embed_info,
                image=watermarked_array,
                format_preserved=format_preserved,
                size_match=size_match,
                original_format=original_format,
                output_format=Image.open(output_path).format,
                original_size=original_size,
                output_size=output_size
            )
            
        except Exception as e:
            return EmbedResult(
                success=False,
                key=self.key,
                error_message=str(e)
            )
    
    def _detect_format_settings(self, path: Path, img: Image.Image) -> Dict[str, Any]:
        """Detect original format-specific settings."""
        settings = {}
        
        if img.format == "JPEG":
            # Try to detect JPEG quality
            if self.config.jpeg_quality is not None:
                settings["quality"] = self.config.jpeg_quality
            else:
                # Estimate quality from file
                settings["quality"] = self._estimate_jpeg_quality(path)
            
            # Detect subsampling
            if self.config.jpeg_subsampling:
                settings["subsampling"] = self.config.jpeg_subsampling
            else:
                settings["subsampling"] = 0  # 4:4:4 (best quality)
        
        elif img.format == "PNG":
            if self.config.png_compression is not None:
                settings["compress_level"] = self.config.png_compression
            else:
                settings["compress_level"] = 6  # Default
        
        elif img.format == "WEBP":
            if self.config.webp_quality is not None:
                settings["quality"] = self.config.webp_quality
            else:
                settings["quality"] = 90
        
        # Preserve metadata
        if self.config.preserve_metadata:
            if hasattr(img, 'info'):
                settings["exif"] = img.info.get("exif")
                settings["icc_profile"] = img.info.get("icc_profile")
        
        return settings
    
    def _estimate_jpeg_quality(self, path: Path) -> int:
        """Estimate JPEG quality from file size."""
        # Rough estimation based on file size ratio
        img = Image.open(path)
        width, height = img.size
        pixels = width * height
        file_size = os.path.getsize(path)
        
        # bytes per pixel
        bpp = file_size / pixels
        
        # Rough mapping (empirical)
        if bpp > 2.0:
            return 95
        elif bpp > 1.5:
            return 90
        elif bpp > 1.0:
            return 85
        elif bpp > 0.5:
            return 75
        else:
            return 70
    
    def _save_with_format_preservation(
        self,
        img: Image.Image,
        output_path: Path,
        original_format: str,
        format_settings: Dict[str, Any],
        target_size: Optional[int] = None
    ):
        """Save image with format preservation and optional size matching."""
        
        if not self.config.preserve_size or target_size is None:
            # Just save with detected settings
            if original_format == "JPEG":
                # Build save kwargs, only include non-None values
                save_kwargs = {
                    "format": "JPEG",
                    "quality": format_settings.get("quality", 85),
                    "subsampling": format_settings.get("subsampling", 0)
                }
                if format_settings.get("exif") is not None:
                    save_kwargs["exif"] = format_settings["exif"]
                if format_settings.get("icc_profile") is not None:
                    save_kwargs["icc_profile"] = format_settings["icc_profile"]
                
                img.save(str(output_path), **save_kwargs)
            elif original_format == "PNG":
                save_kwargs = {
                    "format": "PNG",
                    "compress_level": format_settings.get("compress_level", 6)
                }
                if format_settings.get("icc_profile") is not None:
                    save_kwargs["icc_profile"] = format_settings["icc_profile"]
                
                img.save(str(output_path), **save_kwargs)
            else:
                img.save(str(output_path), format=original_format)
            return
        
        # Binary search for quality to match size
        if original_format == "JPEG":
            quality = self._binary_search_jpeg_quality(
                img,
                output_path,
                target_size,
                format_settings
            )
            save_kwargs = {
                "format": "JPEG",
                "quality": quality,
                "subsampling": format_settings.get("subsampling", 0)
            }
            if format_settings.get("exif") is not None:
                save_kwargs["exif"] = format_settings["exif"]
            if format_settings.get("icc_profile") is not None:
                save_kwargs["icc_profile"] = format_settings["icc_profile"]
            
            img.save(str(output_path), **save_kwargs)
        else:
            # For PNG, just save (compression doesn't affect size much)
            save_kwargs = {
                "format": original_format,
                "compress_level": format_settings.get("compress_level", 6)
            }
            if format_settings.get("icc_profile") is not None:
                save_kwargs["icc_profile"] = format_settings["icc_profile"]
            
            img.save(str(output_path), **save_kwargs)
    
    def _binary_search_jpeg_quality(
        self,
        img: Image.Image,
        output_path: Path,
        target_size: int,
        format_settings: Dict[str, Any],
        max_iterations: int = 10
    ) -> int:
        """Binary search to find JPEG quality that matches target size."""
        
        tolerance = target_size * self.config.size_tolerance
        low_quality = 70
        high_quality = 95
        best_quality = 85
        
        for _ in range(max_iterations):
            mid_quality = (low_quality + high_quality) // 2
            
            # Try saving with this quality
            temp_path = output_path.with_suffix(".temp.jpg")
            img.save(
                str(temp_path),
                format="JPEG",
                quality=mid_quality,
                subsampling=format_settings.get("subsampling", 0)
            )
            
            current_size = os.path.getsize(temp_path)
            temp_path.unlink()
            
            # Check if within tolerance
            if abs(current_size - target_size) <= tolerance:
                return mid_quality
            
            # Adjust search range
            if current_size > target_size:
                high_quality = mid_quality - 1
            else:
                low_quality = mid_quality + 1
                best_quality = mid_quality
        
        return best_quality
    
    def _find_optimal_strength(
        self,
        img_array: np.ndarray,
        payload: bytes,
        saliency_map: Optional[np.ndarray],
        target_psnr: float,
        tolerance: float = 0.5
    ) -> float:
        """Find optimal strength to achieve target PSNR."""
        
        # Start with config strength
        strengths_to_try = [
            self.config.strength * 0.7,
            self.config.strength * 0.85,
            self.config.strength,
            self.config.strength * 1.15,
            self.config.strength * 1.3
        ]
        
        best_strength = self.config.strength
        best_psnr_diff = float('inf')
        
        for strength in strengths_to_try:
            # Try embedding with this strength
            test_embedder = WatermarkEmbedder(
                crypto_engine=self.crypto,
                strength=strength
            )
            
            try:
                _, embed_info = test_embedder.embed(
                    image=img_array,
                    payload=payload,
                    saliency_map=saliency_map
                )
                
                psnr = embed_info.get('psnr_db', 0)
                psnr_diff = abs(psnr - target_psnr)
                
                if psnr_diff < best_psnr_diff:
                    best_psnr_diff = psnr_diff
                    best_strength = strength
                
                # If within tolerance, use it
                if psnr_diff <= tolerance:
                    return strength
                    
            except Exception:
                continue
        
        return best_strength
    
    def embed_batch(
        self,
        image_paths: list[Union[str, Path]],
        copyright_infos: Union[Dict[str, Any], list[Dict[str, Any]]],
        output_dir: Optional[Union[str, Path]] = None
    ) -> list[EmbedResult]:
        """
        Batch embed watermarks into multiple images.
        
        Args:
            image_paths: List of input image paths
            copyright_infos: Single dict for all, or list matching image_paths
            output_dir: Output directory. None = same as input
            
        Returns:
            List of EmbedResult for each image
        """
        results = []
        
        # Handle single copyright info for all images
        if isinstance(copyright_infos, dict):
            copyright_infos = [copyright_infos] * len(image_paths)
        
        for img_path, copyright_info in zip(image_paths, copyright_infos):
            img_path = Path(img_path)
            
            if output_dir:
                output_path = Path(output_dir) / f"{img_path.stem}_watermarked{img_path.suffix}"
            else:
                output_path = None
            
            result = self.embed(img_path, copyright_info, output_path)
            results.append(result)
        
        return results
