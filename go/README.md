# TruthMark Go SDK

Official Go SDK for TruthMark invisible watermarking API.

## Installation

```bash
go get github.com/truthmark/sdk
```

## Quick Start

```go
package main

import (
    "fmt"
    truthmark "github.com/truthmark/sdk"
)

func main() {
    // Initialize client
    client := truthmark.NewClient(nil)

    // Encode watermark
    result, _ := client.Encode("image.png", "My secret message")
    fmt.Printf("✓ Download: %s\n", result.DownloadURL)

    // Decode watermark
    decoded, _ := client.Decode("watermarked.png")
    if decoded.Found {
        fmt.Printf("✓ Message: %s\n", decoded.Message)
    }
}
```

## API Methods

- **`Encode(imagePath, message)`** - Embed watermark into image
- **`Decode(imagePath)`** - Extract watermark from image

## Documentation

Visit [docs.truthmark.com](https://docs.truthmark.com) for full documentation.
