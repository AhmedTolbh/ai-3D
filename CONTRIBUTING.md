# Contributing to Virtual Receptionist Avatar

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🎯 Ways to Contribute

- **Bug Reports**: Found a bug? Let us know!
- **Feature Requests**: Have an idea? We'd love to hear it!
- **Code Contributions**: Submit pull requests for bug fixes or new features
- **Documentation**: Improve README, add examples, fix typos
- **Testing**: Test the application and report issues
- **Translations**: Add support for more languages

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/ai-3D.git
cd ai-3D
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys
```

### 3. Create a Branch

```bash
# Create a new branch for your feature
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

## 📝 Development Guidelines

### Code Style

**Python:**
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small
- Use type hints where appropriate

```python
def process_audio(audio_data: bytes) -> dict:
    """
    Process audio data and return transcription.
    
    Args:
        audio_data: Raw audio bytes
        
    Returns:
        Dictionary with transcription and confidence
    """
    # Implementation
```

**JavaScript:**
- Use consistent indentation (2 or 4 spaces)
- Use camelCase for variables and functions
- Add JSDoc comments for complex functions
- Use async/await for asynchronous operations

```javascript
/**
 * Process recorded audio and send to backend
 * @returns {Promise<void>}
 */
async function processRecording() {
    // Implementation
}
```

### Testing

Before submitting:

```bash
# Test syntax
python -m py_compile app.py

# Run setup test
python test_setup.py

# Test manually with browser
python app.py
# Open http://localhost:5000
```

### Commit Messages

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "Add support for Spanish language"
git commit -m "Fix microphone permission error on Safari"
git commit -m "Update README with Docker instructions"

# Avoid
git commit -m "fix bug"
git commit -m "update"
git commit -m "changes"
```

## 🐛 Reporting Bugs

When reporting bugs, include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Detailed steps to reproduce the bug
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**:
   - OS (Windows/Mac/Linux)
   - Python version
   - Browser and version
   - Any error messages

**Example:**

```markdown
### Bug: Speech recognition not working on Firefox

**Steps to Reproduce:**
1. Open application in Firefox 115
2. Click "Talk to Receptionist"
3. Grant microphone permission
4. Speak into microphone
5. Click "Stop Recording"

**Expected:** Transcription should appear
**Actual:** Error: "No speech detected"

**Environment:**
- OS: Windows 11
- Python: 3.11.0
- Browser: Firefox 115.0
- Error in console: "MediaRecorder not supported"
```

## 💡 Suggesting Features

When suggesting features:

1. **Use Case**: Explain why this feature is needed
2. **Description**: Describe the feature in detail
3. **Examples**: Provide examples of how it would work
4. **Alternatives**: Any alternative solutions considered

## 🔧 Pull Request Process

### 1. Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### 2. Submit Pull Request

1. Push your branch to your fork
2. Go to the original repository
3. Click "New Pull Request"
4. Select your branch
5. Fill out the PR template

### 3. PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
How has this been tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

### 4. Review Process

- Maintainers will review your PR
- Address any requested changes
- Once approved, PR will be merged

## 🎨 UI/UX Contributions

When contributing to the frontend:

- Maintain responsive design
- Ensure accessibility (ARIA labels, keyboard navigation)
- Test on multiple browsers
- Keep the design clean and professional
- Add loading states for async operations

## 🌍 Adding Language Support

To add a new language:

### 1. Update Backend (app.py)

```python
# Add language code to voice_params
voice_params = {
    'en-US': ('en-US', texttospeech.SsmlVoiceGender.FEMALE, 'en-US-Neural2-F'),
    'fi-FI': ('fi-FI', texttospeech.SsmlVoiceGender.FEMALE, 'fi-FI-Standard-A'),
    'ar-SA': ('ar-XA', texttospeech.SsmlVoiceGender.FEMALE, 'ar-XA-Standard-A'),
    'es-ES': ('es-ES', texttospeech.SsmlVoiceGender.FEMALE, 'es-ES-Standard-A'),  # Spanish
}

# Update alternative_language_codes
config = speech.RecognitionConfig(
    # ...
    alternative_language_codes=["fi-FI", "ar-SA", "es-ES"],  # Add new language
)
```

### 2. Update Documentation

- Add to README language list
- Update examples if needed

### 3. Test

- Test speech recognition in the new language
- Test TTS output quality
- Verify avatar lip-sync works well

## 🔒 Security

**DO NOT:**
- Commit API keys or credentials
- Include `.env` files
- Share sensitive data in issues/PRs
- Introduce security vulnerabilities

**If you find a security issue:**
- Do NOT create a public issue
- Email the maintainers directly
- Provide details and reproduction steps

## 📚 Documentation Contributions

Documentation improvements are always welcome:

- Fix typos and grammar
- Add examples
- Improve clarity
- Add diagrams or screenshots
- Translate to other languages

## 🏆 Recognition

Contributors will be:
- Listed in the project README
- Mentioned in release notes
- Credited in commit history

## ❓ Questions?

- Check existing issues
- Read the documentation
- Ask in discussions

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to Virtual Receptionist Avatar! 🎉
