/**
 * TruthMark SDK for JavaScript
 * Official client for TruthMark API - Pure JavaScript implementation
 * @module @truthmark/sdk-javascript
 */

/**
 * Configuration options for TruthMark client
 * @typedef {Object} TruthMarkConfig
 * @property {string} [apiKey] - Optional API key for authentication
 * @property {string} [baseUrl='http://localhost:8000'] - Base URL for TruthMark API
 */

/**
 * Result from encoding operation
 * @typedef {Object} EncodeResult
 * @property {string} status - Status of the operation
 * @property {Object} metadata - Encoding metadata
 * @property {number} metadata.psnr - Peak Signal-to-Noise Ratio
 * @property {number} metadata.bits_embedded - Number of bits embedded
 * @property {string} download_url - URL to download encoded image
 */

/**
 * Result from decoding operation
 * @typedef {Object} DecodeResult
 * @property {boolean} found - Whether watermark was found
 * @property {string|null} message - Extracted message
 * @property {number} confidence - Confidence score (0-1)
 */

/**
 * TruthMark client for watermark encoding and decoding
 */
class TruthMarkClient {
    /**
     * Create a new TruthMark client
     * @param {TruthMarkConfig} [config={}] - Configuration options
     */
    constructor(config = {}) {
        this.apiKey = config.apiKey || null;
        this.baseUrl = config.baseUrl || 'http://localhost:8000';
    }

    /**
     * Encode an invisible watermark into an image
     * @param {string|File|Blob} imagePath - Path to image file (Node.js) or File/Blob object (Browser)
     * @param {string} message - Message to embed in the watermark
     * @returns {Promise<EncodeResult>} Encoding result with metadata
     * @throws {Error} If API request fails
     */
    async encode(imagePath, message) {
        if (typeof imagePath === 'string') {
            // Node.js environment
            const fs = await import('node:fs');
            const FormDataNode = await import('form-data');

            const form = new FormDataNode.default();
            form.append('file', fs.createReadStream(imagePath));
            form.append('message', message);

            const response = await fetch(`${this.baseUrl}/v1/encode`, {
                method: 'POST',
                body: form,
                headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {}
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            return response.json();
        } else {
            // Browser environment
            const formData = new FormData();
            formData.append('file', imagePath);
            formData.append('message', message);

            const response = await fetch(`${this.baseUrl}/v1/encode`, {
                method: 'POST',
                body: formData,
                headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {}
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            return response.json();
        }
    }

    /**
     * Decode watermark from an image
     * @param {string|File|Blob} imagePath - Path to image file (Node.js) or File/Blob object (Browser)
     * @returns {Promise<DecodeResult>} Decoding result with extracted message
     * @throws {Error} If API request fails
     */
    async decode(imagePath) {
        if (typeof imagePath === 'string') {
            // Node.js environment
            const fs = await import('node:fs');
            const FormDataNode = await import('form-data');

            const form = new FormDataNode.default();
            form.append('file', fs.createReadStream(imagePath));

            const response = await fetch(`${this.baseUrl}/v1/decode`, {
                method: 'POST',
                body: form,
                headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {}
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            return response.json();
        } else {
            // Browser environment
            const formData = new FormData();
            formData.append('file', imagePath);

            const response = await fetch(`${this.baseUrl}/v1/decode`, {
                method: 'POST',
                body: formData,
                headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {}
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            return response.json();
        }
    }
}

// Export for both CommonJS and ES modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TruthMarkClient };
    module.exports.default = TruthMarkClient;
}

export { TruthMarkClient };
export default TruthMarkClient;
