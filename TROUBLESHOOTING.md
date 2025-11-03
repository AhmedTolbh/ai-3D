# Troubleshooting Guide

## Virtual Receptionist Avatar - Common Issues and Solutions

---

## Installation Issues

### 1. Python Version Error

**Problem:** `Python version too old` or `Command not found: python3`

**Solution:**
- Install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
- Verify installation: `python3 --version`
- On Windows, ensure Python is added to PATH during installation

### 2. Pip Install Failures

**Problem:** Errors during `pip install -r requirements.txt`

**Solutions:**

**Missing compiler (Windows):**
```bash
# Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

**Permission denied (Linux/Mac):**
```bash
# Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or use --user flag
pip install --user -r requirements.txt
```

**Specific package fails:**
```bash
# Try upgrading pip first
pip install --upgrade pip setuptools wheel

# Then retry
pip install -r requirements.txt
```

---

## API Configuration Issues

### 3. Google Cloud Credentials Error

**Problem:** `Could not automatically determine credentials`

**Solutions:**

**Check credentials file path:**
```bash
# Verify file exists
ls -l path/to/google-cloud-credentials.json

# Check .env file
cat .env | grep GOOGLE_APPLICATION_CREDENTIALS
```

**Set environment variable manually:**
```bash
# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/credentials.json"

# Windows (Command Prompt)
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\credentials.json

# Windows (PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\credentials.json"
```

**Verify credentials are valid:**
```python
from google.cloud import speech
client = speech.SpeechClient()
print("Credentials working!")
```

### 4. Gemini API Key Invalid

**Problem:** `Invalid API key` or `API key not valid`

**Solutions:**
1. Get a new API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Ensure no extra spaces in `.env` file:
   ```
   GEMINI_API_KEY=your_key_here
   # NOT: GEMINI_API_KEY = your_key_here (spaces around =)
   ```
3. Verify key in Python:
   ```python
   import os
   from dotenv import load_dotenv
   load_dotenv()
   print(os.getenv('GEMINI_API_KEY'))
   ```

### 5. D-ID API Errors

**Problem:** `401 Unauthorized` or `Invalid API key`

**Solutions:**
1. Verify API key format (should be base64)
2. Check D-ID account credits
3. Ensure proper authorization header format:
   ```python
   headers = {
       "authorization": f"Basic {DID_API_KEY}"
   }
   ```

---

## Runtime Issues

### 6. Microphone Access Denied

**Problem:** Cannot record audio in browser

**Solutions:**

**Chrome/Edge:**
1. Click the lock icon in address bar
2. Set "Microphone" to "Allow"
3. Reload the page

**Firefox:**
1. Click the permissions icon (left of address bar)
2. Enable microphone access
3. Reload the page

**HTTPS Required:**
- Modern browsers require HTTPS for microphone access
- For local testing, `localhost` is allowed
- For production, use HTTPS/SSL

### 7. No Speech Detected

**Problem:** Speech-to-Text returns "No speech detected"

**Solutions:**
1. **Check microphone input:**
   - Test in system settings
   - Ensure correct microphone is selected
   
2. **Speak clearly:**
   - Moderate pace
   - Clear pronunciation
   - Reduce background noise
   
3. **Recording duration:**
   - Speak for at least 1-2 seconds
   - Don't stop recording too quickly

4. **Audio format issues:**
   ```javascript
   // Try different MIME types
   const options = { mimeType: 'audio/webm;codecs=opus' };
   mediaRecorder = new MediaRecorder(stream, options);
   ```

### 8. Video Generation Timeout

**Problem:** Video takes too long or times out

**Solutions:**

**Increase timeout:**
```javascript
// In app.js, adjust polling
const maxAttempts = 90; // Increase from 60
```

**Check D-ID status:**
- Log in to D-ID dashboard
- Check service status
- Verify account has credits

**Fallback to audio only:**
```javascript
// Play audio while waiting for video
playAudioFallback(audioBase64);
```

### 9. CORS Errors

**Problem:** `Access-Control-Allow-Origin` error in browser console

**Solutions:**

**Verify CORS is enabled in app.py:**
```python
from flask_cors import CORS
CORS(app)
```

**For specific origins in production:**
```python
CORS(app, origins=["https://yourdomain.com"])
```

**Check browser console:**
- Ensure requests go to correct URL
- Verify no mixed HTTP/HTTPS content

---

## Performance Issues

### 10. Slow Response Time

**Problem:** Long wait times for responses

**Solutions:**

**Optimize audio length:**
- Keep questions concise
- 3-10 seconds is optimal

**Use complete-flow endpoint:**
```javascript
// More efficient than individual API calls
fetch('/api/complete-flow', {...})
```

**Check API quotas:**
- Google Cloud quotas might be limited
- D-ID might have rate limits
- Consider upgrading API tiers

### 11. Session Memory Issues

**Problem:** Application crashes or slows down over time

**Solutions:**

**Clean up old sessions:**
```bash
curl -X POST http://localhost:5000/api/cleanup-sessions
```

**Implement Redis (production):**
```python
# Replace in-memory storage with Redis
import redis
r = redis.Redis(host='localhost', port=6379)
```

---

## Browser Compatibility

### 12. Browser Not Supported

**Problem:** Features not working in certain browsers

**Supported Browsers:**
- ✅ Chrome 60+
- ✅ Edge 79+
- ✅ Firefox 55+
- ✅ Safari 14.1+
- ❌ Internet Explorer (not supported)

**MediaRecorder Support:**
```javascript
// Check if supported
if (!MediaRecorder.isTypeSupported('audio/webm')) {
    console.error('WebM not supported, trying alternatives...');
}
```

---

## Deployment Issues

### 13. Port Already in Use

**Problem:** `Address already in use: Port 5000`

**Solutions:**

**Change port:**
```bash
# In .env
PORT=8000

