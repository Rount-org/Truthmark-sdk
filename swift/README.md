# TruthMark Swift SDK

Official Swift SDK for TruthMark invisible watermarking API.

## Installation

Add to your `Package.swift`:

```swift
dependencies: [
    .package(url: "https://github.com/truthmark/sdk-swift", from: "1.0.0")
]
```

Or add to Xcode project via File → Add Packages.

## Quick Start

```swift
import TruthMarkSDK

// Initialize client
let client = TruthMarkClient()

// Encode watermark
let result = try await client.encode(imagePath: "image.png", message: "My secret message")
print("✓ Download: \(result.downloadUrl)")

// Decode watermark
let decoded = try await client.decode(imagePath: "watermarked.png")
if decoded.found {
    print("✓ Message: \(decoded.message)")
}
```

## API Methods

- **`encode(imagePath:message:)`** - Embed watermark into image
- **`decode(imagePath:)`** - Extract watermark from image

## Documentation

Visit [docs.truthmark.com](https://docs.truthmark.com) for full documentation.
