import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Botel AI Widget Preview",
  description: "Preview the Botel AI chat and voice widget",
};

export default function WidgetPreviewPage() {
  // This renders the widget directly without needing the embed script
  return (
    <html>
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Botel AI Widget</title>
      </head>
      <body
        style={{
          margin: 0,
          padding: 0,
          height: "100vh",
          backgroundColor: "#f5f5f5",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
            flexDirection: "column",
            fontFamily: "Arial, sans-serif",
          }}
        >
          <h1 style={{ color: "#333", marginBottom: 20 }}>
            Botel AI Widget Preview
          </h1>
          <p style={{ color: "#666", marginBottom: 40 }}>
            The widget button appears in the bottom-right corner
          </p>
        </div>

        {/* Inline the widget HTML content */}
        <div
          dangerouslySetInnerHTML={{
            __html: `
              <style>
                ${getWidgetStyles()}
              </style>
              
              <!-- Widget Button -->
              <div id="botel-widget-button" class="botel-widget-button">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2C6.48 2 2 6.48 2 12C2 13.19 2.23 14.32 2.64 15.36L2 22L8.64 21.36C9.68 21.77 10.81 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM17 13H15V11H17V13ZM13 13H11V11H13V13ZM9 13H7V11H9V13Z" fill="currentColor"/>
                </svg>
              </div>

              <!-- Widget Container -->
              <div id="botel-widget-container" class="botel-widget-container hidden">
                <!-- Header -->
                <div class="botel-widget-header">
                  <div class="botel-header-info">
                    <h3>Botel AI Assistant</h3>
                    <span class="botel-status-indicator">Online</span>
                  </div>
                  <button class="botel-close-button" id="botel-close-widget">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                  </button>
                </div>

                <!-- Mode Toggle -->
                <div class="botel-mode-toggle">
                  <button class="botel-mode-button active" data-mode="chat">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M8 12H16M8 8H16M8 16H12M4 4H20C20.5523 4 21 4.44772 21 5V19C21 19.5523 20.5523 20 20 20H4C3.44772 20 3 19.5523 3 19V5C3 4.44772 3.44772 4 4 4Z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    Chat
                  </button>
                  <button class="botel-mode-button" data-mode="voice">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2C10.8954 2 10 2.89543 10 4V12C10 13.1046 10.8954 14 12 14C13.1046 14 14 13.1046 14 12V4C14 2.89543 13.1046 2 12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                      <path d="M17 12C17 14.7614 14.7614 17 12 17M7 12C7 14.7614 9.23858 17 12 17M12 17V21M8 21H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    Voice
                  </button>
                </div>

                <!-- Chat Container -->
                <div id="botel-chat-container" class="botel-chat-container">
                  <div class="botel-messages-container" id="botel-messages">
                    <div class="botel-message assistant">
                      <div class="botel-avatar">AI</div>
                      <div class="botel-message-content">
                        Hi! I'm Jamie from Botel AI. How can I help you today?
                      </div>
                    </div>
                  </div>
                  
                  <!-- Chat Input -->
                  <div class="botel-chat-input-container">
                    <input 
                      type="text" 
                      id="botel-chat-input" 
                      class="botel-chat-input" 
                      placeholder="Type your message..."
                      autocomplete="off"
                    />
                    <button id="botel-send-button" class="botel-send-button">
                      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- Voice Container -->
                <div id="botel-voice-container" class="botel-voice-container hidden">
                  <!-- Voice Animation -->
                  <div class="botel-voice-animation-container">
                    <div class="botel-voice-avatar">
                      <div class="botel-avatar-circle">
                        <span>AI</span>
                      </div>
                      <div class="botel-voice-waves" id="botel-voice-waves">
                        <div class="botel-wave"></div>
                        <div class="botel-wave"></div>
                        <div class="botel-wave"></div>
                        <div class="botel-wave"></div>
                        <div class="botel-wave"></div>
                      </div>
                    </div>
                    <p class="botel-voice-status" id="botel-voice-status">Click microphone to start</p>
                  </div>

                  <!-- Voice Controls -->
                  <div class="botel-voice-controls">
                    <button id="botel-mic-button" class="botel-control-button botel-mic-button">
                      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2C10.8954 2 10 2.89543 10 4V12C10 13.1046 10.8954 14 12 14C13.1046 14 14 13.1046 14 12V4C14 2.89543 13.1046 2 12 2Z" fill="currentColor"/>
                        <path d="M17 12C17 14.7614 14.7614 17 12 17M7 12C7 14.7614 9.23858 17 12 17M12 17V21M8 21H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                      </svg>
                    </button>
                    
                    <button id="botel-mute-button" class="botel-control-button secondary">
                      <svg class="unmuted" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M11 5L6 9H2V15H6L11 19V5Z" fill="currentColor"/>
                        <path d="M15.54 8.46C16.4774 9.39764 17.0039 10.6692 17.0039 11.995C17.0039 13.3208 16.4774 14.5924 15.54 15.53M19.07 4.93C20.9447 6.80528 21.9979 9.34836 21.9979 12C21.9979 14.6516 20.9447 17.1947 19.07 19.07" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                      </svg>
                      <svg class="muted hidden" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M11 5L6 9H2V15H6L11 19V5Z" fill="currentColor"/>
                        <path d="M23 9L17 15M17 9L23 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                      </svg>
                    </button>

                    <button id="botel-end-call-button" class="botel-control-button botel-end-call hidden">
                      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 9C15.5 9 18.5 10.5 20.5 12.5L22 11C19.5 8.5 16 7 12 7C8 7 4.5 8.5 2 11L3.5 12.5C5.5 10.5 8.5 9 12 9ZM21 17.5C21 18.3 20.3 19 19.5 19C18.7 19 18 18.3 18 17.5V15C16 16.5 14 17 12 17C10 17 8 16.5 6 15V17.5C6 18.3 5.3 19 4.5 19C3.7 19 3 18.3 3 17.5V14.5C3 14 3.5 13.5 4 13.5C6 15 9 16 12 16C15 16 18 15 20 13.5C20.5 13.5 21 14 21 14.5V17.5Z" fill="currentColor"/>
                      </svg>
                    </button>
                  </div>

                  <!-- Voice Transcript -->
                  <div class="botel-voice-transcript">
                    <div class="botel-transcript-header">Conversation</div>
                    <div class="botel-transcript-messages" id="botel-transcript-messages"></div>
                  </div>
                </div>
              </div>
              
              <script src="https://unpkg.com/livekit-client/dist/livekit-client.umd.min.js"></script>
              <script>
                ${getWidgetScript()}
              </script>
            `,
          }}
        />
      </body>
    </html>
  );
}

