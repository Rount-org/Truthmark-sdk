# TruthMark Python SDK

Official Python SDK for TruthMark invisible watermarking API.

## Installation

```bash
pip install truthmark-sdk
```
# TruthMark Python SDK

Official Python SDK for TruthMark invisible watermarking API.

## Installation

```bash
pip install truthmark-sdk
```

## Quick Start

```python
from truthmark_sdk import TruthMarkClient

# Initialize the client (API Key optional for public beta)
client = TruthMarkClient(api_key="your_api_key")

# 1. Encode (Embed data into image)
result = client.encode(
    image_path="original.jpg",
    message="Copyright 2025 Rount Inc.",
    output_path="protected.png"
)
print(f"Encoded! Saved to: {result['output_path']}")

# 2. Decode (Extract data from image)
data = client.decode("protected.png")

if data["found"]:
    print(f"Found Watermark: {data['message']}")
    print(f"Confidence: {data['confidence']}")
else:
    print("No watermark found.")
```

## Features

- **Cloud-Powered**: Uses the TruthMark API for heavy lifting.
- **Lightweight**: No heavy ML dependencies locally.
- **Secure**: Your core logic remains on the server.
- **Easy Integration**: Simple Python interface.

## Documentation

Full documentation is available at [https://truthmark.com/docs](https://truthmark.com/docs).
