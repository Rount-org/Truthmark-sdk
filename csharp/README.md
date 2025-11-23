# TruthMark C# SDK

Official .NET SDK for TruthMark invisible watermarking API.

## Installation

```bash
dotnet add package TruthMark.SDK
```

Or via NuGet Package Manager:
```
Install-Package TruthMark.SDK
```

## Quick Start

```csharp
using TruthMark.SDK;

// Initialize client
var client = new TruthMarkClient();

// Encode watermark
var result = await client.EncodeAsync("image.png", "My secret message");
Console.WriteLine($"✓ Download: {result.DownloadUrl}");

// Decode watermark
var decoded = await client.DecodeAsync("watermarked.png");
if (decoded.Found) {
    Console.WriteLine($"✓ Message: {decoded.Message}");
}
```

## API Methods

- **`EncodeAsync(imagePath, message)`** - Embed watermark into image
- **`DecodeAsync(imagePath)`** - Extract watermark from image

## Documentation

Visit [docs.truthmark.com](https://docs.truthmark.com) for full documentation.
