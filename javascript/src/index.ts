/**
 * TruthMark SDK for JavaScript/TypeScript
 * Official client for TruthMark API
 */

interface TruthMarkConfig {
    apiKey?: string;
    baseUrl?: string;
}

interface EncodeResult {
    status: string;
    metadata: {
        psnr: number;
        bits_embedded: number;
    };
    download_url: string;
}

interface DecodeResult {
    found: boolean;
    message: string | null;
    confidence: number;
}

export class TruthMarkClient {
    private apiKey: string | null;
    private baseUrl: string;

    constructor(config: TruthMarkConfig = {}) {
        this.apiKey = config.apiKey || null;
        this.baseUrl = config.baseUrl || 'http://localhost:8000';
    }

    async encode(
        imagePath: string | File | Blob,
        message: string
    ): Promise<EncodeResult> {
        const formData = new FormData();

        if (typeof imagePath === 'string') {
            // Node.js environment
            const fs = require('fs');
            const path = require('path');
            const FormData = require('form-data');

            const form = new FormData();
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

    async decode(imagePath: string | File | Blob): Promise<DecodeResult> {
        const formData = new FormData();

        if (typeof imagePath === 'string') {
            // Node.js environment
            const fs = require('fs');
            const FormData = require('form-data');

            const form = new FormData();
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

export default TruthMarkClient;
