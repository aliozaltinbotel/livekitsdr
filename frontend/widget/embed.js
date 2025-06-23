/**
 * Botel AI Widget Embed Script
 * 
 * Usage:
 * <script>
 *   window.BotelWidgetConfig = {
 *     serverUrl: 'wss://your-livekit-server.com',
 *     token: 'your-participant-token',
 *     position: 'bottom-right', // or 'bottom-left'
 *     primaryColor: '#002cf2',
 *     companyName: 'Your Company'
 *   };
 * </script>
 * <script src="https://your-domain.com/widget/embed.js" async></script>
 */

(function() {
  'use strict';

  // Default configuration
  const defaultConfig = {
    position: 'bottom-right',
    primaryColor: '#002cf2',
    companyName: 'Botel AI',
    apiEndpoint: '/api/connection-details'
  };

  // Merge user config with defaults
  const config = Object.assign({}, defaultConfig, window.BotelWidgetConfig || {});

  // Create iframe to isolate widget styles
  function createWidgetIframe() {
    const iframe = document.createElement('iframe');
    iframe.id = 'botel-widget-iframe';
    iframe.style.cssText = `
      position: fixed;
      border: none;
      z-index: 999999;
      transition: all 0.3s ease;
      ${config.position === 'bottom-right' ? 'right: 0; left: auto;' : 'left: 0; right: auto;'}
      bottom: 0;
      width: 100px;
      height: 100px;
      background: transparent;
      pointer-events: none;
    `;
    
    iframe.setAttribute('allow', 'microphone; camera');
    document.body.appendChild(iframe);
    
    return iframe;
  }

  // Initialize widget
  function initWidget() {
    const iframe = createWidgetIframe();
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    
    // Widget HTML with embedded styles
    const widgetHTML = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          ${getWidgetStyles()}
        </style>
      </head>
      <body>
        <div id="botel-widget-root"></div>
        <script src="https://unpkg.com/livekit-client/dist/livekit-client.umd.min.js"></script>
        <script>
          window.BotelConfig = ${JSON.stringify(config)};
          ${getWidgetScript()}
        </script>
      </body>
      </html>
    `;
    
    iframeDoc.open();
    iframeDoc.write(widgetHTML);
    iframeDoc.close();
    
    // Handle iframe resizing
    window.addEventListener('message', (event) => {
      if (event.data.type === 'botel-resize') {
        iframe.style.width = event.data.width + 'px';
        iframe.style.height = event.data.height + 'px';
        iframe.style.pointerEvents = event.data.interactive ? 'all' : 'none';
      }
    });
  }

  // Get widget styles
  function getWidgetStyles() {
    return `
      * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
      }
      
      body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: transparent;
        overflow: hidden;
      }
      
      .widget-button {
        position: fixed;
        ${config.position === 'bottom-right' ? 'right: 20px;' : 'left: 20px;'}
        bottom: 20px;
        width: 60px;
        height: 60px;
        background: ${config.primaryColor};
        border-radius: 50%;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s, box-shadow 0.2s;
        border: none;
        color: white;
      }
      
      .widget-button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
      }
      
      .widget-container {
        position: fixed;
        ${config.position === 'bottom-right' ? 'right: 20px;' : 'left: 20px;'}
        bottom: 90px;
        width: 380px;
        height: 600px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        transform-origin: ${config.position === 'bottom-right' ? 'bottom right' : 'bottom left'};
        animation: slideIn 0.3s ease-out;
      }
      
      @keyframes slideIn {
        from {
          opacity: 0;
          transform: scale(0.95) translateY(20px);
        }
        to {
          opacity: 1;
          transform: scale(1) translateY(0);
        }
      }
      
      .widget-header {
        background: ${config.primaryColor};
        color: white;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      
      .close-button {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 4px;
        opacity: 0.8;
      }
      
      .close-button:hover {
        opacity: 1;
      }
      
      .mode-toggle {
        display: flex;
        background: #f3f4f6;
        padding: 4px;
        gap: 4px;
      }
      
      .mode-button {
        flex: 1;
        padding: 8px 12px;
        background: none;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        color: #6b7280;
        transition: all 0.2s;
      }
      
      .mode-button.active {
        background: white;
        color: ${config.primaryColor};
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      }
      
      .chat-container, .voice-container {
        flex: 1;
        display: flex;
        flex-direction: column;
        background: white;
      }
      
      .messages-container {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
      }
      
      .message {
        display: flex;
        gap: 12px;
        margin-bottom: 16px;
        animation: fadeIn 0.3s ease-out;
      }
      
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      
      .message.user {
        flex-direction: row-reverse;
      }
      
      .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: ${config.primaryColor};
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 14px;
      }
      
      .message.user .avatar {
        background: #e5e7eb;
        color: #374151;
      }
      
      .message-content {
        max-width: 70%;
        padding: 12px 16px;
        border-radius: 12px;
        background: #f3f4f6;
        color: #111827;
        font-size: 14px;
        line-height: 1.5;
      }
      
      .message.user .message-content {
        background: ${config.primaryColor};
        color: white;
      }
      
      .chat-input-container {
        padding: 16px;
        border-top: 1px solid #e5e7eb;
        display: flex;
        gap: 8px;
      }
      
      .chat-input {
        flex: 1;
        padding: 10px 16px;
        border: 1px solid #e5e7eb;
        border-radius: 24px;
        outline: none;
        font-size: 14px;
      }
      
      .chat-input:focus {
        border-color: ${config.primaryColor};
      }
      
      .send-button {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: ${config.primaryColor};
        border: none;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .voice-animation-container {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
      }
      
      .voice-avatar {
        position: relative;
        margin-bottom: 24px;
      }
      
      .avatar-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: ${config.primaryColor};
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 48px;
        font-weight: 600;
      }
      
      .voice-waves {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
      }
      
      .voice-waves.active .wave {
        position: absolute;
        border: 2px solid ${config.primaryColor};
        border-radius: 50%;
        animation: wave 3s linear infinite;
      }
      
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
      
      .voice-controls {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin-top: 32px;
      }
      
      .control-button {
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
      
      .mic-button {
        background: ${config.primaryColor};
        color: white;
      }
      
      .mic-button.active {
        background: #10b981;
      }
      
      .hidden {
        display: none !important;
      }
    `;
  }

  // Get widget JavaScript
  function getWidgetScript() {
    return `
      (function() {
        const config = window.BotelConfig;
        let isOpen = false;
        let mode = 'chat';
        let room = null;
        let isCallActive = false;
        
        // Update parent iframe size
        function updateIframeSize() {
          const width = isOpen ? 400 : 100;
          const height = isOpen ? 690 : 100;
          window.parent.postMessage({
            type: 'botel-resize',
            width: width,
            height: height,
            interactive: true
          }, '*');
        }
        
        // Create widget HTML
        function createWidget() {
          const root = document.getElementById('botel-widget-root');
          
          root.innerHTML = \`
            <button class="widget-button" id="widget-button">
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
                <path d="M12 2C6.48 2 2 6.48 2 12C2 13.19 2.23 14.32 2.64 15.36L2 22L8.64 21.36C9.68 21.77 10.81 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM17 13H15V11H17V13ZM13 13H11V11H13V13ZM9 13H7V11H9V13Z" fill="currentColor"/>
              </svg>
            </button>
            
            <div class="widget-container hidden" id="widget-container">
              <div class="widget-header">
                <div>
                  <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 2px;">\${config.companyName} Assistant</h3>
                  <span style="font-size: 12px; opacity: 0.9;">Online</span>
                </div>
                <button class="close-button" id="close-button">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
              
              <div class="mode-toggle">
                <button class="mode-button active" data-mode="chat">Chat</button>
                <button class="mode-button" data-mode="voice">Voice</button>
              </div>
              
              <div class="chat-container" id="chat-container">
                <div class="messages-container" id="messages">
                  <div class="message assistant">
                    <div class="avatar">AI</div>
                    <div class="message-content">
                      Hi! I'm Jamie from \${config.companyName}. How can I help you today?
                    </div>
                  </div>
                </div>
                
                <div class="chat-input-container">
                  <input type="text" class="chat-input" id="chat-input" placeholder="Type your message..." />
                  <button class="send-button" id="send-button">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                      <path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                </div>
              </div>
              
              <div class="voice-container hidden" id="voice-container">
                <div class="voice-animation-container">
                  <div class="voice-avatar">
                    <div class="avatar-circle">AI</div>
                    <div class="voice-waves" id="voice-waves">
                      <div class="wave"></div>
                      <div class="wave"></div>
                      <div class="wave"></div>
                    </div>
                  </div>
                  <p id="voice-status">Click microphone to start</p>
                </div>
                
                <div class="voice-controls">
                  <button class="control-button mic-button" id="mic-button">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <path d="M12 2C10.8954 2 10 2.89543 10 4V12C10 13.1046 10.8954 14 12 14C13.1046 14 14 13.1046 14 12V4C14 2.89543 13.1046 2 12 2Z" fill="currentColor"/>
                      <path d="M17 12C17 14.7614 14.7614 17 12 17M7 12C7 14.7614 9.23858 17 12 17M12 17V21M8 21H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          \`;
          
          // Set up event listeners
          document.getElementById('widget-button').addEventListener('click', toggleWidget);
          document.getElementById('close-button').addEventListener('click', closeWidget);
          document.getElementById('send-button').addEventListener('click', sendMessage);
          document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
          });
          document.getElementById('mic-button').addEventListener('click', toggleVoiceCall);
          
          document.querySelectorAll('.mode-button').forEach(btn => {
            btn.addEventListener('click', () => switchMode(btn.dataset.mode));
          });
        }
        
        function toggleWidget() {
          isOpen = !isOpen;
          const container = document.getElementById('widget-container');
          const button = document.getElementById('widget-button');
          
          if (isOpen) {
            container.classList.remove('hidden');
            button.classList.add('hidden');
          } else {
            container.classList.add('hidden');
            button.classList.remove('hidden');
          }
          
          updateIframeSize();
        }
        
        function closeWidget() {
          isOpen = false;
          document.getElementById('widget-container').classList.add('hidden');
          document.getElementById('widget-button').classList.remove('hidden');
          updateIframeSize();
        }
        
        function switchMode(newMode) {
          mode = newMode;
          document.querySelectorAll('.mode-button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
          });
          
          document.getElementById('chat-container').classList.toggle('hidden', mode !== 'chat');
          document.getElementById('voice-container').classList.toggle('hidden', mode !== 'voice');
        }
        
        function sendMessage() {
          const input = document.getElementById('chat-input');
          const message = input.value.trim();
          if (!message) return;
          
          addMessage('user', message);
          input.value = '';
          
          // TODO: Send via LiveKit data channel
          setTimeout(() => {
            addMessage('assistant', 'I received your message: "' + message + '"');
          }, 1000);
        }
        
        function addMessage(role, content) {
          const messagesContainer = document.getElementById('messages');
          const messageDiv = document.createElement('div');
          messageDiv.className = 'message ' + role;
          messageDiv.innerHTML = \`
            <div class="avatar">\${role === 'user' ? 'U' : 'AI'}</div>
            <div class="message-content">\${content}</div>
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
            document.getElementById('mic-button').classList.add('active');
            document.getElementById('voice-status').textContent = 'Connecting...';
            document.getElementById('voice-waves').classList.add('active');
            
            // Initialize LiveKit
            if (!room) {
              room = new LivekitClient.Room();
            }
            
            // Get connection details
            const response = await fetch(config.apiEndpoint || '/api/connection-details');
            const { serverUrl, participantToken } = await response.json();
            
            await room.connect(serverUrl || config.serverUrl, participantToken || config.token);
            await room.localParticipant.setMicrophoneEnabled(true);
            
            document.getElementById('voice-status').textContent = 'Connected - Speak now';
          } catch (error) {
            console.error('Error starting call:', error);
            isCallActive = false;
            document.getElementById('mic-button').classList.remove('active');
            document.getElementById('voice-status').textContent = 'Connection failed';
          }
        }
        
        async function endCall() {
          if (room) {
            await room.disconnect();
            room = null;
          }
          isCallActive = false;
          document.getElementById('mic-button').classList.remove('active');
          document.getElementById('voice-status').textContent = 'Click microphone to start';
          document.getElementById('voice-waves').classList.remove('active');
        }
        
        // Initialize widget
        createWidget();
        updateIframeSize();
      })();
    `;
  }

  // Load widget when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWidget);
  } else {
    initWidget();
  }
})();