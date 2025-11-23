# TruthMark SDK - Complete Multi-Language Suite

Professional SDKs for TruthMark invisible watermarking API in 10 programming languages.

## 🌍 Available SDKs

| Language | Status | Installation | Documentation |
|----------|--------|--------------|---------------|
| **Python** | ✅ Ready | `pip install truthmark-sdk` | [Docs](./python/README.md) |
| **JavaScript** | ✅ Ready | `npm install @truthmark/sdk-javascript` | [Docs](./javascript/README.md) |
| **TypeScript** | ✅ Ready | `npm install @truthmark/sdk-typescript` | [Docs](./typescript/README.md) |
| **Java** | ✅ Ready | Maven: `com.truthmark:truthmark-sdk:1.0.0` | [Docs](./java/README.md) |
| **Go** | ✅ Ready | `go get github.com/truthmark/sdk` | [Docs](./go/README.md) |
| **C# (.NET)** | ✅ Ready | NuGet: `TruthMark.SDK` | [Docs](./csharp/README.md) |
| **PHP** | ✅ Ready | `composer require truthmark/sdk` | [Docs](./php/README.md) |
| **Ruby** | ✅ Ready | `gem install truthmark-sdk` | [Docs](./ruby/README.md) |
| **Swift** | ✅ Ready | Add to Xcode project | [Docs](./swift/README.md) |
| **Kotlin** | ✅ Ready | Add to build.gradle | [Docs](./kotlin/README.md) |

## 🚀 Quick Examples

All SDKs follow the same simple API:

### Python
```python
from truthmark_sdk import TruthMarkClient

client = TruthMarkClient()
result = client.encode("image.png", "My watermark", "output.png")
decoded = client.decode("output.png")
```

### JavaScript
```javascript
const { TruthMarkClient } = require('@truthmark/sdk-javascript');

const client = new TruthMarkClient();
const result = await client.encode('./image.png', 'My watermark');
const decoded = await client.decode('./output.png');
```

### TypeScript
```typescript
import { TruthMarkClient } from '@truthmark/sdk-typescript';

const client = new TruthMarkClient();
const result = await client.encode('./image.png', 'My watermark');
const decoded = await client.decode('./output.png');
```

### Java
```java
TruthMarkClient client = new TruthMarkClient();
EncodeResult result = client.encode("image.png", "My watermark");
DecodeResult decoded = client.decode("watermarked.png");
```

### Go
```go
client := truthmark.NewClient(nil)
result, _ := client.Encode("image.png", "My watermark")
decoded, _ := client.Decode("watermarked.png")
```

### C#
```csharp
var client = new TruthMarkClient();
var result = await client.EncodeAsync("image.png", "My watermark");
var decoded = await client.DecodeAsync("watermarked.png");
```

### PHP
```php
$client = new \TruthMark\SDK\TruthMarkClient();
$result = $client->encode('image.png', 'My watermark');
$decoded = $client->decode('watermarked.png');
```

### Ruby
```ruby
client = TruthMark::Client.new
result = client.encode('image.png', 'My watermark')
decoded = client.decode('watermarked.png')
```

### Swift
```swift
let client = TruthMarkClient()
let result = try await client.encode(imagePath: "image.png", message: "My watermark")
let decoded = try await client.decode(imagePath: "watermarked.png")
```

### Kotlin
```kotlin
val client = TruthMarkClient()
val result = client.encode("image.png", "My watermark")
val decoded = client.decode("watermarked.png")
```

## 📦 What's Included

Each SDK includes:
- ✅ **encode()** - Embed invisible watermarks
- ✅ **decode()** - Extract watermarks
- ✅ **Type safety** - Full type definitions/interfaces
- ✅ **Error handling** - Proper exceptions/errors
- ✅ **Authentication** - API key support
- ✅ **Documentation** - Complete API reference

## 🏗️ Build Systems

- **Python**: setuptools, pip install able
- **JavaScript**: Pure JavaScript, no build step
- **TypeScript**: TypeScript + npm
- **Java**: Maven (pom.xml)
- **Go**: Go modules (go.mod)
- **C#**: .NET 6+ (.csproj)
- **PHP**: Composer (composer.json)
- **Ruby**: RubyGems (.gemspec)
- **Swift**: Swift Package Manager
- **Kotlin**: Gradle

## 📖 Full Documentation

Visit [docs.truthmark.com](https://docs.truthmark.com) for:
- Getting started guides
- API reference
- Integration examples
- Best practices

## 🤝 Contributing

Contributions welcome! See language-specific README for development setup.

## 📄 License

MIT © TruthMark Team
