// AgentForge Local Bridge - Popup Script

document.addEventListener('DOMContentLoaded', () => {
  const statusDot = document.getElementById('status-dot');
  const statusText = document.getElementById('status-text');
  const connectBtn = document.getElementById('connect-btn');
  const connectText = document.getElementById('connect-text');
  const settingsBtn = document.getElementById('settings-btn');
  const unrealPath = document.getElementById('unreal-path');
  const unityPath = document.getElementById('unity-path');
  
  // Get current status
  chrome.runtime.sendMessage({ type: 'GET_STATUS' }, (response) => {
    updateStatus(response?.connected || false);
  });
  
  // Load saved config
  chrome.storage.local.get(['localConfig'], (result) => {
    if (result.localConfig) {
      updatePaths(result.localConfig);
    }
  });
  
  // Listen for status updates
  chrome.runtime.onMessage.addListener((message) => {
    if (message.type === 'CONNECTION_STATUS') {
      updateStatus(message.connected);
    }
  });
  
  // Connect button
  connectBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'CONNECT' });
    connectText.textContent = 'Connecting...';
    connectBtn.disabled = true;
    
    setTimeout(() => {
      connectBtn.disabled = false;
      chrome.runtime.sendMessage({ type: 'GET_STATUS' }, (response) => {
        updateStatus(response?.connected || false);
      });
    }, 2000);
  });
  
  // Settings button - open AgentForge settings page
  settingsBtn.addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://file-examiner-10.preview.emergentagent.com/settings' });
  });
  
  function updateStatus(connected) {
    if (connected) {
      statusDot.className = 'status-dot connected';
      statusText.textContent = 'Connected';
      connectText.textContent = 'Reconnect';
    } else {
      statusDot.className = 'status-dot disconnected';
      statusText.textContent = 'Disconnected';
      connectText.textContent = 'Connect';
    }
  }
  
  function updatePaths(config) {
    if (config.unrealProjectPath) {
      unrealPath.textContent = config.unrealProjectPath;
      unrealPath.className = 'config-item-path';
    }
    if (config.unityProjectPath) {
      unityPath.textContent = config.unityProjectPath;
      unityPath.className = 'config-item-path';
    }
  }
});
