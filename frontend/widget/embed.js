/**
 * Botel AI Widget Embed Script
 * 
 * This script creates an iframe that loads the widget from your domain.
 * The widget handles all LiveKit connections internally.
 * 
 * Usage:
 * <script>
 *   window.BotelWidgetConfig = {
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
    companyName: 'Botel AI'
  };

  // Merge user config with defaults
  const config = Object.assign({}, defaultConfig, window.BotelWidgetConfig || {});

  // Get the script's src to determine the base URL
  const scripts = document.getElementsByTagName('script');
  const currentScript = scripts[scripts.length - 1];
  const scriptSrc = currentScript.src;
  const baseUrl = scriptSrc.substring(0, scriptSrc.lastIndexOf('/widget/embed.js'));

  // Create iframe
  function createWidgetIframe() {
    const iframe = document.createElement('iframe');
    iframe.id = 'botel-widget-iframe';
    iframe.style.cssText = `
      position: fixed;
      border: none;
      z-index: 999999;
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
      background: transparent;
      pointer-events: none;
    `;
    
    // Build the widget URL with config parameters
    const params = new URLSearchParams({
      position: config.position,
      primaryColor: config.primaryColor,
      companyName: config.companyName
    });
    
    iframe.src = `${baseUrl}/widget-standalone?${params.toString()}`;
    iframe.setAttribute('allow', 'microphone; camera');
    
    document.body.appendChild(iframe);
    
    // Set up message passing for iframe communication
    window.addEventListener('message', (event) => {
      if (event.origin !== baseUrl) return;
      
      if (event.data.type === 'botel-widget-resize') {
        iframe.style.pointerEvents = event.data.active ? 'all' : 'none';
      }
    });
    
    return iframe;
  }

  // Initialize widget when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createWidgetIframe);
  } else {
    createWidgetIframe();
  }
})();