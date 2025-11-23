require 'net/http'
require 'uri'
require 'json'

module TruthMark
  class Client
    DEFAULT_BASE_URL = 'http://localhost:8000'.freeze

    attr_reader :base_url, :api_key

    def initialize(base_url: DEFAULT_BASE_URL, api_key: nil)
      @base_url = base_url
      @api_key = api_key
    end

    # Embed an invisible watermark into an image
    # @param image_path [String] Path to input image
    # @param message [String] Text to embed (max 500 chars)
    # @return [Hash] Encode result with metadata
    def encode(image_path, message)
      raise ArgumentError, "Image file not found: #{image_path}" unless File.exist?(image_path)

      uri = URI.parse("#{base_url}/v1/encode")
      request = build_request(uri)

      request.set_form(
        [
          ['file', File.open(image_path)],
          ['message', message]
        ],
        'multipart/form-data'
      )

      execute_request(uri, request)
    end

    # Extract watermark from an image
    # @param image_path [String] Path to watermarked image
    # @return [Hash] Decode result with message and confidence
    def decode(image_path)
      raise ArgumentError, "Image file not found: #{image_path}" unless File.exist?(image_path)

      uri = URI.parse("#{base_url}/v1/decode")
      request = build_request(uri)

      request.set_form(
        [['file', File.open(image_path)]],
        'multipart/form-data'
      )

      execute_request(uri, request)
    end

    private

    def build_request(uri)
      request = Net::HTTP::Post.new(uri)
      request['Authorization'] = "Bearer #{api_key}" if api_key
      request
    end

    def execute_request(uri, request)
      response = Net::HTTP.start(uri.hostname, uri.port, use_ssl: uri.scheme == 'https') do |http|
        http.request(request)
      end

      raise "API Error: #{response.code}" unless response.is_a?(Net::HTTPSuccess)

      JSON.parse(response.body, symbolize_names: true)
    end
  end
end
