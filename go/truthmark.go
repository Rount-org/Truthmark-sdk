package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"time"
)

// Config holds the client configuration
type Config struct {
	BaseURL string
	APIKey  string
	Timeout time.Duration
}

// EncodeResult represents the encode API response
type EncodeResult struct {
	Status      string `json:"status"`
	Metadata    Metadata `json:"metadata"`
	DownloadURL string `json:"download_url"`
}

// Metadata holds encoding metadata
type Metadata struct {
	PSNR          float64 `json:"psnr"`
	BitsEmbedded  int     `json:"bits_embedded"`
}

// DecodeResult represents the decode API response
type DecodeResult struct {
	Found      bool    `json:"found"`
	Message    string  `json:"message"`
	Confidence float64 `json:"confidence"`
}

// Client is the TruthMark API client
type Client struct {
	baseURL    string
	apiKey     string
	httpClient *http.Client
}

// NewClient creates a new TruthMark client
func NewClient(config *Config) *Client {
	if config == nil {
		config = &Config{
			BaseURL: "http://localhost:8000",
			Timeout: 30 * time.Second,
		}
	}

	if config.Timeout == 0 {
		config.Timeout = 30 * time.Second
	}

	return &Client{
		baseURL: config.BaseURL,
		apiKey:  config.APIKey,
		httpClient: &http.Client{
			Timeout: config.Timeout,
		},
	}
}

// Encode embeds an invisible watermark into an image
func (c *Client) Encode(imagePath, message string) (*EncodeResult, error) {
	// Open image file
	file, err := os.Open(imagePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open image: %w", err)
	}
	defer file.Close()

	// Create multipart form
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	// Add file
	part, err := writer.CreateFormFile("file", filepath.Base(imagePath))
	if err != nil {
		return nil, err
	}
	if _, err := io.Copy(part, file); err != nil {
		return nil, err
	}

	// Add message
	if err := writer.WriteField("message", message); err != nil {
		return nil, err
	}

	contentType := writer.FormDataContentType()
	writer.Close()

	// Create request
	req, err := http.NewRequest("POST", c.baseURL+"/v1/encode", body)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Content-Type", contentType)
	if c.apiKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.apiKey)
	}

	// Execute request
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API error: %d", resp.StatusCode)
	}

	// Parse response
	var result EncodeResult
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return &result, nil
}

// Decode extracts watermark from an image
func (c *Client) Decode(imagePath string) (*DecodeResult, error) {
	// Open image file
	file, err := os.Open(imagePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open image: %w", err)
	}
	defer file.Close()

	// Create multipart form
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	part, err := writer.CreateFormFile("file", filepath.Base(imagePath))
	if err != nil {
		return nil, err
	}
	if _, err := io.Copy(part, file); err != nil {
		return nil, err
	}

	contentType := writer.FormDataContentType()
	writer.Close()

	// Create request
	req, err := http.NewRequest("POST", c.baseURL+"/v1/decode", body)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Content-Type", contentType)
	if c.apiKey != "" {
		req.Header.Set("Authorization", "Bearer "+c.apiKey)
	}

	// Execute request
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API error: %d", resp.StatusCode)
	}

	// Parse response
	var result DecodeResult
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return &result, nil
}
