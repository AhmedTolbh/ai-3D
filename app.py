"""
Virtual Receptionist Avatar Backend Server
===========================================
This Flask server handles the complete flow:
1. Speech-to-Text (Google Cloud)
2. Conversation Logic (Google Gemini 2.5 Pro)
3. Text-to-Speech (Google Cloud)
4. Avatar Animation (D-ID API)
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import base64
import requests
import io
import time
import uuid

# Google Cloud imports
from google.cloud import speech
from google.cloud import texttospeech
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # Enable CORS for browser testing

# Configure API keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DID_API_KEY = os.getenv('DID_API_KEY')
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Initialize Google Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Google Cloud clients
speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()

# Session storage for conversation context (in-memory for demo)
# In production, use Redis or a database
conversation_sessions = {}


def get_did_headers():
    """
    Get properly formatted headers for D-ID API
    D-ID API uses either:
    1. Simple API key header: x-api-key
    2. Basic auth: Authorization: Basic base64(api_key:)
    
    Using x-api-key method as it's simpler and recommended
    """
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": DID_API_KEY
    }

# Configure Gemini model
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# System prompt for the receptionist persona
RECEPTIONIST_SYSTEM_PROMPT = """You are a friendly and professional virtual receptionist. 
Your role is to:
- Greet visitors warmly and professionally
- Answer questions about the company, office directions, and event schedules
- Be helpful and courteous at all times
- If you don't know something, politely acknowledge it and offer to connect them with support
- Keep responses concise and natural (2-3 sentences maximum for spoken responses)
- Support multilingual interactions (English, Finnish, Arabic)
- Remember context from the conversation

Company Information:
- Company Name: TechInnovate Solutions
- Address: 123 Innovation Drive, Tech City, TC 12345
- Office Hours: Monday-Friday, 9 AM - 6 PM
- Reception Desk: Ground Floor, Main Building
- Upcoming Events: Tech Conference on November 15th, Product Launch on December 1st

Always be polite, professional, and helpful. If the question is beyond your scope, say: 
"I'd be happy to connect you with our support team for more detailed assistance."
"""


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('static', 'index.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Virtual Receptionist Avatar API"})


@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    """
    Convert speech audio to text using Google Cloud Speech-to-Text
    Expects: audio file in the request
    Returns: transcribed text
    """
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        audio_content = audio_file.read()
        
        # Configure speech recognition
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="en-US",
            alternative_language_codes=["fi-FI", "ar-SA"],  # Support Finnish and Arabic
            enable_automatic_punctuation=True,
        )
        
        # Perform speech recognition
        response = speech_client.recognize(config=config, audio=audio)
        
        if not response.results:
            return jsonify({"error": "No speech detected"}), 400
        
        # Get the first result (highest confidence)
        transcription = response.results[0].alternatives[0].transcript
        confidence = response.results[0].alternatives[0].confidence
        
        return jsonify({
            "transcription": transcription,
            "confidence": confidence
        })
    
    except Exception as e:
        print(f"Error in speech-to-text: {str(e)}")
        return jsonify({"error": f"Speech-to-text error: {str(e)}"}), 500


@app.route('/api/chat', methods=['POST'])
def chat_with_gemini():
    """
    Process user message through Gemini and get response
    Expects: JSON with 'message' and optional 'session_id'
    Returns: Gemini's response text
    """
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Get or create conversation session
        if session_id not in conversation_sessions:
            # Initialize new conversation with system prompt
            model = genai.GenerativeModel(
                model_name='gemini-1.5-pro',  # Using Gemini 1.5 Pro (closest to 2.5 Pro)
                generation_config=generation_config,
                safety_settings=safety_settings,
            )
            chat = model.start_chat(history=[])
            conversation_sessions[session_id] = {
                'chat': chat,
                'created_at': time.time()
            }
            
            # Send system prompt as first message
            chat.send_message(RECEPTIONIST_SYSTEM_PROMPT)
        
        # Get existing chat session
        chat = conversation_sessions[session_id]['chat']
        
        # Send user message and get response
        response = chat.send_message(user_message)
        assistant_message = response.text
        
        return jsonify({
            "response": assistant_message,
            "session_id": session_id
        })
    
    except Exception as e:
        print(f"Error in Gemini chat: {str(e)}")
        return jsonify({"error": f"Chat error: {str(e)}"}), 500


@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech using Google Cloud Text-to-Speech
    Expects: JSON with 'text' and optional 'language_code'
    Returns: audio file (base64 encoded)
    """
    try:
        data = request.json
        text = data.get('text', '')
        language_code = data.get('language_code', 'en-US')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Set up the text input
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Select voice based on language
        voice_params = {
            'en-US': ('en-US', texttospeech.SsmlVoiceGender.FEMALE, 'en-US-Neural2-F'),
            'fi-FI': ('fi-FI', texttospeech.SsmlVoiceGender.FEMALE, 'fi-FI-Standard-A'),
            'ar-SA': ('ar-XA', texttospeech.SsmlVoiceGender.FEMALE, 'ar-XA-Standard-A'),
        }
        
        lang_code, gender, name = voice_params.get(language_code, voice_params['en-US'])
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code,
            name=name,
            ssml_gender=gender
        )
        
        # Configure audio output
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )
        
        # Perform text-to-speech
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Encode audio to base64
        audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
        
        return jsonify({
            "audio": audio_base64,
            "format": "mp3"
        })
    
    except Exception as e:
        print(f"Error in text-to-speech: {str(e)}")
        return jsonify({"error": f"Text-to-speech error: {str(e)}"}), 500


