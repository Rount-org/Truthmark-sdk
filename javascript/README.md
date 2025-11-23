# TruthMark JavaScript/TypeScript SDK

Official JavaScript SDK for TruthMark invisible watermarking.

## Installation

```bash
npm install @truthmark/sdk
```

## Quick Start

### Node.js
```javascript
const { TruthMarkClient } = require('@truthmark/sdk');

const client = new TruthMarkClient({
  baseUrl: 'http://localhost:8000'
});

// Encode
const result = await client.encode('./image.png', 'My watermark');
console.log(`Download: ${result.download_url}`);

// Decode
const decoded = await client.decode('./watermarked.png');
if (decoded.found) {
  console.log(`Message: ${decoded.message}`);
}
```

### Browser/React
```typescript
import { TruthMarkClient } from '@truthmark/sdk';

const client = new TruthMarkClient();

// In your component
const handleUpload = async (file: File) => {
  const result = await client.encode(file, 'Copyright 2025');
  window.open(result.download_url);
};
```

## Full Documentation

See [docs.truthmark.com/sdks/javascript](https://docs.truthmark.com/sdks/javascript)
