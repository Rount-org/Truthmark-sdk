# TruthMark PHP SDK

Official PHP SDK for TruthMark invisible watermarking API.

## Installation

```bash
composer require truthmark/sdk
```

## Quick Start

```php
<?php
require 'vendor/autoload.php';

use TruthMark\SDK\TruthMarkClient;

// Initialize client
$client = new TruthMarkClient();

// Encode watermark
$result = $client->encode('image.png', 'My secret message');
echo "✓ Download: {$result['download_url']}\n";

// Decode watermark
$decoded = $client->decode('watermarked.png');
if ($decoded['found']) {
    echo "✓ Message: {$decoded['message']}\n";
}
```

## API Methods

- **`encode($imagePath, $message)`** - Embed watermark into image
- **`decode($imagePath)`** - Extract watermark from image

## Documentation

Visit [docs.truthmark.com](https://docs.truthmark.com) for full documentation.
