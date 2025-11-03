/**
 * Virtual Receptionist Avatar - Frontend JavaScript
 * ===================================================
 * Handles audio recording, API communication, and UI updates
 */

// Global variables
let mediaRecorder = null;
let audioChunks = [];
let sessionId = generateSessionId();
let isRecording = false;

// API base URL (change this for production)
const API_BASE_URL = window.location.origin;

/**
 * Generate a unique session ID for conversation tracking
 */
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Show status message to user
 */
function showStatus(message, type = 'info') {
    const statusEl = document.getElementById('statusMessage');
    statusEl.textContent = message;
    statusEl.className = 'status-message show status-' + type;
    
    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            statusEl.classList.remove('show');
        }, 5000);
    }
}

/**
 * Show/hide loading spinner
 */
function setLoading(loading) {
    const spinner = document.getElementById('loadingSpinner');
    if (loading) {
        spinner.classList.add('active');
    } else {
        spinner.classList.remove('active');
    }
}

/**
 * Add message to conversation log
 */
function addToConversationLog(message, isUser = true) {
    const logEl = document.getElementById('conversationLog');
    const itemsEl = document.getElementById('conversationItems');
    
    // Show conversation log
    logEl.style.display = 'block';
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = 'conversation-item ' + (isUser ? 'user-message' : 'assistant-message');
    
    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = isUser ? 'You:' : 'Receptionist:';
    
    const content = document.createElement('div');
    content.textContent = message;
    
    messageDiv.appendChild(label);
    messageDiv.appendChild(content);
    itemsEl.appendChild(messageDiv);
    
    // Scroll to bottom
    itemsEl.scrollTop = itemsEl.scrollHeight;
}

/**
 * Start audio recording
 */
async function startRecording() {
    try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Create media recorder with supported format
        const options = { mimeType: 'audio/webm' };
        mediaRecorder = new MediaRecorder(stream, options);
        
        // Reset audio chunks
        audioChunks = [];
        
        // Collect audio data
        mediaRecorder.addEventListener('dataavailable', (event) => {
            audioChunks.push(event.data);
        });
        
        // Handle recording stop
        mediaRecorder.addEventListener('stop', async () => {
            // Stop all tracks to release microphone
            stream.getTracks().forEach(track => track.stop());
            
            // Process the recorded audio
            await processRecording();
        });
        
        // Start recording
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        document.getElementById('talkBtn').style.display = 'none';
        document.getElementById('stopBtn').style.display = 'inline-block';
        document.getElementById('stopBtn').disabled = false;
        document.getElementById('recordingIndicator').classList.add('active');
        document.getElementById('resetBtn').disabled = true;
        
        showStatus('Recording started. Speak your question!', 'info');
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        showStatus('Error: Could not access microphone. Please grant permission.', 'error');
    }
}

/**
 * Stop audio recording
 */
function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Update UI
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('recordingIndicator').classList.remove('active');
        
        showStatus('Processing your recording...', 'info');
    }
}

/**
 * Process recorded audio and send to backend
 */
async function processRecording() {
    try {
        setLoading(true);
        
        // Create audio blob
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        
        // Create form data
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        formData.append('session_id', sessionId);
        
        // Send to backend for complete processing
        const response = await fetch(`${API_BASE_URL}/api/complete-flow`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to process audio');
        }
        
        const data = await response.json();
        
        // Update session ID
        sessionId = data.session_id;
        
        // Add messages to conversation log
        addToConversationLog(data.user_text, true);
        addToConversationLog(data.assistant_text, false);
        
        showStatus('Generating avatar video...', 'info');
        
        // Poll for video completion
        await pollVideoStatus(data.talk_id, data.audio_base64);
        
    } catch (error) {
        console.error('Error processing recording:', error);
        showStatus('Error: ' + error.message, 'error');
        setLoading(false);
        resetUI();
    }
}

/**
 * Poll D-ID API for video completion
 */
async function pollVideoStatus(talkId, audioBase64) {
    const maxAttempts = 60; // 2 minutes maximum
    let attempts = 0;
    
    const pollInterval = setInterval(async () => {
        try {
            attempts++;
            
            if (attempts > maxAttempts) {
                clearInterval(pollInterval);
                throw new Error('Video generation timeout. Please try again.');
            }
            
            const response = await fetch(`${API_BASE_URL}/api/check-video-status/${talkId}`);
            const data = await response.json();
            
            if (data.status === 'completed') {
                clearInterval(pollInterval);
                
                // Display the video
                displayVideo(data.video_url);
                
                // Play audio while video is loading (fallback)
                playAudioFallback(audioBase64);
                
                showStatus('Response ready!', 'success');
                setLoading(false);
                resetUI();
                
            } else if (data.status === 'error') {
                clearInterval(pollInterval);
                throw new Error('Video generation failed');
            }
            // else continue polling
            
        } catch (error) {
            clearInterval(pollInterval);
            console.error('Error polling video status:', error);
            showStatus('Error: ' + error.message, 'error');
            setLoading(false);
            resetUI();
        }
    }, 2000); // Poll every 2 seconds
}

