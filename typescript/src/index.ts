/// <reference lib="dom" />
/// <reference lib="dom.iterable" />

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

interface VerifyResult {
    watermarked: boolean;
    confidence: number;
    sync_confidence: number;
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
        if (typeof imagePath === 'string') {
            // Node.js environment
            const fs = await import('node:fs');
            const path = await import('node:path');
            const FormDataNode = await import('form-data');

            const form = new FormDataNode.default();
            form.append('file', fs.createReadStream(imagePath));
            form.append('message', message);

            const response = await fetch(`${this.baseUrl}/v1/encode`, {
                method: 'POST',
                body: form as any,
                headers: this.apiKey ? { 'X-API-Key': this.apiKey } : {}
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
                headers: this.apiKey ? { 'X-API-Key': this.apiKey } : {}
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            return response.json();
        }
    }

    async decode(imagePath: string | File | Blob): Promise<DecodeResult> {
        if (typeof imagePath === 'string') {
            // Node.js environment
            const fs = await import('node:fs');
            const FormDataNode = await import('form-data');

            const form = new FormDataNode.default();
            form.append('file', fs.createReadStream(imagePath));

            const response = await fetch(`${this.baseUrl}/v1/decode`, {
                method: 'POST',
                body: form as any,
                headers: this.apiKey ? { 'X-API-Key': this.apiKey } : {}
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
                headers: this.apiKey ? { 'X-API-Key': this.apiKey } : {}
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            return response.json();
        }
    }

    async verify(imagePath: string | File | Blob): Promise<VerifyResult> {
        if (typeof imagePath === 'string') {
            const fs = await import('node:fs');
            const FormDataNode = await import('form-data');
            const form = new FormDataNode.default();
            form.append('file', fs.createReadStream(imagePath));

            const response = await fetch(`${this.baseUrl}/v1/verify`, {
                method: 'POST',
                body: form as any,
                headers: this.apiKey ? { 'X-API-Key': this.apiKey } : {}
            });

            if (!response.ok) throw new Error(`API Error: ${response.status}`);
            return response.json();
        } else {
            const formData = new FormData();
            formData.append('file', imagePath);

            const response = await fetch(`${this.baseUrl}/v1/verify`, {
                method: 'POST',
                body: formData,
                headers: this.apiKey ? { 'X-API-Key': this.apiKey } : {}
            });

            if (!response.ok) throw new Error(`API Error: ${response.status}`);
            return response.json();
        }
    }
}

export default TruthMarkClient;
