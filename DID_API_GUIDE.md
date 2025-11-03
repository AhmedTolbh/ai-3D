# D-ID API Integration Guide

## Overview

This guide explains how the Virtual Receptionist Avatar application integrates with D-ID's API to create realistic talking avatar videos.

## What is D-ID?

[D-ID](https://www.d-id.com/) is a AI-powered video generation platform that creates realistic talking avatars from still images and audio. It uses advanced deep learning to generate lip-synced videos with natural head movements and expressions.

## Official Resources

- **Website:** https://www.d-id.com/
- **API Documentation:** https://docs.d-id.com/
- **Studio Dashboard:** https://studio.d-id.com/
- **API Status:** https://status.d-id.com/
- **Pricing:** https://www.d-id.com/pricing/

---

## Getting Started with D-ID

### 1. Create an Account

1. Visit [D-ID](https://www.d-id.com/)
2. Click "Sign Up" or "Get Started"
3. Complete the registration process
4. Verify your email address

### 2. Get API Key

1. Log in to [D-ID Studio](https://studio.d-id.com/)
2. Navigate to **Settings** → **API Key** or visit [Account Settings](https://studio.d-id.com/account-settings)
3. Click "Create API Key"
4. Copy the API key (save it securely - you won't see it again!)
5. Add the key to your `.env` file:
   ```
   DID_API_KEY=your_api_key_here
   ```

### 3. Add Credits

D-ID uses a credit-based pricing model:

1. New accounts typically receive free trial credits
2. Each video generation consumes credits based on:
   - Video duration (typically matches audio length)
   - Resolution (default: 512x512)
3. Purchase additional credits from the [D-ID dashboard](https://studio.d-id.com/)
4. Check your credit balance before generating videos

---

## API Authentication

### Current Implementation

The application uses the **API Key authentication** method with the `x-api-key` header:

```python
def get_did_headers():
    """Get properly formatted headers for D-ID API"""
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": DID_API_KEY
    }
```

### Alternative Methods

D-ID API also supports Basic authentication, but we use the simpler API key method as it's recommended by D-ID for most use cases.

---

## API Endpoints Used

### 1. Create Talk (POST)

**Endpoint:** `https://api.d-id.com/talks`

**Purpose:** Create a new talking avatar video from audio

**Request:**
```json
{
  "script": {
    "type": "audio",
    "audio_url": "data:audio/mp3;base64,{base64_encoded_audio}"
  },
  "config": {
    "fluent": true,
    "pad_audio": 0.0
  },
  "source_url": "https://create-images-results.d-id.com/default-presenter-image.png"
}
```

**Response:**
```json
{
  "id": "tlk_xxxxxxxxxxxxx",
  "status": "created",
  "created_at": "2025-11-03T12:00:00.000Z"
}
```

### 2. Get Talk Status (GET)

**Endpoint:** `https://api.d-id.com/talks/{talk_id}`

**Purpose:** Check the status and retrieve the generated video

**Response (Processing):**
```json
{
  "id": "tlk_xxxxxxxxxxxxx",
  "status": "started",
  "created_at": "2025-11-03T12:00:00.000Z"
}
```

**Response (Complete):**
```json
{
  "id": "tlk_xxxxxxxxxxxxx",
  "status": "done",
  "result_url": "https://d-id-talks-prod.s3.amazonaws.com/...",
  "created_at": "2025-11-03T12:00:00.000Z",
  "duration": 5.5
}
```

---

## Video Generation Flow

### Application Flow

```
1. User speaks → Audio recorded
   ↓
2. Speech-to-Text → Text transcription
   ↓
3. Gemini AI → Response text
   ↓
4. Text-to-Speech → MP3 audio (base64)
   ↓
5. POST to D-ID /talks → Talk ID
   ↓
6. Poll /talks/{id} every 2 seconds
   ↓
7. Status = "done" → Video URL
   ↓
8. Display video to user
```

### Status Progression

| Status | Description | Next Action |
|--------|-------------|-------------|
| `created` | Talk queued | Continue polling |
| `started` | Processing video | Continue polling |
| `done` | Video ready | Display video |
| `error` | Generation failed | Show error |

### Typical Generation Times

- **Short responses (< 5 seconds):** 10-20 seconds
- **Medium responses (5-15 seconds):** 20-40 seconds
- **Long responses (> 15 seconds):** 40-60 seconds

---

## Configuration Options

### Avatar Source Image

**Default:**
```python
"source_url": "https://create-images-results.d-id.com/default-presenter-image.png"
```

**Custom Avatar:**
To use your own avatar:

1. Upload a portrait image to a public URL (or use a service like Imgur)
2. Image requirements:
   - Format: PNG or JPG
   - Recommended size: 512x512 or larger
   - Clear frontal face photo
   - Good lighting
   - Neutral expression
3. Update the `source_url` in `app.py`:
   ```python
   "source_url": "https://your-domain.com/your-avatar.png"
   ```

### Audio Configuration

**Fluent Mode:**
```python
"config": {
    "fluent": true,      # Enables natural head movements
    "pad_audio": 0.0     # No padding (immediate start)
}
```

Options:
- `fluent: true` - Natural movements (recommended)
- `fluent: false` - Minimal movements
- `pad_audio: 0.0-3.0` - Silence before/after (seconds)

---

## Best Practices

### 1. Credit Management

- **Monitor usage:** Check credit balance regularly
- **Optimize responses:** Keep responses concise to reduce video length
- **Cache videos:** Store frequently used responses to save credits
- **Implement fallback:** Have audio-only mode when credits are low

### 2. Error Handling

```python
try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if response.status_code == 401:
        # Invalid API key
        print("Check your D-ID API key")
    elif response.status_code == 402:
        # Insufficient credits
        print("Please add credits to your D-ID account")
    elif response.status_code == 429:
        # Rate limit exceeded
        print("Too many requests, please slow down")
    else:
        print(f"D-ID API error: {e}")
```

### 3. Performance Optimization

- **Async processing:** Don't block the UI while waiting for video
- **Progress indicators:** Show status to users during generation
- **Timeouts:** Implement reasonable timeouts (60-120 seconds)
- **Retry logic:** Retry failed requests with exponential backoff

### 4. Security

- **Keep API key secret:** Never commit to version control
- **Use environment variables:** Store in `.env` file
- **Validate inputs:** Check audio data before sending to D-ID
- **HTTPS only:** Ensure all requests use HTTPS

---

## Rate Limits

D-ID implements rate limits to ensure fair usage:

- **Free tier:** Limited requests per minute
- **Paid tiers:** Higher limits based on plan
- **Burst handling:** Implement queuing for multiple requests
- **Status code 429:** "Too Many Requests" - back off and retry

Check your specific limits in the [D-ID dashboard](https://studio.d-id.com/).

---

## Troubleshooting

### Common Issues

#### 1. "401 Unauthorized"
- **Cause:** Invalid or missing API key
- **Solution:** Verify API key in `.env` file

#### 2. "402 Payment Required"
- **Cause:** Insufficient credits
- **Solution:** Add credits in D-ID dashboard

#### 3. "Video generation timeout"
- **Cause:** Video taking longer than expected
- **Solutions:**
  - Increase polling timeout
  - Check D-ID service status
  - Reduce audio length

#### 4. "Invalid audio format"
- **Cause:** Audio not properly base64 encoded
- **Solution:** Verify audio encoding:
  ```python
  import base64
  audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
  ```

#### 5. "Source image not found"
- **Cause:** Avatar image URL not accessible
- **Solution:** Ensure image is publicly accessible via HTTPS

### Getting Help

1. Check [D-ID Documentation](https://docs.d-id.com/)
2. Review [API Status](https://status.d-id.com/) for outages
3. Contact D-ID support through their dashboard
4. Check this repository's [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Code Examples

### Create a Video

```python
import requests
import base64

# Prepare audio
with open('audio.mp3', 'rb') as f:
    audio_bytes = f.read()
audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

# Make request
url = "https://api.d-id.com/talks"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "x-api-key": "YOUR_API_KEY"
}
payload = {
    "script": {
        "type": "audio",
        "audio_url": f"data:audio/mp3;base64,{audio_base64}"
    },
    "config": {
        "fluent": True,
        "pad_audio": 0.0
    },
    "source_url": "https://your-avatar-url.png"
}

response = requests.post(url, json=payload, headers=headers)
talk_id = response.json()['id']
print(f"Talk created: {talk_id}")
```

### Poll for Completion

```python
import time

def wait_for_video(talk_id, api_key, timeout=60):
    """Wait for D-ID video to complete"""
    url = f"https://api.d-id.com/talks/{talk_id}"
    headers = {"x-api-key": api_key}
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data['status'] == 'done':
            return data['result_url']
        elif data['status'] == 'error':
            raise Exception("Video generation failed")
        
        time.sleep(2)  # Poll every 2 seconds
    
    raise TimeoutError("Video generation timeout")

# Use it
video_url = wait_for_video(talk_id, "YOUR_API_KEY")
print(f"Video ready: {video_url}")
```

---

## Pricing Information

D-ID uses a credit-based pricing model:

- **Free Trial:** New accounts receive limited free credits
- **Credit Packages:** Purchase credit packs as needed
- **Subscription Plans:** Monthly plans with included credits
- **Enterprise:** Custom pricing for high-volume usage

**Cost Factors:**
- Video duration (longer = more credits)
- Resolution (higher = more credits)
- Number of requests

Check current pricing at: https://www.d-id.com/pricing/

---

## Advanced Features

### Custom Voice (Not Currently Implemented)

D-ID supports custom voice providers. You can integrate:
- Amazon Polly
- Microsoft Azure TTS
- IBM Watson TTS

See [D-ID Voice Providers](https://docs.d-id.com/) for details.

### Webhooks (Not Currently Implemented)

Instead of polling, you can use webhooks for completion notifications:

```python
payload = {
    "webhook": "https://your-domain.com/webhook",
    # ... rest of payload
}
```

### Batch Processing

For multiple videos, consider implementing a queue system to avoid rate limits.

---

## Migration Notes

### From Basic Auth to API Key

If you were using the old Basic auth method:

**Old:**
```python
headers = {
    "authorization": f"Basic {base64_encoded_key}"
}
```

**New (Current):**
```python
headers = {
    "x-api-key": DID_API_KEY
}
```

The new method is simpler and recommended by D-ID.

---

## References

- **D-ID Website:** https://www.d-id.com/
- **API Documentation:** https://docs.d-id.com/
- **Studio Dashboard:** https://studio.d-id.com/
- **Support:** Available through D-ID dashboard
- **Status Page:** https://status.d-id.com/

---

## Contributing

Found an issue with the D-ID integration? Please:

1. Check existing issues
2. Open a new issue with details
3. Submit a pull request with fixes

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Last Updated:** November 3, 2025

**API Version:** D-ID Talks API v1

**Application Version:** 1.0.0
