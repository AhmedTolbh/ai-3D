# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                               │
│                      (Browser - HTML/JS)                             │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Record     │  │   Display    │  │ Conversation │              │
│  │   Audio      │  │   Avatar     │  │    Log       │              │
│  │  (Mic Input) │  │   Video      │  │              │              │
│  └──────┬───────┘  └──────▲───────┘  └──────────────┘              │
│         │                 │                                          │
└─────────┼─────────────────┼──────────────────────────────────────────┘
          │                 │
          │  WebM Audio     │  Video URL
          │                 │
┌─────────▼─────────────────┴──────────────────────────────────────────┐
│                      FLASK BACKEND SERVER                             │
│                        (app.py - Python)                              │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              /api/complete-flow Endpoint                       │  │
│  │  (Orchestrates the entire conversation flow)                   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│         │                                                             │
│         ├──────────────────────────────────────────────────┐         │
│         │                  │                  │            │         │
│         ▼                  ▼                  ▼            ▼         │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────┐ │
│  │  Speech-to- │   │   Gemini    │   │  Text-to-   │   │  D-ID   │ │
│  │    Text     │──▶│    Chat     │──▶│   Speech    │──▶│ Avatar  │ │
│  │  Converter  │   │   Handler   │   │  Generator  │   │ Creator │ │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────┘ │
│         │                  │                  │            │         │
└─────────┼──────────────────┼──────────────────┼────────────┼─────────┘
          │                  │                  │            │
          │                  │                  │            │
          ▼                  ▼                  ▼            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL APIs                                    │
│                                                                       │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────┐ │
│  │   Google    │   │   Google    │   │   Google    │   │  D-ID   │ │
│  │   Cloud     │   │   Gemini    │   │   Cloud     │   │   API   │ │
│  │  Speech-to- │   │  1.5 Pro    │   │  Text-to-   │   │ (Avatar │ │
│  │    Text     │   │     API     │   │   Speech    │   │  Video) │ │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Speaks
```
User → Microphone → MediaRecorder API → Audio Blob (WebM)
```

### 2. Speech Recognition
```
Audio Blob → POST /api/complete-flow → Google Cloud Speech-to-Text API
→ Text Transcription (e.g., "What are your office hours?")
```

### 3. AI Processing
```
Text → Gemini 1.5 Pro API → Intelligent Response
→ "We're open Monday through Friday, 9 AM to 6 PM."
```

### 4. Voice Synthesis
```
Response Text → Google Cloud Text-to-Speech API → MP3 Audio (Base64)
```

### 5. Avatar Generation
```
MP3 Audio → D-ID API → Animated Video (URL)
→ Lip-synced talking avatar
```

### 6. Display
```
Video URL → HTML5 Video Element → User sees and hears response
```

## Component Interactions

### Frontend (static/app.js)
- **startRecording()**: Captures microphone input
- **stopRecording()**: Stops recording and triggers processing
- **processRecording()**: Sends audio to backend
- **pollVideoStatus()**: Checks video generation status
- **displayVideo()**: Shows final avatar video

### Backend (app.py)
- **speech_to_text()**: Converts audio to text
- **chat_with_gemini()**: Processes conversation with AI
- **text_to_speech()**: Generates voice response
- **create_avatar_video()**: Creates animated avatar
- **complete_flow()**: Orchestrates all steps

## Session Management

```
┌──────────────────────────────────────┐
│     In-Memory Session Storage         │
│                                        │
│  session_id: "session_123"            │
│  ├─ chat: GeminiChatSession           │
│  ├─ created_at: timestamp             │
│  └─ history: [...]                    │
│                                        │
│  Cleanup: Every 1 hour                │
└──────────────────────────────────────┘
```

## Error Handling Flow

```
User Action
    │
    ├─ Try API Call
    │     │
    │     ├─ Success ──▶ Continue Flow
    │     │
    │     └─ Error
    │         │
    │         ├─ Log Error to Console
    │         ├─ Display User-Friendly Message
    │         ├─ Reset UI State
    │         └─ Allow Retry
    │
    └─ Timeout Protection
        └─ Maximum 60 attempts for video polling
```

## Deployment Architecture

### Local Development
```
Developer Machine
├─ Python Virtual Environment
├─ Flask Dev Server (Port 5000)
└─ Browser (localhost:5000)
```

### Docker Deployment
```
Docker Container
├─ Python 3.11 Base Image
├─ Flask Application
├─ Mounted Credentials
└─ Volume for Generated Files
```

### Production (Recommended)
```
Cloud Platform (Vercel/Railway/AWS)
├─ Application Server
├─ Redis (Session Storage)
├─ Load Balancer
├─ CDN (Static Files)
└─ SSL Certificate
```

## Security Layers

```
┌────────────────────────────────────┐
│    Environment Variables (.env)     │
│  • API Keys (Not in Git)           │
│  • Credentials (Separate Files)    │
└────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│      Backend Validation             │
│  • Input Sanitization              │
│  • Request Validation              │
│  • Error Handling                  │
└────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│       HTTPS/CORS                    │
│  • Secure Communication            │
│  • Origin Validation               │
└────────────────────────────────────┘
```

## API Rate Limits

```
┌─────────────────────────────────────────────┐
│  Google Gemini API                           │
│  • Varies by API key tier                   │
│  • Recommended: Implement client-side cache │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Google Cloud Speech-to-Text                 │
│  • Default: 60 requests/minute              │
│  • Max audio length: 1 minute (sync)        │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Google Cloud Text-to-Speech                 │
│  • Default: 300 requests/minute             │
│  • Max text: 5000 characters                │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  D-ID API                                    │
│  • Varies by plan                           │
│  • Credit-based system                      │
│  • Video generation: ~30-60 seconds         │
└─────────────────────────────────────────────┘
```

## Performance Optimization

### Caching Strategy
```
Repeated Questions ──▶ Cache Response ──▶ Skip AI Processing
                              │
                              └──▶ Direct TTS + Avatar
```

### Async Processing
```
Record Audio ──▶ Send to Backend ──▶ Return Talk ID
                                            │
User sees "Processing" ◀────────────────────┘
                                            │
Poll Every 2s ──▶ Check Status ─────────────┤
                      │                     │
                      ├─ Processing ────────┘
                      │
                      └─ Complete ──▶ Display Video
```

## Scalability Considerations

### Current (Demo)
- In-memory session storage
- Single server instance
- Synchronous processing

### Production Recommended
- Redis for session storage
- Multiple server instances
- Async task queue (Celery)
- CDN for static files
- Database for conversation logs
- Monitoring and alerting

## File Structure

```
ai-3D/
├── app.py                      # Main backend server
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
│
├── static/                    # Frontend files
│   ├── index.html            # Main UI
│   ├── app.js                # Frontend logic
│   ├── audio/                # Generated audio files
│   └── video/                # Generated video files
│
├── start.sh                   # Quick start (Linux/Mac)
├── start.bat                  # Quick start (Windows)
├── test_setup.py              # Setup validation
│
├── Dockerfile                 # Docker container
├── docker-compose.yml         # Docker orchestration
│
└── Documentation/
    ├── README.md              # Main documentation
    ├── API_DOCUMENTATION.md   # API reference
    ├── TROUBLESHOOTING.md     # Problem solving
    ├── CONTRIBUTING.md        # Contributor guide
    └── LICENSE                # MIT License
```
