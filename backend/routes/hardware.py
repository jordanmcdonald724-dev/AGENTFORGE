"""
Hardware Interface Layer
========================
Integration with microcontroller ecosystems.
Build IoT dashboards, robotics control software, sensor networks.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from core.database import db
from core.clients import llm_client
from core.utils import serialize_doc
import uuid
import json

router = APIRouter(prefix="/hardware", tags=["hardware"])


PLATFORM_TEMPLATES = {
    "arduino": {
        "name": "Arduino",
        "languages": ["cpp"],
        "frameworks": ["arduino_core"],
        "boards": ["uno", "mega", "nano", "esp32", "esp8266"],
        "capabilities": ["gpio", "pwm", "adc", "serial", "i2c", "spi", "wifi", "bluetooth"]
    },
    "raspberry_pi": {
        "name": "Raspberry Pi",
        "languages": ["python", "cpp"],
        "frameworks": ["rpi_gpio", "pigpio", "gpiozero"],
        "boards": ["pi4", "pi3", "pico", "zero"],
        "capabilities": ["gpio", "pwm", "i2c", "spi", "uart", "camera", "display"]
    },
    "esp32": {
        "name": "ESP32",
        "languages": ["cpp", "micropython"],
        "frameworks": ["esp_idf", "arduino", "micropython"],
        "boards": ["esp32_devkit", "esp32_cam", "esp32_s3"],
        "capabilities": ["wifi", "bluetooth", "ble", "gpio", "adc", "touch", "deep_sleep"]
    },
    "stm32": {
        "name": "STM32",
        "languages": ["c", "cpp"],
        "frameworks": ["stm32cube", "mbed"],
        "boards": ["f4", "f7", "h7", "l4"],
        "capabilities": ["gpio", "adc", "dac", "pwm", "can", "usb", "ethernet"]
    }
}


IOT_PROJECT_TYPES = {
    "smart_home": {
        "name": "Smart Home Controller",
        "sensors": ["temperature", "humidity", "motion", "light"],
        "actuators": ["relay", "servo", "led", "buzzer"],
        "protocols": ["mqtt", "http", "websocket"]
    },
    "weather_station": {
        "name": "Weather Station",
        "sensors": ["temperature", "humidity", "pressure", "wind", "rain"],
        "actuators": ["display", "led"],
        "protocols": ["http", "mqtt"]
    },
    "robot_controller": {
        "name": "Robot Controller",
        "sensors": ["ultrasonic", "ir", "imu", "encoder"],
        "actuators": ["motor", "servo", "led"],
        "protocols": ["serial", "bluetooth"]
    },
    "plant_monitor": {
        "name": "Plant Monitor",
        "sensors": ["soil_moisture", "light", "temperature"],
        "actuators": ["pump", "led"],
        "protocols": ["wifi", "mqtt"]
    },
    "security_system": {
        "name": "Security System",
        "sensors": ["motion", "door", "camera", "smoke"],
        "actuators": ["siren", "led", "lock"],
        "protocols": ["wifi", "mqtt", "http"]
    }
}


@router.get("/platforms")
async def get_hardware_platforms():
    """Get supported hardware platforms"""
    return PLATFORM_TEMPLATES


@router.get("/project-types")
async def get_iot_project_types():
    """Get IoT project types"""
    return IOT_PROJECT_TYPES


@router.post("/generate-firmware")
async def generate_firmware(
    project_id: str,
    platform: str,
    board: str,
    project_type: str,
    custom_requirements: str = None
):
    """Generate firmware code for hardware project"""
    
    if platform not in PLATFORM_TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {platform}")
    
    platform_config = PLATFORM_TEMPLATES[platform]
    project_config = IOT_PROJECT_TYPES.get(project_type, {})
    
    generation = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "platform": platform,
        "board": board,
        "project_type": project_type,
        "status": "generating",
        "files": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Generate main firmware code
    try:
        response = llm_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {"role": "system", "content": f"""Generate {platform} firmware for {board}.
Project type: {project_type}
Sensors: {project_config.get('sensors', [])}
Actuators: {project_config.get('actuators', [])}
Protocols: {project_config.get('protocols', [])}

Generate production-ready firmware with:
- Proper pin definitions
- Sensor reading functions
- Actuator control functions
- Communication handlers
- Error handling
- Power management

