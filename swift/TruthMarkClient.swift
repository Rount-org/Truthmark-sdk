import Foundation

public struct TruthMarkConfig {
    public var baseURL: String
    public var apiKey: String?
    public var timeout: TimeInterval
    
    public init(
        baseURL: String = "http://localhost:8000",
        apiKey: String? = nil,
        timeout: TimeInterval = 30
    ) {
        self.baseURL = baseURL
        self.apiKey = apiKey
        self.timeout = timeout
    }
}

public struct EncodeResult: Codable {
    public let status: String
    public let metadata: Metadata
    public let downloadUrl: String
    
    public struct Metadata: Codable {
        public let psnr: Double
        public let bitsEmbedded: Int
        
        enum CodingKeys: String, CodingKey {
            case psnr
            case bitsEmbedded = "bits_embedded"
        }
    }
    
    enum CodingKeys: String, CodingKey {
        case status, metadata
        case downloadUrl = "download_url"
    }
}

public struct DecodeResult: Codable {
    public let found: Bool
    public let message: String?
    public let confidence: Double
}

public enum TruthMarkError: Error {
    case fileNotFound
    case networkError(Error)
    case apiError(Int, String)
    case decodingError
}

public class TruthMarkClient {
    private let config: TruthMarkConfig
    private let session: URLSession
    
    public init(config: TruthMarkConfig = TruthMarkConfig()) {
        self.config = config
        
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = config.timeout
        self.session = URLSession(configuration: configuration)
    }
    
    /// Embed an invisible watermark into an image
    public func encode(imagePath: String, message: String) async throws -> EncodeResult {
        guard FileManager.default.fileExists(atPath: imagePath) else {
            throw TruthMarkError.fileNotFound
        }
        
        guard let url = URL(string: "\(config.baseURL)/v1/encode") else {
            throw TruthMarkError.apiError(0, "Invalid URL")
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        if let apiKey = config.apiKey {
            request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        }
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        let imageData = try Data(contentsOf: URL(fileURLWithPath: imagePath))
        let fileName = URL(fileURLWithPath: imagePath).lastPathComponent
        
        var body = Data()
        
        // Add file
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/png\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n".data(using: .utf8)!)
        
        // Add message
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"message\"\r\n\r\n".data(using: .utf8)!)
        body.append(message.data(using: .utf8)!)
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw TruthMarkError.networkError(NSError(domain: "Invalid response", code: 0))
            }
            
            guard httpResponse.statusCode == 200 else {
                throw TruthMarkError.apiError(httpResponse.statusCode, "API Error")
            }
            
            let decoder = JSONDecoder()
            return try decoder.decode(EncodeResult.self, from: data)
        } catch let error as TruthMarkError {
            throw error
        } catch {
            throw TruthMarkError.networkError(error)
        }
    }
    
    /// Extract watermark from an image
    public func decode(imagePath: String) async throws -> DecodeResult {
        guard FileManager.default.fileExists(atPath: imagePath) else {
            throw TruthMarkError.fileNotFound
        }
        
        guard let url = URL(string: "\(config.baseURL)/v1/decode") else {
            throw TruthMarkError.apiError(0, "Invalid URL")
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        if let apiKey = config.apiKey {
            request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        }
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        let imageData = try Data(contentsOf: URL(fileURLWithPath: imagePath))
        let fileName = URL(fileURLWithPath: imagePath).lastPathComponent
        
        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/png\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw TruthMarkError.networkError(NSError(domain: "Invalid response", code: 0))
            }
            
            guard httpResponse.statusCode == 200 else {
                throw TruthMarkError.apiError(httpResponse.statusCode, "API Error")
            }
            
            let decoder = JSONDecoder()
            return try decoder.decode(DecodeResult.self, from: data)
        } catch let error as TruthMarkError {
            throw error
        } catch {
            throw TruthMarkError.networkError(error)
        }
    }
}