@app.route('/api/create-avatar-video', methods=['POST'])
def create_avatar_video():
    """
    Create talking avatar video using D-ID API
    Expects: JSON with 'audio_base64' (base64 encoded audio)
    Returns: video URL or video data
    """
    try:
        data = request.json
        audio_base64 = data.get('audio_base64', '')
        
        if not audio_base64:
            return jsonify({"error": "No audio provided"}), 400
        
        # D-ID API endpoint
        url = "https://api.d-id.com/talks"
        
        # Prepare the request payload
        payload = {
            "script": {
                "type": "audio",
                "audio_url": f"data:audio/mp3;base64,{audio_base64}"
            },
            "config": {
                "fluent": True,
                "pad_audio": 0.0
            },
            "source_url": "https://create-images-results.d-id.com/default-presenter-image.png"
        }
        
        headers = get_did_headers()
        
        # Create the talk
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        talk_data = response.json()
        talk_id = talk_data.get('id')
        
        if not talk_id:
            return jsonify({"error": "Failed to create talk"}), 500
        
        # Poll for video completion (with timeout)
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            # Check talk status
            status_url = f"https://api.d-id.com/talks/{talk_id}"
            status_response = requests.get(status_url, headers=headers)
            status_data = status_response.json()
            
            status = status_data.get('status')
            
            if status == 'done':
                # Video is ready
                video_url = status_data.get('result_url')
                return jsonify({
                    "status": "completed",
                    "video_url": video_url,
                    "talk_id": talk_id
                })
            elif status == 'error':
                return jsonify({"error": "Video generation failed"}), 500
            
            # Wait before polling again
            time.sleep(2)
            attempt += 1
        
        # Timeout - return status for frontend to poll
        return jsonify({
            "status": "processing",
            "talk_id": talk_id,
            "message": "Video is still being generated"
        })
    
    except requests.exceptions.RequestException as e:
        print(f"Error in D-ID API: {str(e)}")
        return jsonify({"error": f"Avatar video creation error: {str(e)}"}), 500
    except Exception as e:
        print(f"Error in avatar video creation: {str(e)}")
        return jsonify({"error": f"Avatar video error: {str(e)}"}), 500


