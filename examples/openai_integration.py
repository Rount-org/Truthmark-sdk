"""
OpenAI Integration Simulation
-----------------------------
This script simulates how OpenAI would use TruthMark to watermark generated images.

Scenario:
1. OpenAI DALL-E generates an image.
2. TruthMark SDK embeds metadata (Model, User, Prompt ID).
3. User downloads image and posts to social media (compression).
4. TruthMark Decoder verifies the origin.
"""

import cv2
import numpy as np
import os
import json
from truthmark_sdk import TruthMarkClient

def simulate_openai_integration():
    print("\n" + "="*60)
    print("🤖 OpenAI Integration Simulation")
    print("="*60)

    # 1. Simulate DALL-E Generation
    print("\n🎨 Step 1: DALL-E Generates Image...")
    # Create a dummy image (512x512)
    image = np.zeros((512, 512, 3), dtype=np.uint8)
    # Add some patterns
    cv2.circle(image, (256, 256), 100, (255, 0, 0), -1)
    cv2.rectangle(image, (50, 50), (200, 200), (0, 255, 0), -1)
    
    original_path = "dalle_gen_original.png"
    cv2.imwrite(original_path, image)
    print(f"   ✓ Image generated: {original_path}")

    # 2. OpenAI Embeds Metadata
    print("\n🔐 Step 2: Embedding TruthMark...")
    
    # Metadata OpenAI might want to embed
    metadata = {
        "source": "OpenAI DALL-E 3",
        "gen_id": "gen_abc123xyz",
        "user_hash": "u_987654321",
        "timestamp": "2025-11-23T12:00:00Z",
        "is_ai": True
    }
    message = json.dumps(metadata)
    print(f"   ✓ Metadata: {message}")

    # Initialize SDK
    client = TruthMarkClient()
    
    watermarked_path = "dalle_gen_protected.png"
    result = client.encode(original_path, message, watermarked_path)
    
    print("   ✓ Watermark Embedded!")
    print(f"   ✓ PSNR Quality: {result['psnr']:.2f} dB (Invisible)")
    print(f"   ✓ Saved to: {watermarked_path}")

    # 3. User Downloads & Manipulates (Attack)
    print("\n🌍 Step 3: Simulating Real-World Usage (Attack)...")
    
    # Load protected image
    img = cv2.imread(watermarked_path)
    
    # Attack 1: JPEG Compression
    print("   ⚡ Applying JPEG Compression (Quality 70)...")
    cv2.imwrite("social_media_post.jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
    
    # Attack 2: Resizing (Social Media Preview)
    print("   ⚡ Simulating Resize (50%)...")
    attacked = cv2.imread("social_media_post.jpg")
    h, w = attacked.shape[:2]
    resized = cv2.resize(attacked, (int(w*0.5), int(h*0.5)))
    
    # Save final attacked image
    final_path = "social_media_final.jpg"
    cv2.imwrite(final_path, resized)
    print(f"   ✓ Final image saved: {final_path}")

    # 4. Verification (Decoding)
    print("\n🔍 Step 4: Verifying Origin...")
    
    # Decode from the ATTACKED image
    decode_result = client.decode(final_path)
    
    if decode_result['found']:
        print("\n✅ SUCCESS: Origin Verified!")
        print(f"   Confidence: {decode_result['confidence']:.1%}")
        print(f"   Extracted Data: {decode_result['message']}")
        
        # Parse JSON
        try:
            data = json.loads(decode_result['message'])
            print(f"   Source: {data.get('source')}")
            print(f"   Gen ID: {data.get('gen_id')}")
        except json.JSONDecodeError:
            pass
    else:
        print("\n❌ FAILED: Could not verify origin.")

    print("\n" + "="*60)
    print("Simulation Complete")
    print("="*60)

if __name__ == "__main__":
    simulate_openai_integration()
