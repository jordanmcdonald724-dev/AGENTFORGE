// AgentForge Local Bridge - Background Service Worker
const NATIVE_HOST_NAME = 'com.agentforge.localbridge';

// Connection state
let nativePort = null;
let isConnected = false;
let connectionRetries = 0;
let lastReconnectAttempt = 0;
const MAX_RETRIES = 3;
const RECONNECT_COOLDOWN = 10000; // minimum 10s between reconnect attempts
const RECONNECT_DELAY = 5000;     // fixed 5s delay (no exponential — avoids rapid loops)

// Connect to native messaging host
function connectToNativeHost() {
  const now = Date.now();
  if (now - lastReconnectAttempt < RECONNECT_COOLDOWN && connectionRetries > 0) {
    return; // too soon — skip this attempt
  }
  lastReconnectAttempt = now;

  try {
    nativePort = chrome.runtime.connectNative(NATIVE_HOST_NAME);

    nativePort.onMessage.addListener((message) => {
      handleNativeMessage(message);
    });

    nativePort.onDisconnect.addListener(() => {
      const wasConnected = isConnected;
      isConnected = false;
      nativePort = null;

      if (wasConnected) {
        // Only broadcast if we were actually connected — avoids startup noise
        broadcastConnectionStatus(false);
      }

      // Retry with cooldown — don't loop aggressively
      if (connectionRetries < MAX_RETRIES) {
        connectionRetries++;
        setTimeout(connectToNativeHost, RECONNECT_DELAY);
      }
    });

    isConnected = true;
    connectionRetries = 0;
    broadcastConnectionStatus(true);

    // Send initial ping
    sendToNativeHost({ type: 'ping' });

  } catch (error) {
    console.error('[AgentForge] Failed to connect to native host:', error);
    isConnected = false;
    // Don't retry on initial connection failure — let the user click Connect
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
      break;

    case 'file_saved':
      broadcastToActiveTab({ type: 'FILE_SAVED', data: message.data });
      break;

    case 'build_started':
    case 'build_progress':
    case 'build_complete':
    case 'build_error':
      broadcastToActiveTab({
        type: 'BUILD_STATUS',
        status: message.type.replace('build_', ''),
        data: message.data
      });
      break;

    case 'config':
      chrome.storage.local.set({ localConfig: message.data });
      break;

    case 'error':
      console.error('[AgentForge] Native host error:', message.error);
      break;
  }
}

// Broadcast to the ACTIVE tab only — not every tab (that caused the spam)
function broadcastToActiveTab(message) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]) {
      chrome.tabs.sendMessage(tabs[0].id, message).catch(() => {});
    }
  });
}

// Broadcast connection status
// Sends to popup + active tab only (not ALL tabs)
function broadcastConnectionStatus(connected) {
  chrome.runtime.sendMessage({ type: 'CONNECTION_STATUS', connected }).catch(() => {});
  broadcastToActiveTab({ type: 'CONNECTION_STATUS', connected });
}

// Notify about build status
function notifyBuildStatus(status, data) {
  broadcastToActiveTab({ type: 'BUILD_STATUS', status, data });
}

// Listen for messages from content scripts and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.type) {
    case 'GET_STATUS':
      sendResponse({ connected: isConnected });
      break;

    case 'CONNECT':
      if (!isConnected) {
        connectionRetries = 0; // reset retries on manual connect
        connectToNativeHost();
      }
      sendResponse({ success: true });
      break;

    case 'PUSH_FILES':
      if (isConnected) {
        const ok = sendToNativeHost({ type: 'save_files', data: message.data });
        sendResponse({ success: ok });
      } else {
        sendResponse({ success: false, error: 'Not connected to local bridge' });
      }
      break;

    case 'TRIGGER_BUILD':
      if (isConnected) {
        const ok = sendToNativeHost({ type: 'trigger_build', data: message.data });
        sendResponse({ success: ok });
      } else {
        sendResponse({ success: false, error: 'Not connected to local bridge' });
      }
      break;

    case 'SET_CONFIG':
      if (isConnected) {
        const ok = sendToNativeHost({ type: 'set_config', data: message.data });
        sendResponse({ success: ok });
      } else {
        sendResponse({ success: false, error: 'Not connected' });
      }
      break;

    case 'GET_CONFIG':
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

  return true; // keep channel open for async response
});

// Try to connect on startup — but don't auto-retry if native host not installed
connectToNativeHost();

// Periodic health check — only ping if already connected
setInterval(() => {
  if (isConnected) {
    sendToNativeHost({ type: 'ping' });
  }
}, 30000);
