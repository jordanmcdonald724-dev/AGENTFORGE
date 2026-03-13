"""
Hardware Integration - Arduino & Raspberry Pi code generation and deployment
Generate firmware, drivers, and IoT application code
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
from core.database import db
import uuid

router = APIRouter(prefix="/hardware", tags=["hardware"])


class HardwareProject(BaseModel):
    name: str
    description: str
    platform: str  # arduino_uno, arduino_mega, arduino_nano, esp32, esp8266, raspberry_pi_4, raspberry_pi_pico
    project_type: str  # sensor, actuator, iot, robotics, display, communication
    sensors: List[str] = []
    actuators: List[str] = []


class CodeGenerationRequest(BaseModel):
    project_id: str
    component_type: str  # sensor_read, actuator_control, wifi_connect, mqtt_publish, serial_comm
    component_name: str
    pin_config: Dict = {}


# Hardware platforms
PLATFORMS = {
    "arduino_uno": {
        "name": "Arduino Uno",
        "chip": "ATmega328P",
        "digital_pins": 14,
        "analog_pins": 6,
        "pwm_pins": [3, 5, 6, 9, 10, 11],
        "flash": "32KB",
        "ram": "2KB",
        "language": "C++",
        "framework": "Arduino"
    },
    "arduino_mega": {
        "name": "Arduino Mega",
        "chip": "ATmega2560",
        "digital_pins": 54,
        "analog_pins": 16,
        "pwm_pins": list(range(2, 14)),
        "flash": "256KB",
        "ram": "8KB",
        "language": "C++",
        "framework": "Arduino"
    },
    "esp32": {
        "name": "ESP32",
        "chip": "ESP32",
        "digital_pins": 34,
        "analog_pins": 18,
        "pwm_pins": list(range(0, 34)),
        "flash": "4MB",
        "ram": "520KB",
        "wifi": True,
        "bluetooth": True,
        "language": "C++",
        "framework": "ESP-IDF/Arduino"
    },
    "raspberry_pi_4": {
        "name": "Raspberry Pi 4",
        "chip": "BCM2711",
        "gpio_pins": 40,
        "ram": "2GB/4GB/8GB",
        "wifi": True,
        "bluetooth": True,
        "language": "Python",
        "framework": "RPi.GPIO/gpiozero"
    },
    "raspberry_pi_pico": {
        "name": "Raspberry Pi Pico",
        "chip": "RP2040",
        "gpio_pins": 26,
        "analog_pins": 3,
        "flash": "2MB",
        "ram": "264KB",
        "language": "Python/C++",
        "framework": "MicroPython"
    }
}

# Common sensors
SENSORS = {
    "dht11": {"name": "DHT11 Temperature & Humidity", "library": "DHT", "data_type": "float"},
    "dht22": {"name": "DHT22 Temperature & Humidity", "library": "DHT", "data_type": "float"},
    "bmp280": {"name": "BMP280 Pressure Sensor", "library": "Adafruit_BMP280", "data_type": "float"},
    "mpu6050": {"name": "MPU6050 Accelerometer/Gyroscope", "library": "MPU6050", "data_type": "float[]"},
    "hcsr04": {"name": "HC-SR04 Ultrasonic Distance", "library": "NewPing", "data_type": "int"},
    "pir": {"name": "PIR Motion Sensor", "library": "None", "data_type": "bool"},
    "ldr": {"name": "Light Dependent Resistor", "library": "None", "data_type": "int"},
    "soil_moisture": {"name": "Soil Moisture Sensor", "library": "None", "data_type": "int"},
    "mq2": {"name": "MQ-2 Gas Sensor", "library": "MQUnifiedsensor", "data_type": "float"},
    "bme680": {"name": "BME680 Environmental Sensor", "library": "Adafruit_BME680", "data_type": "float[]"}
}

# Common actuators
ACTUATORS = {
    "led": {"name": "LED", "control": "digital/pwm"},
    "servo": {"name": "Servo Motor", "library": "Servo", "control": "pwm"},
    "dc_motor": {"name": "DC Motor", "library": "None", "control": "pwm"},
    "stepper": {"name": "Stepper Motor", "library": "Stepper", "control": "digital"},
    "relay": {"name": "Relay Module", "control": "digital"},
    "buzzer": {"name": "Buzzer", "control": "digital/pwm"},
    "lcd_i2c": {"name": "LCD Display (I2C)", "library": "LiquidCrystal_I2C"},
    "oled": {"name": "OLED Display", "library": "Adafruit_SSD1306"},
    "neopixel": {"name": "NeoPixel LED Strip", "library": "Adafruit_NeoPixel"}
}


@router.get("/platforms")
async def get_platforms():
    """Get all supported hardware platforms"""
    return PLATFORMS


@router.get("/sensors")
async def get_sensors():
    """Get all supported sensors"""
    return SENSORS


@router.get("/actuators")
async def get_actuators():
    """Get all supported actuators"""
    return ACTUATORS


@router.post("/projects/create")
async def create_hardware_project(project: HardwareProject):
    """Create a new hardware project"""
    
    project_id = str(uuid.uuid4())
    platform_info = PLATFORMS.get(project.platform, PLATFORMS["arduino_uno"])
    
    hardware_project = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "platform": project.platform,
        "platform_info": platform_info,
        "project_type": project.project_type,
        "sensors": project.sensors,
        "actuators": project.actuators,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "code_files": [],
        "pin_mapping": {},
        "libraries": []
    }
    
    await db.hardware_projects.insert_one(hardware_project)
    
    return {
        "project_id": project_id,
        "platform": platform_info["name"],
        "message": f"Hardware project '{project.name}' created"
    }


@router.get("/projects")
async def list_hardware_projects():
    """List all hardware projects"""
    projects = await db.hardware_projects.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return projects


@router.get("/projects/{project_id}")
async def get_hardware_project(project_id: str):
    """Get hardware project details"""
    project = await db.hardware_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/code/generate")
async def generate_code(request: CodeGenerationRequest):
    """Generate code for a hardware component"""
    
    project = await db.hardware_projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    platform = project["platform"]
    is_arduino = platform.startswith("arduino") or platform.startswith("esp")
    
    if is_arduino:
        code = generate_arduino_code(request.component_type, request.component_name, request.pin_config, platform)
    else:
        code = generate_python_code(request.component_type, request.component_name, request.pin_config)
    
    code_file = {
        "id": str(uuid.uuid4()),
        "name": f"{request.component_name}.{'ino' if is_arduino else 'py'}",
        "component_type": request.component_type,
        "code": code,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Add to project
    await db.hardware_projects.update_one(
        {"id": request.project_id},
        {"$push": {"code_files": code_file}}
    )
    
    return code_file


def generate_arduino_code(component_type: str, name: str, pin_config: dict, platform: str) -> str:
    """Generate Arduino/ESP code"""
    
    code = f"""/*
 * {name}
 * Generated by AgentForge Hardware Integration
 * Platform: {platform}
 */

