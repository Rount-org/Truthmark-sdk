using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Threading.Tasks;

namespace TruthMark.SDK
{
    public class TruthMarkConfig
    {
        public string BaseUrl { get; set; } = "http://localhost:8000";
        public string ApiKey { get; set; }
        public int TimeoutSeconds { get; set; } = 30;
    }

    public class EncodeResult
    {
        public string Status { get; set; }
        public Metadata MetaData { get; set; }
        public string DownloadUrl { get; set; }

        public class Metadata
        {
            public double Psnr { get; set; }
            public int BitsEmbedded { get; set; }
        }
    }

    public class DecodeResult
    {
        public bool Found { get; set; }
        public string Message { get; set; }
        public double Confidence { get; set; }
    }

    public class TruthMarkClient : IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly string _baseUrl;
        private readonly string _apiKey;

        public TruthMarkClient() : this(new TruthMarkConfig()) { }

        public TruthMarkClient(TruthMarkConfig config)
        {
            _baseUrl = config.BaseUrl;
            _apiKey = config.ApiKey;
            _httpClient = new HttpClient
            {
                Timeout = TimeSpan.FromSeconds(config.TimeoutSeconds)
            };
        }

        /// <summary>
        /// Embed an invisible watermark into an image
        /// </summary>
        public async Task<EncodeResult> EncodeAsync(string imagePath, string message)
        {
            if (!File.Exists(imagePath))
            {
                throw new FileNotFoundException($"Image file not found: {imagePath}");
            }

            using var form = new MultipartFormDataContent();
            using var fileStream = File.OpenRead(imagePath);
            using var fileContent = new StreamContent(fileStream);
            
            fileContent.Headers.ContentType = MediaTypeHeaderValue.Parse("image/png");
            form.Add(fileContent, "file", Path.GetFileName(imagePath));
            form.Add(new StringContent(message), "message");

            var request = new HttpRequestMessage(HttpMethod.Post, $"{_baseUrl}/v1/encode")
            {
                Content = form
            };

            if (!string.IsNullOrEmpty(_apiKey))
            {
                request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", _apiKey);
            }

            var response = await _httpClient.SendAsync(request);
            response.EnsureSuccessStatusCode();

            var responseBody = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<EncodeResult>(responseBody);
        }

        /// <summary>
        /// Extract watermark from an image
        /// </summary>
        public async Task<DecodeResult> DecodeAsync(string imagePath)
        {
            if (!File.Exists(imagePath))
            {
                throw new FileNotFoundException($"Image file not found: {imagePath}");
            }

            using var form = new MultipartFormDataContent();
            using var fileStream = File.OpenRead(imagePath);
            using var fileContent = new StreamContent(fileStream);
            
            fileContent.Headers.ContentType = MediaTypeHeaderValue.Parse("image/png");
            form.Add(fileContent, "file", Path.GetFileName(imagePath));

            var request = new HttpRequestMessage(HttpMethod.Post, $"{_baseUrl}/v1/decode")
            {
                Content = form
            };

            if (!string.IsNullOrEmpty(_apiKey))
            {
                request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", _apiKey);
            }

            var response = await _httpClient.SendAsync(request);
            response.EnsureSuccessStatusCode();

            var responseBody = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<DecodeResult>(responseBody);
        }

        public void Dispose()
        {
            _httpClient?.Dispose();
        }
    }
}