@app.route('/api/check-video-status/<talk_id>', methods=['GET'])
def check_video_status(talk_id):
    """
    Check the status of a D-ID video generation
    Used for polling when video takes longer to generate
    """
    try:
        url = f"https://api.d-id.com/talks/{talk_id}"
        headers = get_did_headers()
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        status_data = response.json()
        status = status_data.get('status')
        
        if status == 'done':
            return jsonify({
                "status": "completed",
                "video_url": status_data.get('result_url')
            })
        elif status == 'error':
            return jsonify({
                "status": "error",
                "error": "Video generation failed"
            }), 500
        else:
            return jsonify({
                "status": "processing"
            })
    
    except Exception as e:
        print(f"Error checking video status: {str(e)}")
        return jsonify({"error": f"Status check error: {str(e)}"}), 500


@app.route('/api/complete-flow', methods=['POST'])
def complete_flow():
    """
    Complete end-to-end flow:
    1. Speech-to-Text
    2. Gemini Chat
    3. Text-to-Speech
    4. Avatar Video
    
    Expects: audio file
    Returns: video URL and conversation data
    """
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        session_id = request.form.get('session_id', str(uuid.uuid4()))
        
        # Step 1: Speech-to-Text
        audio_file = request.files['audio']
        audio_content = audio_file.read()
        
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="en-US",
            alternative_language_codes=["fi-FI", "ar-SA"],
            enable_automatic_punctuation=True,
        )
        
        stt_response = speech_client.recognize(config=config, audio=audio)
        
        if not stt_response.results:
            return jsonify({"error": "No speech detected"}), 400
        
        user_text = stt_response.results[0].alternatives[0].transcript
        
        # Step 2: Gemini Chat
        if session_id not in conversation_sessions:
            model = genai.GenerativeModel(
                model_name='gemini-1.5-pro',
                generation_config=generation_config,
                safety_settings=safety_settings,
            )
            chat = model.start_chat(history=[])
            conversation_sessions[session_id] = {
                'chat': chat,
                'created_at': time.time()
            }
            chat.send_message(RECEPTIONIST_SYSTEM_PROMPT)
        
        chat = conversation_sessions[session_id]['chat']
        gemini_response = chat.send_message(user_text)
        assistant_text = gemini_response.text
        
        # Step 3: Text-to-Speech
        synthesis_input = texttospeech.SynthesisInput(text=assistant_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-F",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )
        
        tts_response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        audio_base64 = base64.b64encode(tts_response.audio_content).decode('utf-8')
        
        # Step 4: Create Avatar Video
        url = "https://api.d-id.com/talks"
        payload = {
            "script": {
                "type": "audio",
                "audio_url": f"data:audio/mp3;base64,{audio_base64}"
            },
            "config": {
                "fluent": True,
                "pad_audio": 0.0
            },
            "source_url": "https://create-images-results.d-id.com/default-presenter-image.png"
        }
        
        headers = get_did_headers()
        
        did_response = requests.post(url, json=payload, headers=headers)
        did_response.raise_for_status()
        
        talk_data = did_response.json()
        talk_id = talk_data.get('id')
        
        # Return immediately with talk_id for polling
        return jsonify({
            "session_id": session_id,
            "user_text": user_text,
            "assistant_text": assistant_text,
            "audio_base64": audio_base64,
            "talk_id": talk_id,
            "status": "processing"
        })
    
    except Exception as e:
        print(f"Error in complete flow: {str(e)}")
        return jsonify({"error": f"Complete flow error: {str(e)}"}), 500


# Clean up old sessions periodically (simple cleanup for demo)
@app.route('/api/cleanup-sessions', methods=['POST'])
def cleanup_sessions():
    """Remove sessions older than 1 hour"""
    try:
        current_time = time.time()
        old_sessions = []
        
        for session_id, session_data in conversation_sessions.items():
            if current_time - session_data['created_at'] > 3600:  # 1 hour
                old_sessions.append(session_id)
        
        for session_id in old_sessions:
            del conversation_sessions[session_id]
        
        return jsonify({
            "message": f"Cleaned up {len(old_sessions)} old sessions"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Ensure static directories exist
    os.makedirs('static/audio', exist_ok=True)
    os.makedirs('static/video', exist_ok=True)
    
    # Start the server
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