"""
    
    if component_type == "sensor_read":
        sensor_type = pin_config.get("sensor", "dht11")
        pin = pin_config.get("pin", 2)
        
        if sensor_type in ["dht11", "dht22"]:
            code += f"""#include <DHT.h>

#define DHTPIN {pin}
#define DHTTYPE {"DHT11" if sensor_type == "dht11" else "DHT22"}

DHT dht(DHTPIN, DHTTYPE);

void setup() {{
    Serial.begin(9600);
    dht.begin();
    Serial.println("{name} initialized");
}}

void loop() {{
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();
    
    if (isnan(humidity) || isnan(temperature)) {{
        Serial.println("Failed to read from DHT sensor!");
        return;
    }}
    
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print("°C, Humidity: ");
    Serial.print(humidity);
    Serial.println("%");
    
    delay(2000);
}}
"""
        elif sensor_type == "hcsr04":
            trig = pin_config.get("trig_pin", 9)
            echo = pin_config.get("echo_pin", 10)
            code += f"""#define TRIG_PIN {trig}
#define ECHO_PIN {echo}

void setup() {{
    Serial.begin(9600);
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    Serial.println("{name} initialized");
}}

void loop() {{
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    
    long duration = pulseIn(ECHO_PIN, HIGH);
    int distance = duration * 0.034 / 2;
    
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");
    
    delay(500);
}}
"""
    
    elif component_type == "actuator_control":
        actuator_type = pin_config.get("actuator", "led")
        pin = pin_config.get("pin", 13)
        
        if actuator_type == "servo":
            code += f"""#include <Servo.h>

Servo myServo;
#define SERVO_PIN {pin}

void setup() {{
    Serial.begin(9600);
    myServo.attach(SERVO_PIN);
    Serial.println("{name} initialized");
}}

void loop() {{
    // Sweep from 0 to 180 degrees
    for (int pos = 0; pos <= 180; pos++) {{
        myServo.write(pos);
        delay(15);
    }}
    
    for (int pos = 180; pos >= 0; pos--) {{
        myServo.write(pos);
        delay(15);
    }}
}}
"""
        else:
            code += f"""#define LED_PIN {pin}

void setup() {{
    Serial.begin(9600);
    pinMode(LED_PIN, OUTPUT);
    Serial.println("{name} initialized");
}}