# Or via command line
python app.py --port 8000
```

**Kill existing process:**
```bash
# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### 14. Docker Container Issues

**Problem:** Container won't start or crashes

**Solutions:**

**Check logs:**
```bash
docker-compose logs -f
```

**Verify credentials mount:**
```bash
docker-compose exec app ls -l /app/credentials/
```

**Rebuild container:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## API-Specific Issues

### 15. Gemini Response Too Long

**Problem:** Responses are too verbose for speech

**Solutions:**

**Adjust generation config in app.py:**
```python
generation_config = {
    "temperature": 0.7,
    "max_output_tokens": 150,  # Reduce from 1024
}
```

**Update system prompt:**
```python
RECEPTIONIST_SYSTEM_PROMPT = """
...
Keep responses very concise (1-2 sentences maximum).
...
"""
```

### 16. D-ID Credits Exhausted

**Problem:** `Payment required` or `Quota exceeded`

**Solutions:**
1. Check D-ID dashboard for credit balance
2. Purchase more credits
3. Implement fallback to audio-only mode
4. Cache generated videos for repeated responses

---

## Testing and Debugging

### 17. Enable Debug Mode

**For detailed error messages:**

```python
# In app.py
app.run(debug=True)
```

```bash
# In .env
FLASK_DEBUG=True
```

### 18. Test Individual Components

**Test Speech-to-Text only:**
```bash
curl -X POST http://localhost:5000/api/speech-to-text \
  -F "audio=@test-recording.webm"
```

**Test Gemini chat only:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

**Test TTS only:**
```bash
curl -X POST http://localhost:5000/api/text-to-speech \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'
```

### 19. Check Backend Logs

**Python logs:**
```bash
# Start with verbose logging
python app.py 2>&1 | tee app.log
```

**Browser console:**
- Open Developer Tools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for failed requests

---

## Getting Help

If you're still experiencing issues:

1. **Check the logs:**
   - Browser console (F12)
   - Backend terminal output
   
2. **Verify setup:**
   ```bash
   python test_setup.py
   ```

3. **Search GitHub Issues:**
   - Look for similar problems
   - Check closed issues for solutions

4. **Create a new issue:**
   - Include error messages
   - Provide steps to reproduce
   - Mention your environment (OS, Python version, etc.)

---

## Quick Diagnostic Checklist

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created and configured
- [ ] Google Cloud credentials file exists
- [ ] All API keys are valid
- [ ] Google Cloud APIs are enabled
- [ ] Microphone permissions granted
- [ ] Using HTTPS or localhost
- [ ] Port 5000 is available
- [ ] D-ID account has credits
- [ ] Browser is supported (Chrome/Edge/Firefox)
