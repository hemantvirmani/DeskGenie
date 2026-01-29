# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x  | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously and appreciate your efforts to responsibly disclose vulnerabilities.

### How to Report

If you discover a security vulnerability, please do **NOT** open a public issue. Instead, send an email to the project maintainer privately.

**Email**: [Your Email Here] - *Replace with actual email before publishing*

### What to Include

When reporting a vulnerability, please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Suggested fix (if known)
- Your contact information

### What to Expect

- We will acknowledge receipt of your report within 48 hours
- We will provide a detailed response within 7 days regarding the next steps
- We will work with you to understand and resolve the issue
- We will notify you when the fix is deployed
- We will credit you in the security advisory (unless you prefer otherwise)

## Security Best Practices

### For Users

1. **Never commit API keys or secrets** to the repository
2. **Use environment variables** for sensitive configuration
3. **Keep dependencies updated** regularly
4. **Review file operations** before executing them
5. **Backup important files** before using manipulation tools
6. **Run in isolated environment** if handling sensitive data
7. **Review the source code** before running from untrusted sources

### For Developers

1. **Never hardcode credentials** in source code
2. **Use environment variables** for all secrets
3. **Validate all user inputs** before processing
4. **Sanitize file paths** to prevent directory traversal
5. **Limit file size** uploads and processing
6. **Use secure file handling** practices
7. **Review dependencies** for known vulnerabilities
8. **Follow principle of least privilege** for file access

### File Operation Safety

DeskGenie performs file system operations. Keep in mind:

- **Always backup** before batch operations
- **Verify paths** before file manipulations
- **Check file sizes** before processing large files
- **Review tool parameters** before execution
- **Use output directory** for generated files
- **Be cautious with delete operations**

### API Key Security

When using Google Gemini API:

- **Never share** your API key publicly
- **Store keys** in environment variables only
- **Rotate keys** regularly if exposed
- **Use separate keys** for different environments
- **Monitor usage** for suspicious activity
- **Set usage limits** in Google Cloud Console

### Network Security

When using web search and research tools:

- **Connections are encrypted** (HTTPS)
- **No sensitive data** is sent to third parties
- **Web APIs** are used for information retrieval only
- **User files** are never uploaded to external services
- **All processing** happens locally on your machine

## Known Security Considerations

### File System Access

- DeskGenie requires access to local file system to perform operations
- File paths should be validated to prevent path traversal attacks
- Output files are created in configured output directory
- Users should review operations before execution

### API Usage

- Google Gemini API calls require an API key
- API key should be stored in environment variables
- Usage is tracked by Google Cloud Platform
- Users should monitor their API usage

### Third-Party Dependencies

- Project uses various Python and Node.js packages
- Dependencies should be kept up to date
- Regular security audits are recommended
- Review `requirements.txt` and `package.json` regularly

### Web Tools

- Web search and research tools make HTTP requests
- No sensitive information is sent to external services
- Wikipedia, ArXiv, and DuckDuckGo are public services
- No authentication is required for these services

## Secure Development Practices

### Code Review

- All code changes should be reviewed
- Pay special attention to file operations
- Validate all user inputs
- Check for potential injection attacks

### Dependency Management

- Regularly update dependencies
- Use `pip audit` to check for vulnerabilities
- Monitor security advisories for dependencies
- Remove unused dependencies

### Testing

- Test with various file types and sizes
- Test with edge cases and invalid inputs
- Verify error handling
- Test file permission scenarios

## Disclosure Policy

- Security vulnerabilities will be disclosed responsibly
- Users will be notified of security updates
- Security advisories will be published
- Credit will be given to reporters (with permission)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Questions?

If you have questions about security:

- Review this document thoroughly
- Check open issues for similar discussions
- Open a security discussion (not a public issue)
- Contact the maintainers privately for sensitive concerns

---

**Remember**: Security is everyone's responsibility. If you see something, say something!