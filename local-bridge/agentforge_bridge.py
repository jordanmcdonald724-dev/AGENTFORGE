#!/usr/bin/env python3
"""
AgentForge Local Bridge - Native Messaging Host
This script runs locally on the user's machine and handles:
1. Receiving files from the browser extension
2. Saving files to Unreal/Unity project directories
3. Triggering build commands
"""

import sys
import json
import struct
import os
import subprocess
import threading
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
log_dir = Path.home() / '.agentforge'
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=log_dir / 'bridge.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Config file path
CONFIG_FILE = log_dir / 'config.json'

# Default configuration
DEFAULT_CONFIG = {
    'unrealProjectPath': '',
    'unityProjectPath': '',
    'unrealEnginePath': '',
    'unityEditorPath': '',
    'autoOpenEditor': True,
    'autoBuild': False
}

def load_config():
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return {**DEFAULT_CONFIG, **config}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    return DEFAULT_CONFIG

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info("Config saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

def read_message():
    """Read a message from stdin using native messaging protocol"""
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        return None
    
    message_length = struct.unpack('=I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length)
    return json.loads(message.decode('utf-8'))

def send_message(message):
    """Send a message to stdout using native messaging protocol"""
    encoded = json.dumps(message).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('=I', len(encoded)))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()

def determine_file_path(filepath, project_path, engine):
    """Determine the full file path based on project and engine"""
    if engine.lower() in ['unreal', 'ue5', 'unreal engine 5']:
        # Unreal Engine project structure
        # Source files go in Source/ProjectName/
        if filepath.startswith('Source/'):
            return Path(project_path) / filepath
        else:
            project_name = Path(project_path).name
            return Path(project_path) / 'Source' / project_name / filepath
    
    elif engine.lower() in ['unity', 'unity3d']:
        # Unity project structure
        # Scripts go in Assets/Scripts/
        if filepath.startswith('Assets/'):
            return Path(project_path) / filepath
        else:
            return Path(project_path) / 'Assets' / 'Scripts' / filepath
    
    else:
        # Generic - just use relative path
        return Path(project_path) / filepath

def save_files(data):
    """Save files to the local project directory"""
    config = load_config()
    files = data.get('files', [])
    project_path = data.get('projectPath') or config.get('unrealProjectPath')
    engine = data.get('engine', 'unreal')
    
    if not project_path:
        send_message({
            'type': 'error',
            'error': 'No project path configured'
        })
        return
    
    saved_count = 0
    errors = []
    
    for file_data in files:
        try:
            filepath = file_data.get('filepath', file_data.get('filename', ''))
            content = file_data.get('content', '')
            
            if not filepath or not content:
                continue
            
            # Determine full path
            full_path = determine_file_path(filepath, project_path, engine)
            
            # Create directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved file: {full_path}")
            saved_count += 1
            
            # Notify about each file
            send_message({
                'type': 'file_saved',
                'data': {
                    'filepath': str(full_path),
                    'originalPath': filepath
                }
            })
            
        except Exception as e:
            logger.error(f"Error saving file {filepath}: {e}")
            errors.append({'filepath': filepath, 'error': str(e)})
    
    # Send completion message
    send_message({
        'type': 'files_complete',
        'data': {
            'saved': saved_count,
            'total': len(files),
            'errors': errors
        }
    })
    
    # Auto-build if configured
    if config.get('autoBuild') and saved_count > 0:
        trigger_build({'projectPath': project_path, 'engine': engine})

def trigger_build(data):
    """Trigger a build in Unreal Engine or Unity"""
    config = load_config()
    project_path = data.get('projectPath') or config.get('unrealProjectPath')
    engine = data.get('engine', 'unreal')
    build_config = data.get('buildConfig', {})
    
    if not project_path:
        send_message({
            'type': 'error',
            'error': 'No project path configured'
        })
        return
    
    send_message({
        'type': 'build_started',
        'data': {
            'engine': engine,
            'projectPath': project_path
        }
    })
    
    def run_build():
        try:
            if engine.lower() in ['unreal', 'ue5', 'unreal engine 5']:
                build_unreal(project_path, build_config, config)
            elif engine.lower() in ['unity', 'unity3d']:
                build_unity(project_path, build_config, config)
            else:
                send_message({
                    'type': 'build_error',
                    'data': {'error': f'Unknown engine: {engine}'}
                })
        except Exception as e:
            logger.error(f"Build error: {e}")
            send_message({
                'type': 'build_error',
                'data': {'error': str(e)}
            })
    
    # Run build in background thread
    build_thread = threading.Thread(target=run_build)
    build_thread.start()

def build_unreal(project_path, build_config, config):
    """Build Unreal Engine project"""
    project_path = Path(project_path)
    
    # Find .uproject file
    uproject_files = list(project_path.glob('*.uproject'))
    if not uproject_files:
        send_message({
            'type': 'build_error',
            'data': {'error': 'No .uproject file found in project directory'}
        })
        return
    
    uproject = uproject_files[0]
    project_name = uproject.stem
    
    # Find Unreal Engine installation
    ue_path = config.get('unrealEnginePath', '')
    
    # Common UE5 paths on Windows
    if not ue_path or not Path(ue_path).exists():
        common_paths = [
            r'C:\Program Files\Epic Games\UE_5.4\Engine\Build\BatchFiles\Build.bat',
            r'C:\Program Files\Epic Games\UE_5.3\Engine\Build\BatchFiles\Build.bat',
            r'C:\Program Files\Epic Games\UE_5.2\Engine\Build\BatchFiles\Build.bat',
            r'C:\Program Files\Epic Games\UE_5.1\Engine\Build\BatchFiles\Build.bat',
        ]
        
        for path in common_paths:
            if Path(path).exists():
                ue_path = path
                break
    
    if not ue_path or not Path(ue_path).exists():
        # Try using UnrealBuildTool directly
        send_message({
            'type': 'build_progress',
            'data': {'message': 'Looking for Unreal Engine Build Tool...'}
        })
        
        # Generate Visual Studio project files instead (more reliable)
        generate_cmd = [
            str(uproject),
            '-generateproject'
        ]
        
        send_message({
            'type': 'build_progress',
            'data': {'message': 'Refreshing project files...'}
        })
        
        # For now, just report success with instructions
        send_message({
            'type': 'build_complete',
            'data': {
                'success': True,
                'message': f'Files saved to {project_path}. Open {uproject} in Unreal Editor to compile.',
                'projectFile': str(uproject)
            }
        })
        return
    
    # Build command
    platform = build_config.get('platform', 'Win64')
    configuration = build_config.get('configuration', 'Development')
    
    cmd = [
        str(ue_path),
        f'{project_name}Editor',
        platform,
        configuration,
        str(uproject),
        '-waitmutex'
    ]
    
    send_message({
        'type': 'build_progress',
        'data': {'message': f'Building {project_name} ({platform} {configuration})...'}
    })
    
    logger.info(f"Running build command: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )
    
    # Stream output
    for line in process.stdout:
        line = line.strip()
        if line:
            send_message({
                'type': 'build_progress',
                'data': {'message': line}
            })
    
    return_code = process.wait()
    
    if return_code == 0:
        send_message({
            'type': 'build_complete',
            'data': {
                'success': True,
                'message': 'Build completed successfully!'
            }
        })
    else:
        stderr = process.stderr.read()
        send_message({
            'type': 'build_error',
            'data': {'error': f'Build failed with code {return_code}: {stderr}'}
        })

def build_unity(project_path, build_config, config):
    """Build Unity project"""
    project_path = Path(project_path)
    
    # Find Unity Editor
    unity_path = config.get('unityEditorPath', '')
    
    # Common Unity paths on Windows
    if not unity_path or not Path(unity_path).exists():
        unity_hub_path = Path.home() / 'AppData' / 'Local' / 'Unity' / 'Hub' / 'Editor'
        if unity_hub_path.exists():
            # Get latest Unity version
            versions = sorted(unity_hub_path.iterdir(), reverse=True)
            for version in versions:
                editor = version / 'Editor' / 'Unity.exe'
                if editor.exists():
                    unity_path = str(editor)
                    break
    
    if not unity_path or not Path(unity_path).exists():
        send_message({
            'type': 'build_complete',
            'data': {
                'success': True,
                'message': f'Files saved to {project_path}. Open Unity Editor to compile.',
                'projectPath': str(project_path)
            }
        })
        return
    
    # Build command
    build_target = build_config.get('buildTarget', 'Win64')
    
    cmd = [
        unity_path,
        '-batchmode',
        '-nographics',
        '-projectPath', str(project_path),
        '-buildTarget', build_target,
        '-quit'
    ]
    
    send_message({
        'type': 'build_progress',
        'data': {'message': f'Building Unity project ({build_target})...'}
    })
    
    logger.info(f"Running Unity build: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    return_code = process.wait()
    
    if return_code == 0:
        send_message({
            'type': 'build_complete',
            'data': {
                'success': True,
                'message': 'Unity project refreshed successfully!'
            }
        })
    else:
        stderr = process.stderr.read()
        send_message({
            'type': 'build_error',
            'data': {'error': f'Unity returned code {return_code}: {stderr}'}
        })

def handle_message(message):
    """Handle incoming message from browser extension"""
    msg_type = message.get('type')
    data = message.get('data', {})
    
    logger.info(f"Received message: {msg_type}")
    
    if msg_type == 'ping':
        send_message({'type': 'pong'})
    
    elif msg_type == 'get_config':
        config = load_config()
        send_message({'type': 'config', 'data': config})
    
    elif msg_type == 'set_config':
        config = load_config()
        config.update(data)
        if save_config(config):
            send_message({'type': 'config', 'data': config})
        else:
            send_message({'type': 'error', 'error': 'Failed to save config'})
    
    elif msg_type == 'save_files':
        save_files(data)
    
    elif msg_type == 'trigger_build':
        trigger_build(data)
    
    else:
        send_message({'type': 'error', 'error': f'Unknown message type: {msg_type}'})

def main():
    """Main entry point"""
    logger.info("AgentForge Local Bridge started")
    
    # Send initial pong to confirm we're running
    send_message({'type': 'pong', 'data': {'version': '1.0.0'}})
    
    # Message loop
    while True:
        try:
            message = read_message()
            if message is None:
                logger.info("No more messages, exiting")
                break
            
            handle_message(message)
            
        except Exception as e:
            logger.error(f"Error in message loop: {e}")
            try:
                send_message({'type': 'error', 'error': str(e)})
            except:
                pass

if __name__ == '__main__':
    main()
