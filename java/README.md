# TruthMark Java SDK

Official Java SDK for TruthMark invisible watermarking API.

## Installation

Add to your `pom.xml`:

```xml
<dependency>
    <groupId>com.truthmark</groupId>
    <artifactId>truthmark-sdk</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Quick Start

```java
import com.truthmark.sdk.TruthMarkClient;

// Initialize client
TruthMarkClient client = new TruthMarkClient();

// Encode watermark
EncodeResult result = client.encode("image.png", "My secret message");
System.out.println("✓ Download: " + result.download_url);

// Decode watermark
DecodeResult decoded = client.decode("watermarked.png");
if (decoded.found) {
    System.out.println("✓ Message: " + decoded.message);
}
```

## API Methods

- **`encode(imagePath, message)`** - Embed watermark into image
- **`decode(imagePath)`** - Extract watermark from image

## Documentation

Visit [docs.truthmark.com](https://docs.truthmark.com) for full documentation.
