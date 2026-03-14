// AgentForge Local Bridge - Background Service Worker
const NATIVE_HOST_NAME = 'com.agentforge.localbridge';

// Connection state
let nativePort = null;
let isConnected = false;
let connectionRetries = 0;
const MAX_RETRIES = 3;

// Connect to native messaging host
function connectToNativeHost() {
  try {
    nativePort = chrome.runtime.connectNative(NATIVE_HOST_NAME);
    
    nativePort.onMessage.addListener((message) => {
      console.log('[AgentForge] Native host message:', message);
      handleNativeMessage(message);
    });
    
    nativePort.onDisconnect.addListener(() => {
      console.log('[AgentForge] Native host disconnected:', chrome.runtime.lastError?.message);
      isConnected = false;
      nativePort = null;
      
      // Notify popup and content scripts
      broadcastConnectionStatus(false);
    });
    
    isConnected = true;
    connectionRetries = 0;
    broadcastConnectionStatus(true);
    
    // Send initial ping
    sendToNativeHost({ type: 'ping' });
    
  } catch (error) {
    console.error('[AgentForge] Failed to connect to native host:', error);
    isConnected = false;
    
    if (connectionRetries < MAX_RETRIES) {
      connectionRetries++;
      setTimeout(connectToNativeHost, 2000 * connectionRetries);
    }
  }
}

// Send message to native host
function sendToNativeHost(message) {
  if (nativePort && isConnected) {
    try {
      nativePort.postMessage(message);
      return true;
    } catch (error) {
      console.error('[AgentForge] Error sending to native host:', error);
      isConnected = false;
      return false;
    }
  }
  return false;
}

// Handle messages from native host
function handleNativeMessage(message) {
  switch (message.type) {
    case 'pong':
      console.log('[AgentForge] Native host alive');
      break;
      
    case 'file_saved':
      // Notify content script of successful file save
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
          chrome.tabs.sendMessage(tabs[0].id, {
            type: 'FILE_SAVED',
            data: message.data
          });
        }
      });
      break;
      
    case 'build_started':
      notifyBuildStatus('started', message.data);
      break;
      
    case 'build_progress':
      notifyBuildStatus('progress', message.data);
      break;
      
    case 'build_complete':
      notifyBuildStatus('complete', message.data);
      break;
      
    case 'build_error':
      notifyBuildStatus('error', message.data);
      break;
      
    case 'config':
      // Store config received from native host
      chrome.storage.local.set({ localConfig: message.data });
      break;
      
    case 'error':
      console.error('[AgentForge] Native host error:', message.error);
      break;
  }
}

// Broadcast connection status to all listeners
function broadcastConnectionStatus(connected) {
  // To popup
  chrome.runtime.sendMessage({ 
    type: 'CONNECTION_STATUS', 
    connected 
  }).catch(() => {});
  
  // To content scripts
  chrome.tabs.query({}, (tabs) => {
    tabs.forEach(tab => {
      chrome.tabs.sendMessage(tab.id, { 
        type: 'CONNECTION_STATUS', 
        connected 
      }).catch(() => {});
    });
  });
}

// Notify about build status
function notifyBuildStatus(status, data) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]) {
      chrome.tabs.sendMessage(tabs[0].id, {
        type: 'BUILD_STATUS',
        status,
        data
      });
    }
  });
}

// Listen for messages from content scripts and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('[AgentForge] Received message:', message.type);
  
  switch (message.type) {
    case 'GET_STATUS':
      sendResponse({ connected: isConnected });
      break;
      
    case 'CONNECT':
      if (!isConnected) {
        connectToNativeHost();
      }
      sendResponse({ success: true });
      break;
      
    case 'PUSH_FILES':
      // Send files to native host for saving
      if (isConnected) {
        const success = sendToNativeHost({
          type: 'save_files',
          data: message.data
        });
        sendResponse({ success });
      } else {
        sendResponse({ success: false, error: 'Not connected to local bridge' });
      }
      break;
      
    case 'TRIGGER_BUILD':
      // Trigger build in Unreal/Unity
      if (isConnected) {
        const success = sendToNativeHost({
          type: 'trigger_build',
          data: message.data
        });
        sendResponse({ success });
      } else {
        sendResponse({ success: false, error: 'Not connected to local bridge' });
      }
      break;
      
    case 'SET_CONFIG':
      // Update local bridge configuration
      if (isConnected) {
        const success = sendToNativeHost({
          type: 'set_config',
          data: message.data
        });
        sendResponse({ success });
      } else {
        sendResponse({ success: false, error: 'Not connected to local bridge' });
      }
      break;
      
    case 'GET_CONFIG':
      // Request config from native host
      if (isConnected) {
        sendToNativeHost({ type: 'get_config' });
        sendResponse({ success: true });
      } else {
        sendResponse({ success: false, error: 'Not connected' });
      }
      break;
      
    default:
      sendResponse({ error: 'Unknown message type' });
  }
  
  return true; // Keep channel open for async response
});

// Try to connect on startup
connectToNativeHost();

// Periodic health check
setInterval(() => {
  if (isConnected) {
    sendToNativeHost({ type: 'ping' });
  }
}, 30000);
