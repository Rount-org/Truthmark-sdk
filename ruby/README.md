# TruthMark Ruby SDK

Official Ruby SDK for TruthMark invisible watermarking API.

## Installation

```bash
gem install truthmark-sdk
```

Or add to your `Gemfile`:
```ruby
gem 'truthmark-sdk'
```

## Quick Start

```ruby
require 'truthmark'

# Initialize client
client = TruthMark::Client.new

# Encode watermark
result = client.encode('image.png', 'My secret message')
puts "✓ Download: #{result[:download_url]}"

# Decode watermark
decoded = client.decode('watermarked.png')
if decoded[:found]
  puts "✓ Message: #{decoded[:message]}"
end
```

## API Methods

- **`encode(image_path, message)`** - Embed watermark into image
- **`decode(image_path)`** - Extract watermark from image

## Documentation

Visit [docs.truthmark.com](https://docs.truthmark.com) for full documentation.
