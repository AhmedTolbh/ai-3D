# Virtual Receptionist Avatar 🤖

An AI-powered virtual receptionist with realistic avatar animation, powered by Google Gemini, Google Cloud APIs, and D-ID.

## 🌟 Features

- **Voice Interaction**: Record your questions using your microphone
- **Speech Recognition**: Powered by Google Cloud Speech-to-Text API
- **Intelligent Conversations**: Google Gemini 2.5 Pro handles conversation logic and context
- **Natural Voice**: Google Cloud Text-to-Speech generates realistic responses
- **Animated Avatar**: D-ID API creates lip-synced video of a talking receptionist
- **Multilingual Support**: English, Finnish, and Arabic
- **Session Memory**: Maintains conversation context across multiple interactions
- **Modern UI**: Clean, responsive web interface

## 🎯 Use Cases

The virtual receptionist can:
- Greet visitors warmly and professionally
- Answer questions about company information, office directions, and event schedules
- Handle simple inquiries and redirect to support when needed
- Support multilingual interactions
- Maintain conversation context for natural dialogues

## 🏗️ Architecture

```
User speaks → Speech-to-Text → Gemini AI → Text-to-Speech → D-ID Avatar → Video Display
                  ↓                ↓              ↓              ↓
              Google Cloud    Conversation    Google Cloud    Video
                 API            Logic            API         Generation
```

## 📋 Prerequisites

Before you begin, ensure you have the following:

1. **Python 3.8+** installed
2. **Google Cloud Platform account** with:
   - Speech-to-Text API enabled
   - Text-to-Speech API enabled
   - Service account JSON credentials file
3. **Google Gemini API key** (from Google AI Studio)
4. **D-ID API key** (from D-ID platform)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/AhmedTolbh/ai-3D.git
cd ai-3D
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud credentials (path to JSON file)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/google-cloud-credentials.json

# D-ID API Key
DID_API_KEY=your_did_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### 4. Obtain API Keys

#### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

#### Google Cloud Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Cloud Speech-to-Text API
   - Cloud Text-to-Speech API
4. Create a service account:
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Grant roles: "Speech-to-Text Admin" and "Text-to-Speech Admin"
   - Create and download JSON key file
5. Save the JSON file and update the path in `.env`

