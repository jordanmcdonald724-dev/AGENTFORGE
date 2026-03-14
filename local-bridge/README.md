# AgentForge Local Bridge

Connect AgentForge to your local Unreal Engine and Unity projects. This bridge allows God Mode to push generated code directly into your local IDE and trigger builds.

## Components

1. **Browser Extension** - Runs in Chrome/Edge, bridges the web app to your local machine
2. **Native Messaging Host** - Python script that handles file operations and build commands

## Installation

### Step 1: Install the Native Messaging Host

1. **Download** the Local Bridge package from AgentForge Settings page
2. **Extract** to any folder (e.g., `C:\AgentForge-Bridge\`)
3. **Run** `install_windows.bat` as Administrator

The installer will:
- Copy the bridge script to `%USERPROFILE%\.agentforge\`
- Register the native messaging host with Chrome/Edge

### Step 2: Install the Browser Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top right)
3. Click **Load unpacked**
4. Select the `browser-extension` folder

### Step 3: Update Extension ID

1. Copy the Extension ID shown in `chrome://extensions/`
2. Run `update_extension_id.bat YOUR_EXTENSION_ID`
3. Restart Chrome

### Step 4: Configure Project Paths

1. Go to AgentForge Settings page (`/settings`)
2. Enter your Unreal Engine project path (folder containing `.uproject`)
3. Enter your Unity project path (folder containing `Assets`)
4. Save settings

## Usage

### Push Files to Local IDE

1. Complete a God Mode build
2. Click **"PUSH TO LOCAL"** button
3. Files will be saved to your configured project path

### Trigger Local Build

1. After pushing files, click **"LOCAL BUILD"**
2. The bridge will attempt to compile your project
3. Build progress appears in the log

## Project Structure Mapping

### Unreal Engine
- Files are saved to `Source/[ProjectName]/`
- Example: `Combat/DamageSystem.h` → `C:\MyGame\Source\MyGame\Combat\DamageSystem.h`

### Unity
- Files are saved to `Assets/Scripts/`
- Example: `PlayerController.cs` → `C:\MyUnityGame\Assets\Scripts\PlayerController.cs`

## Troubleshooting

### Bridge not connecting
1. Check if the native host is registered: Look in Windows Registry at `HKCU\SOFTWARE\Google\Chrome\NativeMessagingHosts`
2. Ensure Python 3.8+ is installed and in PATH
3. Check logs at `%USERPROFILE%\.agentforge\bridge.log`

### Build not starting
1. Verify engine paths in settings
2. For Unreal: Ensure you have the correct UE5 version installed
3. For Unity: Ensure Unity Hub is installed

### Files not appearing in IDE
1. Check the project path is correct
2. Ensure the path points to the project root (not a subfolder)
3. Refresh/reimport in Unreal/Unity

## Requirements

- Windows 10/11
- Python 3.8+
- Chrome or Edge browser
- Unreal Engine 5.x and/or Unity 2021+

## Security

- The extension only communicates with `emergentagent.com` and `localhost`
- All file operations are sandboxed to your configured project paths
- No data is sent to external servers

## Support

For issues, visit the AgentForge documentation or reach out through the app.