function getWidgetStyles() {
  return `
    .hidden { display: none !important; }
    
    .botel-widget-button {
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 60px;
      height: 60px;
      background: #002cf2;
      border-radius: 50%;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      z-index: 999998;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .botel-widget-button:hover {
      transform: scale(1.05);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
    }
    
    .botel-widget-button svg {
      width: 30px;
      height: 30px;
      color: white;
    }
    
    .botel-widget-container {
      position: fixed;
      bottom: 90px;
      right: 20px;
      width: 380px;
      height: 600px;
      background: white;
      border-radius: 16px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
      z-index: 999999;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .botel-widget-header {
      background: #002cf2;
      color: white;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    
    .botel-header-info h3 {
      font-size: 18px;
      font-weight: 600;
      margin: 0 0 2px 0;
    }
    
    .botel-status-indicator {
      display: inline-flex;
      align-items: center;
      font-size: 12px;
      opacity: 0.9;
    }
    
    .botel-status-indicator::before {
      content: '';
      width: 8px;
      height: 8px;
      background: #4ade80;
      border-radius: 50%;
      margin-right: 6px;
      animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
      0% { opacity: 1; }
      50% { opacity: 0.5; }
      100% { opacity: 1; }
    }
    
    .botel-close-button {
      background: none;
      border: none;
      color: white;
      cursor: pointer;
      padding: 4px;
      opacity: 0.8;
      transition: opacity 0.2s;
    }
    
    .botel-close-button:hover {
      opacity: 1;
    }
    
    .botel-close-button svg {
      width: 24px;
      height: 24px;
    }
    
    .botel-mode-toggle {
      display: flex;
      background: #f3f4f6;
      padding: 4px;
      gap: 4px;
    }
    
    .botel-mode-button {
      flex: 1;
      padding: 8px 12px;
      background: none;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      font-size: 14px;
      color: #6b7280;
      transition: all 0.2s;
    }
    
    .botel-mode-button svg {
      width: 18px;
      height: 18px;
    }
    
    .botel-mode-button.active {
      background: white;
      color: #002cf2;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .botel-chat-container,
    .botel-voice-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      background: white;
    }
    
    .botel-messages-container {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      scroll-behavior: smooth;
    }
    
    .botel-message {
      display: flex;
      gap: 12px;
      margin-bottom: 16px;
      animation: fadeIn 0.3s ease-out;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .botel-message.user {
      flex-direction: row-reverse;
    }
    
    .botel-avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: #002cf2;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      font-size: 14px;
      flex-shrink: 0;
    }
    
    .botel-message.user .botel-avatar {
      background: #e5e7eb;
      color: #374151;
    }
    
    .botel-message-content {
      max-width: 70%;
      padding: 12px 16px;
      border-radius: 12px;
      background: #f3f4f6;
      color: #111827;
      font-size: 14px;
      line-height: 1.5;
    }
    
    .botel-message.user .botel-message-content {
      background: #002cf2;
      color: white;
    }
    
    .botel-chat-input-container {
      padding: 16px;
      border-top: 1px solid #e5e7eb;
      display: flex;
      gap: 8px;
    }
    
    .botel-chat-input {
      flex: 1;
      padding: 10px 16px;
      border: 1px solid #e5e7eb;
      border-radius: 24px;
      outline: none;
      font-size: 14px;
      transition: border-color 0.2s;
    }
    
    .botel-chat-input:focus {
      border-color: #002cf2;
    }
    
    .botel-send-button {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: #002cf2;
      border: none;
      color: white;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background-color 0.2s;
    }
    
    .botel-send-button:hover {
      background: #0022d0;
    }
    
    .botel-send-button svg {
      width: 20px;
      height: 20px;
    }
    
    .botel-voice-animation-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    
    .botel-voice-avatar {
      position: relative;
      margin-bottom: 24px;
    }
    
    .botel-avatar-circle {
      width: 120px;
      height: 120px;
      border-radius: 50%;
      background: #002cf2;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 48px;
      font-weight: 600;
      position: relative;
      z-index: 2;
    }
    
    .botel-voice-waves {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      display: none;
    }
    
    .botel-voice-waves.active {
      display: block;
    }
    
    .botel-wave {
      position: absolute;
      border: 2px solid #002cf2;
      border-radius: 50%;
      opacity: 0;
      animation: wave 3s linear infinite;
    }
    
    .botel-wave:nth-child(1) { animation-delay: 0s; }
    .botel-wave:nth-child(2) { animation-delay: 0.6s; }
    .botel-wave:nth-child(3) { animation-delay: 1.2s; }
    .botel-wave:nth-child(4) { animation-delay: 1.8s; }
    .botel-wave:nth-child(5) { animation-delay: 2.4s; }
    
    @keyframes wave {
      0% {
        width: 120px;
        height: 120px;
        opacity: 0.6;
        top: -60px;
        left: -60px;
      }
      100% {
        width: 300px;
        height: 300px;
        opacity: 0;
        top: -150px;
        left: -150px;
      }
    }
    
    .botel-voice-status {
      font-size: 16px;
      color: #6b7280;
      text-align: center;
      margin: 0;
    }
    
    .botel-voice-controls {
      display: flex;
      justify-content: center;
      gap: 16px;
      margin-top: 32px;
    }
    
    .botel-control-button {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
    }
    
    .botel-mic-button {
      background: #002cf2;
      color: white;
    }
    
    .botel-mic-button:hover {
      background: #0022d0;
      transform: scale(1.05);
    }
    
    .botel-mic-button.active {
      background: #10b981;
    }
    
    .botel-control-button.secondary {
      background: #f3f4f6;
      color: #374151;
    }
    
    .botel-control-button.secondary:hover {
      background: #e5e7eb;
    }
    
    .botel-end-call {
      background: #ef4444;
      color: white;
    }
    
    .botel-end-call:hover {
      background: #dc2626;
    }
    
    .botel-control-button svg {
      width: 24px;
      height: 24px;
    }
    
    .botel-voice-transcript {
      margin-top: 24px;
      padding: 16px;
      background: #f9fafb;
      border-radius: 8px;
      max-height: 200px;
      overflow-y: auto;
    }
    
    .botel-transcript-header {
      font-size: 12px;
      font-weight: 600;
      color: #6b7280;
      margin-bottom: 8px;
      text-transform: uppercase;
    }
  `;
}