#### D-ID API Key
1. Visit [D-ID Platform](https://www.d-id.com/)
2. Sign up or log in to your account
3. Navigate to your account settings or [API page](https://studio.d-id.com/account-settings)
4. Generate an API key (you may need to add credits to your account)
5. Copy the API key to your `.env` file

**Important Notes:**
- D-ID API is a paid service with free trial credits
- Each video generation consumes credits based on video duration
- Check [D-ID documentation](https://docs.d-id.com/) for latest API details
- API key should be kept secure and not committed to version control

### 5. Run the Application

```bash
python app.py
```

The server will start at `http://localhost:5000`

### 6. Open in Browser

Navigate to `http://localhost:5000` in your web browser.

## 🎮 How to Use

1. **Start**: Click the "🎤 Talk to Receptionist" button
2. **Allow Access**: Grant microphone permissions when prompted
3. **Speak**: Ask your question clearly (e.g., "What are your office hours?")
4. **Stop**: Click "⏹ Stop Recording" when finished speaking
5. **Wait**: The system will:
   - Transcribe your speech
   - Generate a response using Gemini AI
   - Convert response to speech
   - Create an animated avatar video
   - Display the video response
6. **Continue**: Ask follow-up questions or click "🔄 New Conversation" to start fresh

## 💬 Example Conversations

### Example 1: Office Information
```
User: "What are your office hours?"
Receptionist: "We're open Monday through Friday, 9 AM to 6 PM. How else can I help you today?"
```

### Example 2: Directions
```
User: "Where is the reception desk?"
Receptionist: "Our reception desk is located on the ground floor of the main building. You'll see it right as you enter. Is there anything else you'd like to know?"
```

### Example 3: Events
```
User: "Are there any upcoming events?"
Receptionist: "Yes! We have a Tech Conference scheduled for November 15th and a Product Launch on December 1st. Would you like more details about either event?"
```

### Example 4: Multilingual
```
User: "Miten voin auttaa?" (Finnish: How can I help?)
Receptionist: [Responds in Finnish]
```

## 🛠️ Technical Details

### Backend (Python Flask)

- **Framework**: Flask 3.0
- **APIs Used**:
  - Google Cloud Speech-to-Text v2
  - Google Generative AI (Gemini 1.5 Pro)
  - Google Cloud Text-to-Speech v2
  - D-ID Talks API
- **CORS**: Enabled for browser testing
- **Session Management**: In-memory (use Redis for production)

### Frontend (HTML/JavaScript)

- **Audio Recording**: MediaRecorder API
- **UI Framework**: Vanilla JavaScript + CSS
- **Async Communication**: Fetch API
- **Video Playback**: HTML5 Video Element

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve main HTML page |
| `/health` | GET | Health check |
| `/api/speech-to-text` | POST | Convert audio to text |
| `/api/chat` | POST | Chat with Gemini AI |
| `/api/text-to-speech` | POST | Convert text to audio |
| `/api/create-avatar-video` | POST | Generate avatar video |
| `/api/check-video-status/<id>` | GET | Check video generation status |
| `/api/complete-flow` | POST | End-to-end processing |

## 📁 Project Structure

```
ai-3D/
├── app.py                 # Flask backend server
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── static/               # Frontend files
    ├── index.html        # Main HTML page
    ├── app.js            # Frontend JavaScript
    ├── audio/            # Audio files (generated)
    └── video/            # Video files (generated)
```

## 🚢 Deployment

### Local Deployment
Already covered in Quick Start section above.

### Replit Deployment

1. Import the repository to Replit
2. Add secrets (environment variables) in Replit's Secrets tab:
   - `GEMINI_API_KEY`
   - `DID_API_KEY`
3. For Google Cloud credentials:
   - Upload the JSON file as a secret or use Replit's file upload
   - Set `GOOGLE_APPLICATION_CREDENTIALS` to the file path
4. Run the application

### Vercel/Railway Deployment

1. Connect your GitHub repository
2. Configure environment variables in the platform settings
3. For Google Cloud credentials, encode JSON as base64 or use platform secrets
4. Deploy

**Note**: For production, replace in-memory session storage with Redis or a database.

## 🔧 Configuration

### Customize the Receptionist Persona

Edit the `RECEPTIONIST_SYSTEM_PROMPT` in `app.py`:

```python
RECEPTIONIST_SYSTEM_PROMPT = """
Your custom prompt here...
"""
```

### Change Avatar Image

In `app.py`, modify the `source_url` in the D-ID API call:

```python
"source_url": "https://your-custom-avatar-image-url.png"
```

### Adjust Voice Settings

Modify voice parameters in the `text-to-speech` function:

```python
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Neural2-F",  # Change voice type
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
)
```

## 🐛 Troubleshooting

### Microphone Not Working
- Check browser permissions
- Ensure you're using HTTPS (required for microphone access)
- Try a different browser (Chrome/Edge recommended)

### API Errors
- Verify all API keys are correct in `.env`
- Check that Google Cloud APIs are enabled
- Ensure service account has proper permissions
- Check API quotas and billing

### Video Not Generating
- Verify D-ID API key is valid
- Check D-ID account credits
- Look at browser console for errors
- Check backend logs for API responses

### Speech Recognition Issues
- Speak clearly and at moderate pace
- Ensure quiet environment
- Check microphone quality
- Verify correct language settings

## 📊 API Rate Limits

Be aware of the following rate limits:

- **Google Gemini**: Check your API quota
- **Google Cloud Speech-to-Text**: 60 requests/minute (default)
- **Google Cloud Text-to-Speech**: 300 requests/minute (default)
- **D-ID**: Varies by plan (check your account)

## 🔐 Security Notes

- Never commit `.env` file or API keys to version control
- Use environment variables for all sensitive data
- Enable HTTPS in production
- Implement rate limiting for production deployment
- Validate and sanitize all user inputs
- Use proper authentication for production APIs

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Google Gemini for conversation AI
- Google Cloud for speech services
- D-ID for avatar animation technology
- Flask for the web framework

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review API documentation
3. Open an issue on GitHub

## 🎓 Demo & Hackathon Presentation

### Key Talking Points:

1. **Problem**: Traditional receptionists are limited to office hours and single conversations
2. **Solution**: AI-powered avatar that works 24/7 with natural conversation
3. **Technology Stack**: 
   - Gemini AI for intelligent responses
   - Google Cloud for speech processing
   - D-ID for realistic avatar animation
4. **Benefits**:
   - Reduced workload for human staff
   - Consistent, professional interactions
   - Multilingual support
   - Scalable to multiple locations

### Live Demo Flow:

1. Show the clean UI
2. Ask a simple question: "What are your office hours?"
3. Show the avatar response
4. Ask a follow-up to demonstrate context: "And where is the reception desk?"
5. Demonstrate multilingual: Switch to Finnish or Arabic
6. Show the conversation log

---

**Built with ❤️ for the hackathon**