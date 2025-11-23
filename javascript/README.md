# TruthMark JavaScript SDK

Official pure JavaScript SDK for TruthMark invisible watermarking. No build step required, works directly with Node.js and browsers.

## Installation

```bash
npm install @truthmark/sdk-javascript
```

## Quick Start

### Node.js

```javascript
const { TruthMarkClient } = require('@truthmark/sdk-javascript');

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

```javascript
import { TruthMarkClient } from '@truthmark/sdk-javascript';

const client = new TruthMarkClient();

// In your component
const handleUpload = async (file) => {
  const result = await client.encode(file, 'Copyright 2025');
  window.open(result.download_url);
};

// Decode from file input
const handleDecode = async (file) => {
  const result = await client.decode(file);
  if (result.found) {
    alert(`Watermark found: ${result.message}`);
  }
};
```

## Features

- ✅ **Pure JavaScript** - No TypeScript, no build step needed
- ✅ **Universal** - Works in Node.js and browsers
- ✅ **JSDoc Types** - Full IDE intellisense support
- ✅ **ES Modules** - Modern JavaScript module system
- ✅ **Simple API** - Just two methods: `encode()` and `decode()`

## API Reference

### Constructor

```javascript
const client = new TruthMarkClient(config);
```

**Parameters:**
- `config` (optional): Configuration object
  - `apiKey` (string, optional): API key for authentication
  - `baseUrl` (string, optional): Base URL for API (default: 'http://localhost:8000')

### encode(imagePath, message)

Embed an invisible watermark into an image.

**Parameters:**
- `imagePath` (string|File|Blob): Path to image file (Node.js) or File/Blob object (Browser)
- `message` (string): Text message to embed

**Returns:** Promise<EncodeResult>
- `status` (string): Operation status
- `metadata` (object): Encoding metadata
  - `psnr` (number): Peak Signal-to-Noise Ratio
  - `bits_embedded` (number): Number of bits embedded
- `download_url` (string): URL to download watermarked image

### decode(imagePath)

Extract watermark from an image.

**Parameters:**
- `imagePath` (string|File|Blob): Path to image file (Node.js) or File/Blob object (Browser)

**Returns:** Promise<DecodeResult>
- `found` (boolean): Whether watermark was found
- `message` (string|null): Extracted message
- `confidence` (number): Confidence score (0-1)

## Full Documentation

See [docs.truthmark.com/sdks/javascript](https://docs.truthmark.com/sdks/javascript)
