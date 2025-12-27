# Security Policy

## Supported Versions

<<<<<<< HEAD
We actively support the following versions of TruthMark SDK:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**DO NOT** open a public issue for security vulnerabilities.

Instead, please report security vulnerabilities to:
- **Email**: security@truthmark.com
- **Response Time**: Within 48 hours

### What to Include

Please include the following in your report:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)
5. Your name/handle for credit (optional)

### What Happens Next

1. **Acknowledgment**: We'll respond within 48 hours
2. **Investigation**: We'll investigate and determine severity
3. **Fix**: We'll develop and test a patch
4. **Disclosure**: We'll coordinate disclosure with you
5. **Credit**: We'll credit you in the security advisory (if you wish)

### Security Bug Bounty

We currently do not have a bug bounty program, but we greatly appreciate responsible disclosure and will acknowledge your contribution.

## Security Best Practices for SDK Users

### API Key Management
- **Never** commit API keys to version control
- Use environment variables or secure secret managers
- Rotate keys regularly
- Use different keys for development and production

### Image Handling
- Validate image inputs before processing
- Implement rate limiting to prevent abuse
- Sanitize user-provided messages before embedding
- Use HTTPS for all API communications

### Production Deployment
```python
# ✅ Good - Using environment variables
import os
client = TruthMarkClient(api_key=os.environ['TRUTHMARK_API_KEY'])

# ❌ Bad - Hardcoded key
client = TruthMarkClient(api_key='sk_live_abc123xyz')
```

## Known Security Considerations

### Watermark Extraction
- Watermark extraction requires the encryption key
- Without the key, watermarks cannot be extracted
- Store encryption keys securely (use AWS KMS, Azure Key Vault, etc.)

### Data Privacy
- TruthMark API does not store uploaded images
- All processing is ephemeral (in-memory only)
- Watermark metadata is logged for debugging (disable in production)

## Security Updates

Subscribe to security updates:
- **GitHub**: Watch this repository for security advisories
- **Email**: security-announce@truthmark.com
- **RSS**: https://github.com/Round-Tech/TruthMark-SDK/security/advisories.atom

## Compliance

TruthMark SDK is designed to comply with:
- GDPR (EU data protection)
- CCPA (California privacy law)
- SOC 2 Type II (in progress)
- ISO 27001 (in progress)

---

**Last Updated**: December 27, 2025  
**Version**: 1.0
=======
Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 5.1.x   | :white_check_mark: |
| 5.0.x   | :x:                |
| 4.0.x   | :white_check_mark: |
| < 4.0   | :x:                |

## Reporting a Vulnerability

Use this section to tell people how to report a vulnerability.

Tell them where to go, how often they can expect to get an update on a
reported vulnerability, what to expect if the vulnerability is accepted or
declined, etc.
>>>>>>> 1a7ead59a2110f95087b72f10e8e1e1c5ccb7aeb
