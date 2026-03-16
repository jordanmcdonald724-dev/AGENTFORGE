"""
Hardware Integration - Arduino, Raspberry Pi, STM32, Teensy code generation
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
from engine.core.database import db
import uuid

router = APIRouter(prefix="/hardware", tags=["hardware"])

PLATFORMS = {
    "arduino_uno": {"name": "Arduino Uno", "mcu": "ATmega328P", "language": "C++", "framework": "Arduino"},
    "arduino_mega": {"name": "Arduino Mega", "mcu": "ATmega2560", "language": "C++", "framework": "Arduino"},
    "arduino_nano": {"name": "Arduino Nano", "mcu": "ATmega328P", "language": "C++", "framework": "Arduino"},
    "esp32": {"name": "ESP32", "mcu": "ESP32", "language": "C++", "framework": "Arduino/ESP-IDF"},
    "esp8266": {"name": "ESP8266", "mcu": "ESP8266", "language": "C++", "framework": "Arduino"},
    "raspberry_pi_4": {"name": "Raspberry Pi 4", "mcu": "BCM2711", "language": "Python", "framework": "RPi.GPIO"},
    "raspberry_pi_pico": {"name": "Raspberry Pi Pico", "mcu": "RP2040", "language": "Python/C++", "framework": "MicroPython"},
    "raspberry_pi_pico_w": {"name": "Raspberry Pi Pico W", "mcu": "RP2040", "language": "Python/C++", "framework": "MicroPython"},
    "stm32_bluepill": {"name": "STM32 Blue Pill", "mcu": "STM32F103C8T6", "language": "C", "framework": "STM32 HAL"},
    "stm32_blackpill": {"name": "STM32 Black Pill", "mcu": "STM32F411CEU6", "language": "C", "framework": "STM32 HAL"},
    "teensy_40": {"name": "Teensy 4.0", "mcu": "IMXRT1062", "language": "C++", "framework": "Teensyduino"},
    "teensy_41": {"name": "Teensy 4.1", "mcu": "IMXRT1062", "language": "C++", "framework": "Teensyduino"}
}

SENSORS = {
    "dht11": {"name": "DHT11 Temperature/Humidity", "type": "environmental"},
    "dht22": {"name": "DHT22 Temperature/Humidity", "type": "environmental"},
    "bmp280": {"name": "BMP280 Pressure/Temp", "type": "environmental"},
    "mpu6050": {"name": "MPU6050 Accelerometer/Gyro", "type": "motion"},
    "hcsr04": {"name": "HC-SR04 Ultrasonic", "type": "distance"},
    "pir": {"name": "PIR Motion Sensor", "type": "motion"},
    "ldr": {"name": "LDR Light Sensor", "type": "light"},
    "soil_moisture": {"name": "Soil Moisture Sensor", "type": "environmental"},
    "mq2": {"name": "MQ-2 Gas Sensor", "type": "environmental"},
    "bme680": {"name": "BME680 Air Quality", "type": "environmental"}
}

class HardwareProjectCreate(BaseModel):
    name: str
    description: str
    platform: str
    sensors: List[str] = []
    features: List[str] = []

class CodeGenerateRequest(BaseModel):
    project_id: str
    include_comments: bool = True

@router.get("/platforms")
async def get_platforms():
    """Get supported hardware platforms"""
    return PLATFORMS

@router.get("/sensors")
async def get_sensors():
    """Get supported sensors"""
    return SENSORS

@router.post("/projects")
async def create_project(project: HardwareProjectCreate):
    """Create hardware project"""
    project_id = str(uuid.uuid4())
    
    platform_info = PLATFORMS.get(project.platform)
    if not platform_info:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    hw_project = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "platform": project.platform,
        "platform_info": platform_info,
        "sensors": project.sensors,
        "features": project.features,
        "status": "created",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "code": None
    }
    
    await db.hardware_projects.insert_one(hw_project)
    return {"project_id": project_id, "platform": platform_info["name"]}

@router.get("/projects")
async def list_projects():
    """List hardware projects"""
    projects = await db.hardware_projects.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return projects

@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    project = await db.hardware_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/generate")
async def generate_code(request: CodeGenerateRequest):
    """Generate code for hardware project"""
    project = await db.hardware_projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    platform = project["platform"]
    sensors = project["sensors"]
    
    if platform.startswith("arduino") or platform.startswith("esp"):
        code = generate_arduino_code(project["name"], platform, sensors, request.include_comments)
    elif platform.startswith("raspberry"):
        code = generate_python_code(project["name"], platform, sensors, request.include_comments)
    elif platform.startswith("stm32"):
        code = generate_stm32_code(project["name"], platform, sensors, request.include_comments)
    elif platform.startswith("teensy"):
        code = generate_teensy_code(project["name"], platform, sensors, request.include_comments)
    else:
        code = "// Platform not supported yet"
    
    await db.hardware_projects.update_one(
        {"id": request.project_id},
        {"$set": {"code": code, "status": "generated"}}
    )
    
    return {"project_id": request.project_id, "code": code}

def generate_arduino_code(name: str, platform: str, sensors: List[str], comments: bool) -> str:
    """Generate Arduino/ESP code"""
    code = f"// {name} - Generated by AgentForge\n"
    code += f"// Platform: {PLATFORMS[platform]['name']}\n\n"
    
    # Includes
    if "dht11" in sensors or "dht22" in sensors:
        code += '#include <DHT.h>\n'
    if "bmp280" in sensors:
        code += '#include <Adafruit_BMP280.h>\n'
    if "mpu6050" in sensors:
        code += '#include <Wire.h>\n#include <MPU6050.h>\n'
    
    code += "\n"
    
    # Pin definitions
    if "dht11" in sensors:
        code += "#define DHT_PIN 2\n#define DHT_TYPE DHT11\nDHT dht(DHT_PIN, DHT_TYPE);\n"
    if "dht22" in sensors:
        code += "#define DHT_PIN 2\n#define DHT_TYPE DHT22\nDHT dht(DHT_PIN, DHT_TYPE);\n"
    if "hcsr04" in sensors:
        code += "#define TRIG_PIN 9\n#define ECHO_PIN 10\n"
    
    code += "\nvoid setup() {\n"
    code += "  Serial.begin(115200);\n"
    if "dht11" in sensors or "dht22" in sensors:
        code += "  dht.begin();\n"
    if "hcsr04" in sensors:
        code += "  pinMode(TRIG_PIN, OUTPUT);\n  pinMode(ECHO_PIN, INPUT);\n"
    code += "}\n\n"
    
    code += "void loop() {\n"
    if "dht11" in sensors or "dht22" in sensors:
        code += "  float temp = dht.readTemperature();\n"
        code += "  float humidity = dht.readHumidity();\n"
        code += '  Serial.print("Temp: "); Serial.print(temp); Serial.print(" Humidity: "); Serial.println(humidity);\n'
    if "hcsr04" in sensors:
        code += "  digitalWrite(TRIG_PIN, LOW);\n  delayMicroseconds(2);\n"
        code += "  digitalWrite(TRIG_PIN, HIGH);\n  delayMicroseconds(10);\n"
        code += "  digitalWrite(TRIG_PIN, LOW);\n"
        code += "  long duration = pulseIn(ECHO_PIN, HIGH);\n"
        code += "  float distance = duration * 0.034 / 2;\n"
        code += '  Serial.print("Distance: "); Serial.println(distance);\n'
    code += "  delay(1000);\n"
    code += "}\n"
    
    return code

def generate_python_code(name: str, platform: str, sensors: List[str], comments: bool) -> str:
    """Generate Raspberry Pi Python code"""
    code = f"# {name} - Generated by AgentForge\n"
    code += f"# Platform: {PLATFORMS[platform]['name']}\n\n"
    
    code += "import time\n"
    if platform == "raspberry_pi_4":
        code += "import RPi.GPIO as GPIO\n"
    else:
        code += "from machine import Pin, I2C\n"
    
    if "dht11" in sensors or "dht22" in sensors:
        code += "import dht\n"
    
    code += "\n"
    code += "# Pin Setup\n"
    code += "GPIO.setmode(GPIO.BCM)\n" if platform == "raspberry_pi_4" else ""
    
    if "dht11" in sensors:
        code += "DHT_PIN = 4\n"
        code += "dht_sensor = dht.DHT11(Pin(DHT_PIN))\n"
    
    code += "\ndef main():\n"
    code += "    while True:\n"
    if "dht11" in sensors or "dht22" in sensors:
        code += "        dht_sensor.measure()\n"
        code += "        temp = dht_sensor.temperature()\n"
        code += "        humidity = dht_sensor.humidity()\n"
        code += '        print(f"Temp: {temp}C, Humidity: {humidity}%")\n'
    code += "        time.sleep(1)\n"
    code += "\nif __name__ == '__main__':\n    main()\n"
    
    return code

def generate_stm32_code(name: str, platform: str, sensors: List[str], comments: bool) -> str:
    """Generate STM32 HAL code"""
    code = f"/* {name} - Generated by AgentForge */\n"
    code += f"/* Platform: {PLATFORMS[platform]['name']} */\n\n"
    code += '#include "main.h"\n#include "stm32f1xx_hal.h"\n\n'
    code += "int main(void) {\n"
    code += "  HAL_Init();\n"
    code += "  SystemClock_Config();\n"
    code += "  MX_GPIO_Init();\n"
    code += "  MX_USART1_UART_Init();\n\n"
    code += "  while (1) {\n"
    code += "    // Sensor reading code here\n"
    code += "    HAL_Delay(1000);\n"
    code += "  }\n"
    code += "}\n"
    return code

def generate_teensy_code(name: str, platform: str, sensors: List[str], comments: bool) -> str:
    """Generate Teensy code"""
    code = f"// {name} - Generated by AgentForge\n"
    code += f"// Platform: {PLATFORMS[platform]['name']}\n\n"
    code += "void setup() {\n"
    code += "  Serial.begin(115200);\n"
    code += "  while (!Serial) { }\n"
    code += '  Serial.println("Teensy Ready");\n'
    code += "}\n\n"
    code += "void loop() {\n"
    code += "  // Sensor code here\n"
    code += "  delay(1000);\n"
    code += "}\n"
    return code

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    result = await db.hardware_projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}
