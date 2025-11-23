# TruthMark Python SDK

Official Python SDK for TruthMark invisible watermarking API.

## Installation

```bash
pip install truthmark-sdk
```

## Quick Start

```python
from truthmark_sdk import TruthMarkClient

# Initialize client
client = TruthMarkClient()

# Encode watermark
result = client.encode("image.png", "My secret message", "output.png")
print(f"✓ Encoded with PSNR: {result['psnr']}")

# Decode watermark
decoded = client.decode("output.png")
if decoded['found']:
    print(f"✓ Message: {decoded['message']}")
```

## API Methods

- **`encode(image_path, message, output_path)`** - Embed watermark into image
- **`decode(image_path)`** - Extract watermark from image

## Documentation

Visit [docs.truthmark.com](https://docs.truthmark.com) for full documentation.
