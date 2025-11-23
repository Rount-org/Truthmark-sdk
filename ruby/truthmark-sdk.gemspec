Gem::Specification.new do |spec|
  spec.name          = "truthmark-sdk"
  spec.version       = "1.0.0"
  spec.authors       = ["TruthMark Team"]
  spec.email         = ["contact.darkmintis@gmail.com"]

  spec.summary       = "Official Ruby SDK for TruthMark invisible watermarking"
  spec.description   = "Embed and extract invisible watermarks using the TruthMark API"
  spec.homepage      = "https://truthmark.com"
  spec.license       = "MIT"

  spec.files         = Dir["lib/**/*", "README.md"]
  spec.require_paths = ["lib"]

  spec.required_ruby_version = ">= 2.7.0"

  # No external dependencies - uses standard library only
end
