import smbus2
import math
import time
import paho.mqtt.client as mqtt
import json  # Import json module

# I2C Address for MPU9250
MPU9250_ADDR = 0x68
MAGNETOMETER_ADDR = 0x0C

# MPU9250 Registers
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43
TEMP_OUT_H = 0x41

# Initialize I2C bus
bus = smbus2.SMBus(4)  # 1 is usually for Raspberry Pi / Orange Pi (I2C bus)

# MQTT Settings
mqtt_broker = "192.168.195.49"  # Use your MQTT broker address
mqtt_port = 1883
mqtt_topic = "mpu6050/data"

# MQTT Client setup
client = mqtt.Client()
client.connect(mqtt_broker, mqtt_port, 60)

# Function to read data from MPU9250
def read_bytes(addr, reg, length):
    data = bus.read_i2c_block_data(addr, reg, length)
    return data

# Convert data to 16-bit signed integer
def to_signed_16bit(data):
    val = (data[0] << 8) + data[1]
    if val >= 0x8000:
        val -= 0x10000
    return val

# Function to read sensor data from MPU9250
def read_mpu9250():
    accel_data = read_bytes(MPU9250_ADDR, ACCEL_XOUT_H, 6)
    accel_x = to_signed_16bit(accel_data[0:2])
    accel_y = to_signed_16bit(accel_data[2:4])
    accel_z = to_signed_16bit(accel_data[4:6])

    gyro_data = read_bytes(MPU9250_ADDR, GYRO_XOUT_H, 6)
    gyro_x = to_signed_16bit(gyro_data[0:2])
    gyro_y = to_signed_16bit(gyro_data[2:4])
    gyro_z = to_signed_16bit(gyro_data[4:6])

    return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z

# Function to calculate pitch, roll, and yaw
def calculate_angles(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z):
    # Calculate the pitch (rotation around the X axis)
    pitch = math.atan2(accel_y, math.sqrt(accel_x**2 + accel_z**2)) * 180 / math.pi
    
    # Calculate the roll (rotation around the Y axis)
    roll = math.atan2(-accel_x, accel_z) * 180 / math.pi
    
    # Calculate yaw (rotation around the Z axis)
    # Using gyroscope data for yaw estimation (approximation)
    yaw = math.atan2(gyro_y, gyro_x) * 180 / math.pi
    
    return roll, pitch, yaw

# Function to publish data to MQTT
def publish_data(roll, pitch, yaw):
    payload = {
        'roll': roll,
        'pitch': pitch,
        'yaw': yaw
    }
    # Use json.dumps() to convert the dictionary into a JSON-formatted string
    json_payload = json.dumps(payload)
    client.publish(mqtt_topic, json_payload)

# Initialize MPU9250
bus.write_byte_data(MPU9250_ADDR, PWR_MGMT_1, 0)  # Wake up MPU9250

while True:
    accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = read_mpu9250()
    
    # Convert raw accelerometer data to G (gravitational force)
    accel_x = accel_x / 16384.0
    accel_y = accel_y / 16384.0
    accel_z = accel_z / 16384.0

    # Calculate roll, pitch, and yaw
    roll, pitch, yaw = calculate_angles(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z)
    
    # Publish data to MQTT
    publish_data(roll, pitch, yaw)

    # Print to console
    print(f"Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")

    time.sleep(1)
