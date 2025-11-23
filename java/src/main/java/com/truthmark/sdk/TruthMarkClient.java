package com.truthmark.sdk;

import okhttp3.*;
import com.google.gson.Gson;

import java.io.File;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

/**
 * TruthMark SDK for Java
 * Official client for invisible watermarking
 */
public class TruthMarkClient {
    private final String baseUrl;
    private final String apiKey;
    private final OkHttpClient httpClient;
    private final Gson gson;

    public static class Config {
        public String baseUrl = "http://localhost:8000";
        public String apiKey = null;
        public int timeoutSeconds = 30;
    }

    public static class EncodeResult {
        public String status;
        public Metadata metadata;
        public String download_url;

        public static class Metadata {
            public double psnr;
            public int bits_embedded;
        }
    }

    public static class DecodeResult {
        public boolean found;
        public String message;
        public double confidence;
    }

    public TruthMarkClient() {
        this(new Config());
    }

    public TruthMarkClient(Config config) {
        this.baseUrl = config.baseUrl;
        this.apiKey = config.apiKey;
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(config.timeoutSeconds, TimeUnit.SECONDS)
                .readTimeout(config.timeoutSeconds, TimeUnit.SECONDS)
                .build();
        this.gson = new Gson();
    }

    /**
     * Embed an invisible watermark into an image
     * 
     * @param imagePath Path to input image
     * @param message   Text to embed (max 500 chars)
     * @return EncodeResult with metadata and download URL
     */
    public EncodeResult encode(String imagePath, String message) throws IOException {
        File imageFile = new File(imagePath);
        if (!imageFile.exists()) {
            throw new IOException("Image file not found: " + imagePath);
        }

        RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", imageFile.getName(),
                        RequestBody.create(imageFile, MediaType.parse("image/*")))
                .addFormDataPart("message", message)
                .build();

        Request.Builder requestBuilder = new Request.Builder()
                .url(baseUrl + "/v1/encode")
                .post(requestBody);

        if (apiKey != null) {
            requestBuilder.addHeader("Authorization", "Bearer " + apiKey);
        }

        try (Response response = httpClient.newCall(requestBuilder.build()).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("API Error: " + response.code());
            }

            String responseBody = response.body().string();
            return gson.fromJson(responseBody, EncodeResult.class);
        }
    }

    /**
     * Extract watermark from an image
     * 
     * @param imagePath Path to watermarked image
     * @return DecodeResult with extracted message
     */
    public DecodeResult decode(String imagePath) throws IOException {
        File imageFile = new File(imagePath);
        if (!imageFile.exists()) {
            throw new IOException("Image file not found: " + imagePath);
        }

        RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", imageFile.getName(),
                        RequestBody.create(imageFile, MediaType.parse("image/*")))
                .build();

        Request.Builder requestBuilder = new Request.Builder()
                .url(baseUrl + "/v1/decode")
                .post(requestBody);

        if (apiKey != null) {
            requestBuilder.addHeader("Authorization", "Bearer " + apiKey);
        }

        try (Response response = httpClient.newCall(requestBuilder.build()).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("API Error: " + response.code());
            }

            String responseBody = response.body().string();
            return gson.fromJson(responseBody, DecodeResult.class);
        }
    }
}