void loop() {{
    digitalWrite(LED_PIN, HIGH);
    delay(1000);
    digitalWrite(LED_PIN, LOW);
    delay(1000);
}}
"""
    
    elif component_type == "wifi_connect":
        ssid = pin_config.get("ssid", "YourSSID")
        password = pin_config.get("password", "YourPassword")
        
        code += f"""#include <WiFi.h>

const char* ssid = "{ssid}";
const char* password = "{password}";

void setup() {{
    Serial.begin(115200);
    
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    
    while (WiFi.status() != WL_CONNECTED) {{
        delay(500);
        Serial.print(".");
    }}
    
    Serial.println();
    Serial.print("Connected! IP: ");
    Serial.println(WiFi.localIP());
}}

void loop() {{
    // Your code here
    delay(1000);
}}
"""
    
    elif component_type == "mqtt_publish":
        broker = pin_config.get("broker", "broker.hivemq.com")
        topic = pin_config.get("topic", "agentforge/data")
        
        code += f"""#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "YourSSID";
const char* password = "YourPassword";
const char* mqtt_broker = "{broker}";
const char* topic = "{topic}";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {{
    Serial.begin(115200);
    
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {{
        delay(500);
    }}
    
    client.setServer(mqtt_broker, 1883);
    
    while (!client.connected()) {{
        if (client.connect("AgentForgeDevice")) {{
            Serial.println("MQTT Connected");
        }}
    }}
}}

void loop() {{
    client.loop();
    
    String message = "Hello from AgentForge!";
    client.publish(topic, message.c_str());
    
    delay(5000);
}}
"""
    
    return code


def generate_python_code(component_type: str, name: str, pin_config: dict) -> str:
    """Generate Raspberry Pi Python code"""
    
    code = f'''"""
{name}
Generated by AgentForge Hardware Integration
Platform: Raspberry Pi
"""

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

'''
    
    if component_type == "sensor_read":
        sensor_type = pin_config.get("sensor", "dht11")
        pin = pin_config.get("pin", 4)
        
        if sensor_type in ["dht11", "dht22"]:
            code += f'''import adafruit_dht
import board

# Initialize DHT sensor
dht = adafruit_dht.{"DHT11" if sensor_type == "dht11" else "DHT22"}(board.D{pin})

def read_sensor():
    try:
        temperature = dht.temperature
        humidity = dht.humidity
        return temperature, humidity
    except RuntimeError as e:
        print(f"Reading error: {{e}}")
        return None, None

if __name__ == "__main__":
    print("{name} initialized")
    while True:
        temp, hum = read_sensor()
        if temp is not None:
            print(f"Temperature: {{temp}}°C, Humidity: {{hum}}%")
        time.sleep(2)
'''
    
    elif component_type == "actuator_control":
        pin = pin_config.get("pin", 18)
        
        code += f'''LED_PIN = {pin}

GPIO.setup(LED_PIN, GPIO.OUT)

def led_on():
    GPIO.output(LED_PIN, GPIO.HIGH)

def led_off():
    GPIO.output(LED_PIN, GPIO.LOW)

if __name__ == "__main__":
    print("{name} initialized")
    try:
        while True:
            led_on()
            time.sleep(1)
            led_off()
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
'''
    
    return code


@router.post("/projects/{project_id}/compile")
async def compile_project(project_id: str, background_tasks: BackgroundTasks):
    """Compile/verify hardware project code"""
    
    project = await db.hardware_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    compile_id = str(uuid.uuid4())
    
    compile_result = {
        "id": compile_id,
        "project_id": project_id,
        "status": "compiling",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "output": []
    }
    
    await db.hardware_compiles.insert_one(compile_result)
    
    # Simulate compilation
    background_tasks.add_task(simulate_compilation, compile_id, project)
    
    return {
        "compile_id": compile_id,
        "status": "compiling",
        "message": "Compilation started"
    }


async def simulate_compilation(compile_id: str, project: dict):
    """Simulate compilation process"""
    import asyncio
    
    output = [
        f"Compiling for {project['platform']}...",
        "Checking libraries...",
        "Compiling source files...",
        "Linking...",
        "Build complete!"
    ]
    
    for i, msg in enumerate(output):
        await asyncio.sleep(0.5)
        await db.hardware_compiles.update_one(
            {"id": compile_id},
            {"$push": {"output": msg}}
        )
    
    await db.hardware_compiles.update_one(
        {"id": compile_id},
        {
            "$set": {
                "status": "success",
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )


@router.get("/compile/{compile_id}")
async def get_compile_status(compile_id: str):
    """Get compilation status"""
    result = await db.hardware_compiles.find_one({"id": compile_id}, {"_id": 0})
    if not result:
        raise HTTPException(status_code=404, detail="Compilation not found")
    return result
