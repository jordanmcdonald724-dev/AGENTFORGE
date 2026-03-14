#!/usr/bin/env python3
"""
AgentForge Local Bridge - Native Messaging Host
Simplified version for stability
"""

import sys
import json
import struct
import os
from pathlib import Path

# Set up logging to file
LOG_DIR = Path.home() / '.agentforge'
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / 'bridge.log'

def log(msg):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{msg}\n")

def read_message():
    """Read a message from stdin"""
    try:
        raw_length = sys.stdin.buffer.read(4)
        if not raw_length:
            return None
        message_length = struct.unpack('=I', raw_length)[0]
        message = sys.stdin.buffer.read(message_length)
        return json.loads(message.decode('utf-8'))
    except Exception as e:
        log(f"Read error: {e}")
        return None

def send_message(message):
    """Send a message to stdout"""
    try:
        encoded = json.dumps(message).encode('utf-8')
        sys.stdout.buffer.write(struct.pack('=I', len(encoded)))
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()
    except Exception as e:
        log(f"Send error: {e}")

def save_files(data):
    """Save files to local project"""
    files = data.get('files', [])
    project_path = data.get('projectPath', 'D:\\UE_5.7\\OceanCivilization')
    
    log(f"Saving {len(files)} files to {project_path}")
    
    saved = 0
    for f in files:
        try:
            filepath = f.get('filepath', f.get('filename', ''))
            content = f.get('content', '')
            
            if not filepath or not content:
                continue
            
            # Determine full path
            if filepath.startswith('Source/'):
                full_path = Path(project_path) / filepath
            else:
                project_name = Path(project_path).name
                full_path = Path(project_path) / 'Source' / project_name / filepath
            
            # Create dirs and write file
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as out:
                out.write(content)
            
            log(f"Saved: {full_path}")
            saved += 1
            
            send_message({
                'type': 'file_saved',
                'data': {'filepath': str(full_path)}
            })
            
        except Exception as e:
            log(f"Error saving {filepath}: {e}")
    
    send_message({
        'type': 'files_complete',
        'data': {'saved': saved, 'total': len(files)}
    })

def trigger_build(data):
    """Trigger build - just notify for now"""
    project_path = data.get('projectPath', 'D:\\UE_5.7\\OceanCivilization')
    
    # Find .uproject
    uproject = None
    for f in Path(project_path).glob('*.uproject'):
        uproject = f
        break
    
    # For UE 5.7, try to find the build tool
    # Check common locations for UE 5.7
    ue_locations = [
        Path('C:/Program Files/Epic Games/UE_5.7'),
        Path('D:/UE_5.7'),
        Path('D:/Epic Games/UE_5.7'),
        Path('C:/UE_5.7'),
    ]
    
    engine_path = None
    for loc in ue_locations:
        if loc.exists():
            engine_path = loc
            break
    
    if engine_path:
        log(f"Found UE 5.7 at: {engine_path}")
        send_message({
            'type': 'build_progress',
            'data': {'message': f'Found Unreal Engine 5.7 at {engine_path}'}
        })
    
    send_message({
        'type': 'build_complete',
        'data': {
            'success': True,
            'message': f'Files saved! Open {uproject or project_path} in Unreal Editor 5.7 and press Ctrl+Alt+F11 to compile.'
        }
    })

def main():
    log("Bridge started")
    
    # Send initial pong
    send_message({'type': 'pong', 'data': {'version': '1.0.0'}})
    
    while True:
        try:
            msg = read_message()
            if msg is None:
                log("No message, exiting")
                break
            
            log(f"Received: {msg.get('type')}")
            
            msg_type = msg.get('type')
            data = msg.get('data', {})
            
            if msg_type == 'ping':
                send_message({'type': 'pong'})
            
            elif msg_type == 'get_config':
                send_message({'type': 'config', 'data': {
                    'unrealProjectPath': 'D:\\UE_5.7\\OceanCivilization'
                }})
            
            elif msg_type == 'save_files':
                save_files(data)
            
            elif msg_type == 'trigger_build':
                trigger_build(data)
            
            else:
                send_message({'type': 'pong'})
                
        except Exception as e:
            log(f"Error: {e}")
            break
    
    log("Bridge exiting")

if __name__ == '__main__':
    main()