function getWidgetScript() {
  return `
    (function() {
      let isOpen = false;
      let mode = 'chat';
      let room = null;
      let isCallActive = false;
      let isMuted = false;
      
      // Setup event listeners
      document.getElementById('botel-widget-button').addEventListener('click', toggleWidget);
      document.getElementById('botel-close-widget').addEventListener('click', closeWidget);
      document.getElementById('botel-send-button').addEventListener('click', sendMessage);
      document.getElementById('botel-chat-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
      });
      document.getElementById('botel-mic-button').addEventListener('click', toggleVoiceCall);
      document.getElementById('botel-mute-button').addEventListener('click', toggleMute);
      document.getElementById('botel-end-call-button').addEventListener('click', endCall);
      
      document.querySelectorAll('.botel-mode-button').forEach(btn => {
        btn.addEventListener('click', () => switchMode(btn.dataset.mode));
      });
      
      function toggleWidget() {
        isOpen = !isOpen;
        const container = document.getElementById('botel-widget-container');
        const button = document.getElementById('botel-widget-button');
        
        if (isOpen) {
          container.classList.remove('hidden');
          button.classList.add('hidden');
        } else {
          container.classList.add('hidden');
          button.classList.remove('hidden');
        }
      }
      
      function closeWidget() {
        isOpen = false;
        document.getElementById('botel-widget-container').classList.add('hidden');
        document.getElementById('botel-widget-button').classList.remove('hidden');
      }
      
      function switchMode(newMode) {
        mode = newMode;
        document.querySelectorAll('.botel-mode-button').forEach(btn => {
          btn.classList.toggle('active', btn.dataset.mode === mode);
        });
        
        document.getElementById('botel-chat-container').classList.toggle('hidden', mode !== 'chat');
        document.getElementById('botel-voice-container').classList.toggle('hidden', mode !== 'voice');
      }
      
      function sendMessage() {
        const input = document.getElementById('botel-chat-input');
        const message = input.value.trim();
        if (!message) return;
        
        addMessage('user', message);
        input.value = '';
        
        // Simulate response
        setTimeout(() => {
          addMessage('assistant', 'Thanks for your message! In a live environment, I would connect to your AI agent to provide a real response.');
        }, 1000);
      }
      
      function addMessage(role, content) {
        const messagesContainer = document.getElementById('botel-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'botel-message ' + role;
        messageDiv.innerHTML = \`
          <div class="botel-avatar">\${role === 'user' ? 'U' : 'AI'}</div>
          <div class="botel-message-content">\${content}</div>
        \`;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
      
      async function toggleVoiceCall() {
        if (!isCallActive) {
          await startVoiceCall();
        } else {
          await endCall();
        }
      }
      
      async function startVoiceCall() {
        try {
          isCallActive = true;
          document.getElementById('botel-mic-button').classList.add('active');
          document.getElementById('botel-end-call-button').classList.remove('hidden');
          document.getElementById('botel-voice-status').textContent = 'Connecting...';
          document.getElementById('botel-voice-waves').classList.add('active');
          
          // In production, connect to LiveKit here
          setTimeout(() => {
            document.getElementById('botel-voice-status').textContent = 'Connected - Speak now';
          }, 1000);
          
        } catch (error) {
          console.error('Error starting call:', error);
          isCallActive = false;
          document.getElementById('botel-mic-button').classList.remove('active');
          document.getElementById('botel-voice-status').textContent = 'Connection failed';
        }
      }
      
      async function endCall() {
        if (room) {
          await room.disconnect();
          room = null;
        }
        isCallActive = false;
        document.getElementById('botel-mic-button').classList.remove('active');
        document.getElementById('botel-end-call-button').classList.add('hidden');
        document.getElementById('botel-voice-status').textContent = 'Click microphone to start';
        document.getElementById('botel-voice-waves').classList.remove('active');
      }
      
      function toggleMute() {
        isMuted = !isMuted;
        const muteButton = document.getElementById('botel-mute-button');
        muteButton.querySelector('.unmuted').classList.toggle('hidden', isMuted);
        muteButton.querySelector('.muted').classList.toggle('hidden', !isMuted);
        
        if (room && room.localParticipant) {
          room.localParticipant.setMicrophoneEnabled(!isMuted);
        }
      }
    })();
  `;
}
