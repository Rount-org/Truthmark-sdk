# TruthMark SDK

Multi-language SDK collection for TruthMark invisible watermarking API.

## 🌍 Available SDKs

| Language | Status | Path | Documentation |
|----------|--------|------|---------------|
| **Python** | ✅ Production Ready | [`/python`](./python) | [Docs](./python/README.md) |
| **JavaScript/TypeScript** | ✅ Production Ready | [`/javascript`](./javascript) | [Docs](./javascript/README.md) |
| **Java** | ✅ Production Ready | [`/java`](./java) | [Docs](./java/README.md) |
| **Go** | ✅ Production Ready | [`/go`](./go) | [Docs](./go/README.md) |
| **C# (.NET)** | ✅ Production Ready | [`/csharp`](./csharp) | [Docs](./csharp/README.md) |
| **PHP** | ✅ Production Ready | [`/php`](./php) | [Docs](./php/README.md) |
| **Swift (iOS)** | ✅ Production Ready | [`/swift`](./swift) | [Docs](./swift/README.md) |
| **Kotlin (Android)** | ✅ Production Ready | [`/kotlin`](./kotlin) | [Docs](./kotlin/README.md) |

## 🚀 Quick Start

Choose your language and follow the installation guide:

### Python
```bash
cd python && pip install -e .
```

### JavaScript/TypeScript
```bash
cd javascript && npm install
```

### Java
```bash
cd java && mvn install
```

### Go
```bash
cd go && go get
```

### C#
```bash
cd csharp && dotnet build
```

### PHP
```bash
cd php && composer install
```

### Swift
```swift
// Add TruthMarkClient.swift to your Xcode project
```

### Kotlin
```kotlin
// Add to your build.gradle
```

## 📖 Usage Examples

All SDKs follow the same simple API:

**Encode:**
```
client.encode(imagePath, message)
```

**Decode:**
```
client.decode(imagePath)
```

See language-specific READMEs for detailed examples.

## 🏗️ Core Engine

All SDKs use the same C++ core watermarking engine located in `/core`.

## 🤝 Contributing

Contributions welcome! See language-specific README for development setup.

## 📄 License

MIT © TruthMark Team
