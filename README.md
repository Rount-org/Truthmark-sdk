# TruthMark SDK

Multi-language SDK for TruthMark invisible watermarking API.

## 📦 Available Languages

| Language | Path | Status | Documentation |
|----------|------|--------|---------------|
| **Python** | [`/python`](./python) | ✅ Stable | [Docs](./python/README.md) |
| **JavaScript/TypeScript** | [`/javascript`](./javascript) | ✅ Stable | [Docs](./javascript/README.md) |
| **Java** | [`/java`](./java) | 🚧 Planned | Coming soon |
| **Go** | [`/go`](./go) | 🚧 Planned | Coming soon |
| **Ruby** | [`/ruby`](./ruby) | 🚧 Planned | Coming soon |

## 🚀 Quick Start

Choose your language:

### Python
```bash
cd python
pip install -e .
```

```python
from truthmark_sdk import TruthMarkClient

client = TruthMarkClient()
client.encode("input.png", "My watermark", "output.png")
```

### JavaScript/TypeScript
```bash
cd javascript
npm install
npm run build
```

```javascript
const { TruthMarkClient } = require('@truthmark/sdk');

const client = new TruthMarkClient();
await client.encode('./input.png', 'My watermark');
```

## 📖 Full Documentation

Visit [docs.truthmark.com](https://docs.truthmark.com) for complete guides and API reference.

## 🏗️ Core Engine

All language SDKs use the same C++ core watermarking engine located in `/core`.

## 🤝 Contributing

Contributions welcome! See language-specific README for development setup.

## 📄 License

MIT © TruthMark Team
