<?php

namespace TruthMark\SDK;

class TruthMarkClient
{
    private string $baseUrl;
    private ?string $apiKey;
    private int $timeout;

    public function __construct(array $config = [])
    {
        $this->baseUrl = $config['base_url'] ?? 'http://localhost:8000';
        $this->apiKey = $config['api_key'] ?? null;
        $this->timeout = $config['timeout'] ?? 30;
    }

    /**
     * Embed an invisible watermark into an image
     *
     * @param string $imagePath Path to input image
     * @param string $message Text to embed (max 500 chars)
     * @return array Encode result with metadata
     * @throws \Exception
     */
    public function encode(string $imagePath, string $message): array
    {
        if (!file_exists($imagePath)) {
            throw new \Exception("Image file not found: {$imagePath}");
        }

        $ch = curl_init();
        
        $data = [
            'file' => new \CURLFile($imagePath),
            'message' => $message
        ];

        $headers = [];
        if ($this->apiKey) {
            $headers[] = "Authorization: Bearer {$this->apiKey}";
        }

        curl_setopt_array($ch, [
            CURLOPT_URL => "{$this->baseUrl}/v1/encode",
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $data,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_TIMEOUT => $this->timeout,
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        
        if (curl_errno($ch)) {
            $error = curl_error($ch);
            curl_close($ch);
            throw new \Exception("cURL error: {$error}");
        }
        
        curl_close($ch);

        if ($httpCode !== 200) {
            throw new \Exception("API Error: HTTP {$httpCode}");
        }

        $result = json_decode($response, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new \Exception("Failed to parse JSON response");
        }

        return $result;
    }

    /**
     * Extract watermark from an image
     *
     * @param string $imagePath Path to watermarked image
     * @return array Decode result with message and confidence
     * @throws \Exception
     */
    public function decode(string $imagePath): array
    {
        if (!file_exists($imagePath)) {
            throw new \Exception("Image file not found: {$imagePath}");
        }

        $ch = curl_init();
        
        $data = [
            'file' => new \CURLFile($imagePath)
        ];

        $headers = [];
        if ($this->apiKey) {
            $headers[] = "Authorization: Bearer {$this->apiKey}";
        }

        curl_setopt_array($ch, [
            CURLOPT_URL => "{$this->baseUrl}/v1/decode",
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $data,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_TIMEOUT => $this->timeout,
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        
        if (curl_errno($ch)) {
            $error = curl_error($ch);
            curl_close($ch);
            throw new \Exception("cURL error: {$error}");
        }
        
        curl_close($ch);

        if ($httpCode !== 200) {
            throw new \Exception("API Error: HTTP {$httpCode}");
        }

        $result = json_decode($response, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new \Exception("Failed to parse JSON response");
        }

        return $result;
    }
}
