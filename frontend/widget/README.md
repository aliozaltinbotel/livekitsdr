# Botel AI Widget Integration Guide

## Overview

The Botel AI Widget allows you to add an AI-powered chat and voice assistant to any website. It provides a seamless way for your website visitors to interact with your AI assistant through both text chat and voice conversations.

## Features

- 💬 **Text Chat**: Traditional chat interface with message history
- 🎤 **Voice Calls**: Real-time voice conversations with the AI assistant
- 🎨 **Customizable**: Configure colors, position, and branding
- 📱 **Responsive**: Works on desktop and mobile devices
- 🔐 **Secure**: Uses LiveKit for secure, real-time communication

## Quick Start

### Method 1: Simple Embed (Recommended)

Add this code to your website's HTML, just before the closing `</body>` tag:

```html
<script>
  window.BotelWidgetConfig = {
    // Required: Your API endpoint or connection details
    apiEndpoint: 'https://your-api.com/api/connection-details',
    // OR provide static credentials (less secure)
    // serverUrl: 'wss://your-livekit-server.com',
    // token: 'your-participant-token',
    
    // Optional customization
    position: 'bottom-right', // or 'bottom-left'
    primaryColor: '#002cf2',
    companyName: 'Your Company'
  };
</script>
<script src="https://your-domain.com/widget/embed.js" async></script>
```

### Method 2: React Component

If you're using React, you can use the BotelWidget component:

```tsx
import { BotelWidget } from '@botel/widget';

function App() {
  return (
    <>
      {/* Your app content */}
      <BotelWidget
        serverUrl="wss://your-livekit-server.com"
        token="your-participant-token"
        position="bottom-right"
        primaryColor="#002cf2"
        companyName="Your Company"
      />
    </>
  );
}
```

### Method 3: Self-Hosted HTML

For complete control, you can host the widget HTML on your own server:

1. Copy `widget.html` to your server
2. Update the configuration in the HTML file
3. Include it in an iframe:

```html
<iframe 
  src="https://your-domain.com/widget.html"
  style="position: fixed; bottom: 0; right: 0; border: none; z-index: 999999;"
  allow="microphone; camera"
></iframe>
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiEndpoint` | string | `/api/connection-details` | API endpoint to fetch LiveKit credentials |
| `serverUrl` | string | - | LiveKit server URL (if not using API endpoint) |
| `token` | string | - | LiveKit participant token (if not using API endpoint) |
| `position` | string | `'bottom-right'` | Widget position: `'bottom-right'` or `'bottom-left'` |
| `primaryColor` | string | `'#002cf2'` | Primary color for buttons and accents |
| `companyName` | string | `'Botel AI'` | Company name displayed in the widget |

## API Endpoint

If using the `apiEndpoint` option, your endpoint should return:

```json
{
  "serverUrl": "wss://your-livekit-server.com",
  "participantToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Styling

The widget is designed to work with any website without CSS conflicts. It uses:
- Shadow DOM or iframe isolation
- Scoped CSS with unique class names
- Responsive design that adapts to mobile screens

## Browser Support

- Chrome/Edge 80+
- Firefox 75+
- Safari 13+
- Mobile browsers (iOS Safari, Chrome for Android)

## Security Considerations

1. **Use HTTPS**: The widget requires HTTPS for microphone access
2. **Token Security**: Generate participant tokens server-side
3. **CORS**: Configure your API to allow widget requests
4. **CSP**: Add LiveKit domains to your Content Security Policy if needed

## Events

You can listen to widget events:

```javascript
window.addEventListener('message', (event) => {
  if (event.data.type === 'botel-widget-event') {
    console.log('Widget event:', event.data);
  }
});
```

Available events:
- `widget-opened`
- `widget-closed`
- `chat-message-sent`
- `voice-call-started`
- `voice-call-ended`

## Troubleshooting

### Widget not appearing
- Check browser console for errors
- Verify the script URL is correct
- Ensure your domain is whitelisted in CORS settings

### Microphone not working
- Ensure your site uses HTTPS
- Check browser microphone permissions
- Verify LiveKit credentials are valid

### Connection issues
- Check LiveKit server is running
- Verify firewall allows WebSocket connections
- Test with LiveKit's connection test tool

## Advanced Customization

For advanced customization, you can:

1. Fork the widget source code
2. Modify styles and functionality
3. Build and host your own version

```bash
# Clone the repository
git clone https://github.com/your-org/botel-widget

# Install dependencies
npm install

# Customize and build
npm run build

# Deploy to your CDN
npm run deploy
```

## Support

- Documentation: https://docs.botel.ai/widget
- GitHub Issues: https://github.com/your-org/botel-widget/issues
- Email: support@botel.ai

## License

The Botel AI Widget is licensed under the MIT License. See LICENSE file for details.