# TruthMark Kotlin SDK

Official Kotlin SDK for TruthMark invisible watermarking API.

## Installation

Add to your `build.gradle.kts`:

```kotlin
dependencies {
    implementation("com.truthmark:sdk:1.0.0")
}
```

## Quick Start

```kotlin
import com.truthmark.sdk.TruthMarkClient

// Initialize client
val client = TruthMarkClient()

// Encode watermark
val result = client.encode("image.png", "My secret message")
println("✓ Download: ${result.downloadUrl}")

// Decode watermark
val decoded = client.decode("watermarked.png")
if (decoded.found) {
    println("✓ Message: ${decoded.message}")
}
```

## API Methods

- **`encode(imagePath, message)`** - Embed watermark into image
- **`decode(imagePath)`** - Extract watermark from image

## Documentation

Visit [docs.truthmark.com](https://docs.truthmark.com) for full documentation.
