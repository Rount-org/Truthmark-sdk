package com.truthmark.sdk

import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.asRequestBody
import com.google.gson.Gson
import java.io.File
import java.io.IOException
import java.util.concurrent.TimeUnit

data class TruthMarkConfig(
    val baseUrl: String = "http://localhost:8000",
    val apiKey: String? = null,
    val timeoutSeconds: Long = 30
)

data class EncodeResult(
    val status: String,
    val metadata: Metadata,
    val download_url: String
) {
    data class Metadata(
        val psnr: Double,
        val bits_embedded: Int
    )
}

data class DecodeResult(
    val found: Boolean,
    val message: String?,
    val confidence: Double
)

class TruthMarkClient(config: TruthMarkConfig = TruthMarkConfig()) {
    private val baseUrl = config.baseUrl
    private val apiKey = config.apiKey
    private val httpClient: OkHttpClient
    private val gson = Gson()

    init {
        httpClient = OkHttpClient.Builder()
            .connectTimeout(config.timeoutSeconds, TimeUnit.SECONDS)
            .readTimeout(config.timeoutSeconds, TimeUnit.SECONDS)
            .build()
    }

    /**
     * Embed an invisible watermark into an image
     * @param imagePath Path to input image
     * @param message Text to embed (max 500 chars)
     * @return EncodeResult with metadata and download URL
     */
    @Throws(IOException::class)
    fun encode(imagePath: String, message: String): EncodeResult {
        val imageFile = File(imagePath)
        if (!imageFile.exists()) {
            throw IOException("Image file not found: $imagePath")
        }

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "file",
                imageFile.name,
                imageFile.asRequestBody("image/*".toMediaTypeOrNull())
            )
            .addFormDataPart("message", message)
            .build()

        val requestBuilder = Request.Builder()
            .url("$baseUrl/v1/encode")
            .post(requestBody)

        apiKey?.let {
            requestBuilder.addHeader("Authorization", "Bearer $it")
        }

        val response = httpClient.newCall(requestBuilder.build()).execute()

        if (!response.isSuccessful) {
            throw IOException("API Error: ${response.code}")
        }

        val responseBody = response.body?.string()
            ?: throw IOException("Empty response body")

        return gson.fromJson(responseBody, EncodeResult::class.java)
    }

    /**
     * Extract watermark from an image
     * @param imagePath Path to watermarked image
     * @return DecodeResult with extracted message
     */
    @Throws(IOException::class)
    fun decode(imagePath: String): DecodeResult {
        val imageFile = File(imagePath)
        if (!imageFile.exists()) {
            throw IOException("Image file not found: $imagePath")
        }

        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "file",
                imageFile.name,
                imageFile.asRequestBody("image/*".toMediaTypeOrNull())
            )
            .build()

        val requestBuilder = Request.Builder()
            .url("$baseUrl/v1/decode")
            .post(requestBody)

        apiKey?.let {
            requestBuilder.addHeader("Authorization", "Bearer $it")
        }

        val response = httpClient.newCall(requestBuilder.build()).execute()

        if (!response.isSuccessful) {
            throw IOException("API Error: ${response.code}")
        }

        val responseBody = response.body?.string()
            ?: throw IOException("Empty response body")

        return gson.fromJson(responseBody, DecodeResult::class.java)
    }
}
