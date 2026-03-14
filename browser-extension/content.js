// AgentForge Local Bridge - Content Script
// Bridges the web application with the browser extension

(function() {
  'use strict';
  
  let isConnected = false;
  
  // Inject status indicator into AgentForge pages
  function injectStatusIndicator() {
    if (document.getElementById('agentforge-bridge-indicator')) return;
    
    const indicator = document.createElement('div');
    indicator.id = 'agentforge-bridge-indicator';
    indicator.innerHTML = `
      <div id="af-bridge-status" style="
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 99999;
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 16px;
        background: rgba(0, 0, 0, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 13px;
        color: #fff;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        cursor: pointer;
        transition: all 0.2s ease;
      ">
        <div id="af-bridge-dot" style="
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: #ef4444;
          animation: pulse 2s infinite;
        "></div>
        <span id="af-bridge-text">Local Bridge: Disconnected</span>
      </div>
      <style>
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        #af-bridge-status:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 25px rgba(0,0,0,0.4);
        }
      </style>
    `;
    document.body.appendChild(indicator);
    
    // Click to toggle connection
    document.getElementById('af-bridge-status').addEventListener('click', () => {
      chrome.runtime.sendMessage({ type: 'CONNECT' });
    });
  }
  
  // Update status indicator
  function updateStatusIndicator(connected) {
    isConnected = connected;
    const dot = document.getElementById('af-bridge-dot');
    const text = document.getElementById('af-bridge-text');
    
    if (dot && text) {
      dot.style.background = connected ? '#22c55e' : '#ef4444';
      dot.style.animation = connected ? 'none' : 'pulse 2s infinite';
      text.textContent = connected ? 'Local Bridge: Connected' : 'Local Bridge: Disconnected';
    }
  }
  
  // Listen for messages from background script
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    switch (message.type) {
      case 'CONNECTION_STATUS':
        updateStatusIndicator(message.connected);
        // Dispatch custom event for the web app
        window.dispatchEvent(new CustomEvent('agentforge-bridge-status', {
          detail: { connected: message.connected }
        }));
        break;
        
      case 'FILE_SAVED':
        window.dispatchEvent(new CustomEvent('agentforge-file-saved', {
          detail: message.data
        }));
        showNotification('File Saved', message.data.filepath, 'success');
        break;
        
      case 'BUILD_STATUS':
        window.dispatchEvent(new CustomEvent('agentforge-build-status', {
          detail: { status: message.status, data: message.data }
        }));
        
        if (message.status === 'complete') {
          showNotification('Build Complete', 'Project built successfully!', 'success');
        } else if (message.status === 'error') {
          showNotification('Build Failed', message.data.error, 'error');
        }
        break;
    }
    sendResponse({ received: true });
    return true;
  });
  
  // Listen for messages from the web page
  window.addEventListener('agentforge-push-files', async (event) => {
    const { files, projectPath, engine } = event.detail;
    
    if (!isConnected) {
      showNotification('Not Connected', 'Please connect to Local Bridge first', 'error');
      return;
    }
    
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'PUSH_FILES',
        data: { files, projectPath, engine }
      });
      
      if (response.success) {
        showNotification('Files Pushed', `Sending ${files.length} files to local project`, 'info');
      } else {
        showNotification('Push Failed', response.error, 'error');
      }
    } catch (error) {
      showNotification('Error', error.message, 'error');
    }
  });
  
  // Listen for build trigger from web page
  window.addEventListener('agentforge-trigger-build', async (event) => {
    const { projectPath, engine, buildConfig } = event.detail;
    
    if (!isConnected) {
      showNotification('Not Connected', 'Please connect to Local Bridge first', 'error');
      return;
    }
    
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'TRIGGER_BUILD',
        data: { projectPath, engine, buildConfig }
      });
      
      if (response.success) {
        showNotification('Build Started', 'Building project locally...', 'info');
      } else {
        showNotification('Build Failed', response.error, 'error');
      }
    } catch (error) {
      showNotification('Error', error.message, 'error');
    }
  });
  
  // Listen for config updates from web page
  window.addEventListener('agentforge-set-config', async (event) => {
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'SET_CONFIG',
        data: event.detail
      });
      
      if (response.success) {
        showNotification('Config Saved', 'Local bridge configuration updated', 'success');
      }
    } catch (error) {
      console.error('[AgentForge] Config error:', error);
    }
  });
  
  // Request connection status from web page
  window.addEventListener('agentforge-get-status', async () => {
    try {
      const response = await chrome.runtime.sendMessage({ type: 'GET_STATUS' });
      window.dispatchEvent(new CustomEvent('agentforge-bridge-status', {
        detail: { connected: response.connected }
      }));
    } catch (error) {
      window.dispatchEvent(new CustomEvent('agentforge-bridge-status', {
        detail: { connected: false }
      }));
    }
  });
  
  // Show toast notification
  function showNotification(title, message, type = 'info') {
    const colors = {
      success: { bg: 'rgba(34, 197, 94, 0.9)', border: '#22c55e' },
      error: { bg: 'rgba(239, 68, 68, 0.9)', border: '#ef4444' },
      info: { bg: 'rgba(59, 130, 246, 0.9)', border: '#3b82f6' }
    };
    
    const color = colors[type] || colors.info;
    
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed;
      bottom: 70px;
      left: 20px;
      z-index: 99999;
      padding: 12px 20px;
      background: ${color.bg};
      border: 1px solid ${color.border};
      border-radius: 8px;
      font-family: system-ui, -apple-system, sans-serif;
      color: white;
      backdrop-filter: blur(10px);
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      animation: slideIn 0.3s ease;
      max-width: 300px;
    `;
    
    toast.innerHTML = `
      <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px;">${title}</div>
      <div style="font-size: 12px; opacity: 0.9;">${message}</div>
      <style>
        @keyframes slideIn {
          from { transform: translateX(-100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      </style>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.animation = 'slideIn 0.3s ease reverse';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }
  
  // Initialize
  function init() {
    // Only inject on AgentForge pages
    if (window.location.hostname.includes('emergentagent.com') || 
        window.location.hostname === 'localhost') {
      injectStatusIndicator();
      
      // Get initial status
      chrome.runtime.sendMessage({ type: 'GET_STATUS' }, (response) => {
        if (response) {
          updateStatusIndicator(response.connected);
        }
      });
    }
  }
  
  // Wait for DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