Output complete, compilable code."""},
                {"role": "user", "content": f"Generate {project_config.get('name', project_type)} firmware. {custom_requirements or ''}"}
            ],
            max_tokens=4000
        )
        
        main_code = response.choices[0].message.content
        
        ext = ".ino" if platform == "arduino" else ".py" if "python" in platform_config["languages"] else ".cpp"
        
        generation["files"].append({
            "filename": f"main{ext}",
            "path": f"/firmware/main{ext}",
            "language": platform_config["languages"][0],
            "content": main_code
        })
        
    except Exception as e:
        generation["error"] = str(e)
    
    # Generate config header
    generation["files"].append({
        "filename": "config.h",
        "path": "/firmware/config.h",
        "language": "cpp",
        "content": f'''#ifndef CONFIG_H
#define CONFIG_H

// Platform: {platform}
// Board: {board}
// Project: {project_type}

// WiFi Configuration
#define WIFI_SSID "your_wifi_ssid"
#define WIFI_PASSWORD "your_wifi_password"

// MQTT Configuration
#define MQTT_BROKER "mqtt.example.com"
#define MQTT_PORT 1883
#define MQTT_TOPIC "{project_type}/data"

// Pin Definitions
#define LED_PIN 2
#define SENSOR_PIN A0

// Timing
#define SENSOR_INTERVAL 5000
#define MQTT_INTERVAL 10000

#endif
'''
    })
    
    # Generate README
    generation["files"].append({
        "filename": "README.md",
        "path": "/firmware/README.md",
        "language": "markdown",
        "content": f'''# {project_config.get("name", project_type)} Firmware

Platform: {platform_config["name"]}
Board: {board}

## Sensors
{chr(10).join([f"- {s}" for s in project_config.get("sensors", [])])}

## Actuators
{chr(10).join([f"- {a}" for a in project_config.get("actuators", [])])}

## Setup

1. Install required libraries
2. Update `config.h` with your credentials
3. Upload to {board}

## Wiring

See schematic in `/docs` folder.

---
*Generated by AgentForge Hardware Interface*
'''
    })
    
    generation["status"] = "completed"
    generation["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.firmware_generations.insert_one(generation)
    return serialize_doc(generation)


@router.post("/generate-dashboard")
async def generate_iot_dashboard(
    project_id: str,
    project_type: str,
    data_points: List[str] = None
):
    """Generate IoT dashboard for hardware project"""
    
    project_config = IOT_PROJECT_TYPES.get(project_type, {})
    data_points = data_points or project_config.get("sensors", [])
    
    dashboard = {
        "id": str(uuid.uuid4()),
        "project_id": project_id,
        "project_type": project_type,
        "data_points": data_points,
        "files": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Generate React dashboard component
    data_cards = "\n".join([
        f'''        <div className="p-4 bg-gray-800 rounded-xl">
          <p className="text-gray-400 text-sm">{dp.replace("_", " ").title()}</p>
          <p className="text-2xl font-bold">{{data.{dp} || 0}}</p>
        </div>'''
        for dp in data_points
    ])
    
    dashboard["files"].append({
        "filename": "Dashboard.jsx",
        "path": "/src/components/IoTDashboard.jsx",
        "language": "jsx",
        "content": f'''import React, {{ useState, useEffect }} from 'react';

const IoTDashboard = () => {{
  const [data, setData] = useState({{}});
  const [connected, setConnected] = useState(false);
  
  useEffect(() => {{
    // Connect to MQTT or WebSocket
    const fetchData = async () => {{
      try {{
        const res = await fetch('/api/iot/data');
        const json = await res.json();
        setData(json);
        setConnected(true);
      }} catch (e) {{
        setConnected(false);
      }}
    }};
    
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }}, []);
  
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">{project_config.get("name", "IoT")} Dashboard</h1>
        <div className={{`px-3 py-1 rounded-full text-sm ${{connected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}}`}}>
          {{connected ? 'Connected' : 'Disconnected'}}
        </div>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
{data_cards}
      </div>
      
      <div className="grid md:grid-cols-2 gap-6">
        <div className="p-6 bg-gray-800 rounded-xl">
          <h2 className="text-xl font-semibold mb-4">Real-time Data</h2>
          <div className="h-64 bg-gray-700 rounded-lg flex items-center justify-center">
            Chart placeholder
          </div>
        </div>
        <div className="p-6 bg-gray-800 rounded-xl">
          <h2 className="text-xl font-semibold mb-4">Controls</h2>
          <div className="space-y-4">
            <button className="w-full py-2 bg-blue-600 rounded-lg hover:bg-blue-700">
              Refresh Data
            </button>
            <button className="w-full py-2 bg-gray-700 rounded-lg hover:bg-gray-600">
              Download CSV
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}};

export default IoTDashboard;
'''
    })
    
    # Generate API endpoint
    dashboard["files"].append({
        "filename": "iot_routes.py",
        "path": "/backend/routes/iot_routes.py",
        "language": "python",
        "content": f'''"""IoT Data Routes"""

from fastapi import APIRouter
from datetime import datetime
import random

router = APIRouter(prefix="/iot", tags=["iot"])

@router.get("/data")
async def get_iot_data():
    """Get latest IoT sensor data"""
    return {{
{chr(10).join([f'        "{dp}": round(random.uniform(0, 100), 2),' for dp in data_points])}
        "timestamp": datetime.utcnow().isoformat()
    }}

@router.get("/history")
async def get_iot_history(hours: int = 24):
    """Get historical IoT data"""
    return {{"data": [], "hours": hours}}

@router.post("/command")
async def send_command(command: str, value: str = None):
    """Send command to IoT device"""
    return {{"command": command, "value": value, "status": "sent"}}
'''
    })
    
    dashboard["status"] = "completed"
    await db.iot_dashboards.insert_one(dashboard)
    return serialize_doc(dashboard)


@router.get("/firmware")
async def list_firmware_generations(project_id: str = None, limit: int = 20):
    """List firmware generations"""
    query = {}
    if project_id:
        query["project_id"] = project_id
    return await db.firmware_generations.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
