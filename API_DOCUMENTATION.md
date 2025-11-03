# API Documentation

## Virtual Receptionist Avatar API

Base URL: `http://localhost:5000`

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the server is running

**Response:**
```json
{
  "status": "healthy",
  "service": "Virtual Receptionist Avatar API"
}
```

---

### 2. Speech-to-Text

**Endpoint:** `POST /api/speech-to-text`

**Description:** Convert audio to text using Google Cloud Speech-to-Text

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `audio`: Audio file (WebM format)

**Response:**
```json
{
  "transcription": "What are your office hours?",
  "confidence": 0.95
}
```

**Error Response:**
```json
{
  "error": "No speech detected"
}
```

---

### 3. Chat with Gemini

**Endpoint:** `POST /api/chat`

**Description:** Send a message to Gemini AI and get a response

**Request:**
```json
{
  "message": "What are your office hours?",
  "session_id": "session_12345" // optional
}
```

**Response:**
```json
{
  "response": "We're open Monday through Friday, 9 AM to 6 PM.",
  "session_id": "session_12345"
}
```

---

### 4. Text-to-Speech

**Endpoint:** `POST /api/text-to-speech`

**Description:** Convert text to speech using Google Cloud TTS

**Request:**
```json
{
  "text": "We're open Monday through Friday, 9 AM to 6 PM.",
  "language_code": "en-US" // optional, default: en-US
}
```

**Response:**
```json
{
  "audio": "base64_encoded_audio_data",
  "format": "mp3"
}
```

---

### 5. Create Avatar Video

**Endpoint:** `POST /api/create-avatar-video`

**Description:** Generate a talking avatar video using D-ID API

**Request:**
```json
{
  "audio_base64": "base64_encoded_audio_data"
}
```

**Response (Immediate):**
```json
{
  "status": "processing",
  "talk_id": "tlk_abc123",
  "message": "Video is still being generated"
}
```

**Response (When complete):**
```json
{
  "status": "completed",
  "video_url": "https://d-id.com/talks/video.mp4",
  "talk_id": "tlk_abc123"
}
```

---

### 6. Check Video Status

**Endpoint:** `GET /api/check-video-status/<talk_id>`

**Description:** Check the status of a video generation job

**Response (Processing):**
```json
{
  "status": "processing"
}
```

**Response (Completed):**
```json
{
  "status": "completed",
  "video_url": "https://d-id.com/talks/video.mp4"
}
```

**Response (Error):**
```json
{
  "status": "error",
  "error": "Video generation failed"
}
```

---

### 7. Complete Flow (Recommended)

**Endpoint:** `POST /api/complete-flow`

**Description:** Process the entire flow in one request (speech-to-text → chat → TTS → avatar)

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `audio`: Audio file (WebM format)
  - `session_id`: Session ID (optional)

**Response:**
```json
{
  "session_id": "session_12345",
  "user_text": "What are your office hours?",
  "assistant_text": "We're open Monday through Friday, 9 AM to 6 PM.",
  "audio_base64": "base64_encoded_audio_data",
  "talk_id": "tlk_abc123",
  "status": "processing"
}
```

**Note:** After receiving this response, poll `/api/check-video-status/<talk_id>` to get the final video URL.

---

### 8. Cleanup Sessions

**Endpoint:** `POST /api/cleanup-sessions`

**Description:** Remove conversation sessions older than 1 hour

**Response:**
```json
{
  "message": "Cleaned up 3 old sessions"
}
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (missing parameters, invalid input)
- `500` - Internal Server Error (API failures, processing errors)

Error responses have the format:
```json
{
  "error": "Description of what went wrong"
}
```

---

## Rate Limits

Be aware of the following API rate limits:

- **Google Gemini**: Varies by API key tier
- **Google Cloud Speech-to-Text**: 60 requests/minute (default)
- **Google Cloud Text-to-Speech**: 300 requests/minute (default)
- **D-ID**: Varies by plan

---

## Usage Example

### Using the Complete Flow

```javascript
// Record audio
const audioBlob = /* recorded audio blob */;

// Create form data
const formData = new FormData();
formData.append('audio', audioBlob, 'recording.webm');
formData.append('session_id', 'my-session-id');

// Send request
const response = await fetch('/api/complete-flow', {
  method: 'POST',
  body: formData
});

const data = await response.json();

// Poll for video
const pollInterval = setInterval(async () => {
  const statusResponse = await fetch(`/api/check-video-status/${data.talk_id}`);
  const statusData = await statusResponse.json();
  
  if (statusData.status === 'completed') {
    clearInterval(pollInterval);
    // Display video
    videoElement.src = statusData.video_url;
  }
}, 2000);
```

---

## Session Management

Sessions are stored in memory and persist for 1 hour. Each session maintains:
- Conversation history with Gemini
- Context for follow-up questions
- Timestamp for cleanup

To start a new conversation, either:
1. Generate a new session ID
2. Let the client generate one automatically
3. Call `/api/cleanup-sessions` to clear old sessions

---

## Supported Languages

The system supports:
- **English** (en-US) - Primary
- **Finnish** (fi-FI)
- **Arabic** (ar-SA)

Speech recognition automatically detects the language from the configured alternatives.

---

## Audio Format Requirements

### Input (Speech-to-Text)
- Format: WebM with Opus codec
- Sample Rate: 48000 Hz
- Channels: Mono or Stereo

### Output (Text-to-Speech)
- Format: MP3
- Sample Rate: 24000 Hz (default)
- Encoding: Base64 string

---

## Video Generation

### Avatar Configuration

Default avatar image URL:
```
https://create-images-results.d-id.com/default-presenter-image.png
```

To use a custom avatar, modify the `source_url` in the backend.

### Video Specifications
- Format: MP4
- Resolution: 512x512 (D-ID default)
- Duration: Matches audio length
- Features: Lip-sync, head movements, natural expressions

---

## Best Practices

1. **Use Complete Flow Endpoint**: More efficient than calling individual endpoints
2. **Poll Responsibly**: Wait 2-3 seconds between video status checks
3. **Handle Timeouts**: Video generation can take 30-60 seconds
4. **Session Management**: Clean up old sessions periodically
5. **Error Handling**: Always check response status and handle errors
6. **Audio Quality**: Use clear audio recordings for best transcription
7. **Rate Limiting**: Implement client-side rate limiting to avoid API quota exhaustion

---

## Security Considerations

1. **API Keys**: Never expose API keys in client-side code
2. **HTTPS**: Use HTTPS in production
3. **Input Validation**: Server validates all inputs
4. **CORS**: Configured for browser access (restrict in production)
5. **Rate Limiting**: Implement in production to prevent abuse