/**
 * Display the generated video
 */
function displayVideo(videoUrl) {
    const videoEl = document.getElementById('avatarVideo');
    const placeholderEl = document.getElementById('placeholder');
    
    // Hide placeholder
    placeholderEl.style.display = 'none';
    
    // Show and play video
    videoEl.src = videoUrl;
    videoEl.style.display = 'block';
    videoEl.load();
    
    // Auto-play video when loaded
    videoEl.addEventListener('loadeddata', () => {
        videoEl.play().catch(err => {
            console.error('Error playing video:', err);
        });
    });
}

/**
 * Play audio as fallback (if video takes too long)
 */
function playAudioFallback(audioBase64) {
    try {
        const audio = new Audio('data:audio/mp3;base64,' + audioBase64);
        // Audio will play in background while video loads
    } catch (error) {
        console.error('Error playing audio fallback:', error);
    }
}

/**
 * Reset UI to initial state
 */
function resetUI() {
    document.getElementById('talkBtn').style.display = 'inline-block';
    document.getElementById('stopBtn').style.display = 'none';
    document.getElementById('stopBtn').disabled = true;
    document.getElementById('resetBtn').disabled = false;
    document.getElementById('recordingIndicator').classList.remove('active');
}

/**
 * Reset conversation (new session)
 */
function resetConversation() {
    // Generate new session ID
    sessionId = generateSessionId();
    
    // Clear conversation log
    const itemsEl = document.getElementById('conversationItems');
    itemsEl.innerHTML = '';
    document.getElementById('conversationLog').style.display = 'none';
    
    // Reset video
    const videoEl = document.getElementById('avatarVideo');
    const placeholderEl = document.getElementById('placeholder');
    
    videoEl.src = '';
    videoEl.style.display = 'none';
    placeholderEl.style.display = 'block';
    
    // Clear status
    document.getElementById('statusMessage').classList.remove('show');
    
    showStatus('New conversation started', 'success');
}

/**
 * Check if backend is available
 */
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('Backend status:', data);
        return true;
    } catch (error) {
        console.error('Backend is not available:', error);
        showStatus('Warning: Backend server is not responding', 'error');
        return false;
    }
}

/**
 * Initialize the app
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Virtual Receptionist Avatar initialized');
    
    // Check backend availability
    await checkBackendHealth();
    
    // Check for microphone support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showStatus('Error: Your browser does not support audio recording', 'error');
        document.getElementById('talkBtn').disabled = true;
    }
});

/**
 * Alternative: Step-by-step processing (for debugging)
 * Can be used instead of complete-flow endpoint
 */
async function processStepByStep() {
    try {
        setLoading(true);
        
        // Create audio blob
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        
        // Step 1: Speech-to-Text
        showStatus('Converting speech to text...', 'info');
        const sttFormData = new FormData();
        sttFormData.append('audio', audioBlob);
        
        const sttResponse = await fetch(`${API_BASE_URL}/api/speech-to-text`, {
            method: 'POST',
            body: sttFormData
        });
        
        const sttData = await sttResponse.json();
        const userText = sttData.transcription;
        
        addToConversationLog(userText, true);
        
        // Step 2: Chat with Gemini
        showStatus('Thinking...', 'info');
        const chatResponse = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: userText,
                session_id: sessionId
            })
        });
        
        const chatData = await chatResponse.json();
        sessionId = chatData.session_id;
        const assistantText = chatData.response;
        
        addToConversationLog(assistantText, false);
        
        // Step 3: Text-to-Speech
        showStatus('Generating voice...', 'info');
        const ttsResponse = await fetch(`${API_BASE_URL}/api/text-to-speech`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: assistantText })
        });
        
        const ttsData = await ttsResponse.json();
        const audioBase64 = ttsData.audio;
        
        // Step 4: Create Avatar Video
        showStatus('Creating avatar video...', 'info');
        const avatarResponse = await fetch(`${API_BASE_URL}/api/create-avatar-video`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ audio_base64: audioBase64 })
        });
        
        const avatarData = await avatarResponse.json();
        
        if (avatarData.status === 'completed') {
            displayVideo(avatarData.video_url);
            showStatus('Response ready!', 'success');
        } else {
            // Poll for completion
            await pollVideoStatus(avatarData.talk_id, audioBase64);
        }
        
        setLoading(false);
        resetUI();
        
    } catch (error) {
        console.error('Error in step-by-step processing:', error);
        showStatus('Error: ' + error.message, 'error');
        setLoading(false);
        resetUI();
    }
}
