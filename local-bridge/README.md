# AgentForge Local Bridge

Connect AgentForge to your local Unreal Engine and Unity projects. Push generated code directly to your IDE and launch builds from the web app.

## Quick Start (One-Click Install)

### Step 1: Download & Extract
1. Download the Local Bridge ZIP from AgentForge Settings (`/settings`)
2. Extract to any folder (e.g., `C:\AgentForge-Bridge\`)

### Step 2: Install Browser Extension
1. Open Chrome/Edge and go to `chrome://extensions` or `edge://extensions`
2. Enable **Developer mode** (toggle in top right)
3. Click **Load unpacked**
4. Select the `browser-extension` folder from the download

### Step 3: Run One-Click Installer
1. Double-click **`OneClickInstaller.bat`**
2. The installer will automatically:
   - Check Python is installed
   - Copy bridge files to `%USERPROFILE%\.agentforge\`
   - Register with Chrome, Edge, and Chromium
   - Configure everything

### Step 4: Restart Browser
Close ALL browser windows and reopen. The bridge should connect automatically!

---

## Configuration

### Project Paths
1. Go to AgentForge Settings page (`/settings`)
2. Enter your Unreal Engine project path (folder containing `.uproject`)
3. Enter your Unity project path (folder containing `Assets`)
4. Save settings

### If Extension ID Changed
If you reinstalled the extension and got a new ID:
1. Run **`UpdateExtensionID.bat`**
2. Enter your new Extension ID when prompted
3. Restart browser

---

## Usage

### Push Files to Local IDE
1. Complete a God Mode build in AgentForge
2. Click **"PUSH TO LOCAL"** button
3. Files will be saved to your configured project path

### Launch Unreal Engine
1. After pushing files, click **"LOCAL BUILD"**
2. The bridge will launch Unreal Editor with your project

---

## Troubleshooting

### Bridge Not Connecting

1. **Check extension is enabled** - Go to `chrome://extensions` and ensure the AgentForge extension is ON
2. **Check native host registration** - Run `regedit` and look for:
   - `HKCU\SOFTWARE\Google\Chrome\NativeMessagingHosts\com.agentforge.localbridge`
   - `HKCU\SOFTWARE\Microsoft\Edge\NativeMessagingHosts\com.agentforge.localbridge`
3. **Check logs** - View `%USERPROFILE%\.agentforge\bridge.log`
4. **Re-run installer** - Run `OneClickInstaller.bat` again

### Wrong Extension ID

1. Copy your Extension ID from `chrome://extensions`
2. Run `UpdateExtensionID.bat YOUR_ID_HERE`
3. Restart browser

### Python Not Found

1. Install Python 3.8+ from https://www.python.org/downloads/
2. **Important**: Check "Add Python to PATH" during installation
3. Run the installer again

---

## Files Included

| File | Purpose |
|------|---------|
| `OneClickInstaller.bat` | Main installer - run this first |
| `UpdateExtensionID.bat` | Update extension ID if it changed |
| `Uninstall.bat` | Remove the local bridge |
| `agentforge_bridge.py` | Python script that handles file operations |
| `agentforge_bridge.bat` | Launcher for the Python script |

---

## Requirements

- Windows 10/11
- Python 3.8+ (with PATH configured)
- Chrome, Edge, or Chromium browser
- Unreal Engine 5.x and/or Unity 2021+

---

## Support

For issues, check the AgentForge Settings page or view the logs at:
`%USERPROFILE%\.agentforge\bridge.log`
