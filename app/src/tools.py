from config import *
import datetime
import sys
import asyncio
import json

def std_out(msg, priority=False):
    if DEBUG or priority:
        if TIMESTAMP:
            sys.stdout.write(f"{datetime.datetime.now()}: {msg}\n")
        else:
            sys.stdout.write(msg)

async def tcp_state_client(message):
    reader, writer = await asyncio.open_connection(
                    LOGGER_IP, LOGGER_PORT)
    writer.write(json.dumps(message).encode())
    await writer.drain()

    writer.close()
    await writer.wait_closed()

def display_data(message):

    # Extracting data from the message
    lowstate=message['LOW_STATE']
    multiplestate=message['MULTIPLE_STATE']
    sportstate=message['LF_SPORT_MOD_STATE']

    motor_state = lowstate['motor_state']
    bms_state = lowstate['bms_state']
    foot_force = lowstate['foot_force']
    temperature_ntc1 = lowstate['temperature_ntc1']
    power_v = lowstate['power_v']

    imu_state = sportstate['imu_state']
    quaternion = imu_state['quaternion']
    gyroscope = imu_state['gyroscope']
    accelerometer = imu_state['accelerometer']
    rpy = imu_state['rpy']
    temperature = imu_state['temperature']
    mode = sportstate['mode']
    progress = sportstate['progress']
    gait_type = sportstate['gait_type']
    foot_raise_height = sportstate['foot_raise_height']
    position = sportstate['position']
    body_height = sportstate['body_height']
    velocity = sportstate['velocity']
    yaw_speed = sportstate['yaw_speed']
    range_obstacle = sportstate['range_obstacle']
    foot_force = sportstate['foot_force']
    foot_position_body = sportstate['foot_position_body']
    foot_speed_body = sportstate['foot_speed_body']

    # body_height = multiplestate['bodyHeight']
    brightness = multiplestate['brightness']
    # foot_raise_height = multiplestate['footRaiseHeight']
    obstacles_avoid_switch = multiplestate['obstaclesAvoidSwitch']
    speed_level = multiplestate['speedLevel']
    uwb_switch = multiplestate['uwbSwitch']
    volume = multiplestate['volume']

    # Clear the entire screen and reset cursor position to top
    sys.stdout.write("\033[H\033[J")

    # Print the Go2 Robot Status
    print("Go2 Robot Status")
    print("===========================")
    print(f"Mode: {mode}")
    print(f"Progress: {progress}")
    print(f"Gait Type: {gait_type}")
    print(f"Foot Raise Height: {foot_raise_height} m")
    print(f"Position: {position}")
    print(f"Body Height: {body_height} m")
    print(f"Velocity: {velocity}")
    print(f"Yaw Speed: {yaw_speed}")
    print(f"Range Obstacle: {range_obstacle}")

    # IMU State (RPY)
    print(f"IMU - RPY: Roll: {rpy[0]}, Pitch: {rpy[1]}, Yaw: {rpy[2]}")
    print(f"IMU - Quaternion: {quaternion}")
    print(f"IMU - Gyroscope: {gyroscope}")
    print(f"IMU - Accelerometer: {accelerometer}")
    print(f"IMU - RPY: {rpy}")
    print(f"IMU - Temperature: {temperature}°C")

  # Compact Motor States Display (Each motor on one line)
    print("\nMotor States (q, Temperature, Lost):")
    print("------------------------------------------------------------")
    for i, motor in enumerate(motor_state):
        # Display motor info in a single line
        print(f"Motor {i + 1:2}: q={motor['q']:.4f}, Temp={motor['temperature']}°C, Lost={motor['lost']}")

    # BMS (Battery Management System) State
    print("\nBattery Management System (BMS) State:")
    print(f"  Version: {bms_state['version_high']}.{bms_state['version_low']}")
    print(f"  SOC (State of Charge): {bms_state['soc']}%")
    print(f"  Current: {bms_state['current']} mA")
    print(f"  Cycle Count: {bms_state['cycle']}")
    print(f"  BQ NTC: {bms_state['bq_ntc']}°C")
    print(f"  MCU NTC: {bms_state['mcu_ntc']}°C")

    # Foot Force
    print(f"\nFoot Force: {foot_force}")
    # Too much info
    # print(f"Foot Position (Body): {foot_position_body}")
    # print(f"Foot Speed (Body): {foot_speed_body}")

    print(f"Brightness:            {brightness}")
    print(f"Obstacles Avoid Switch: {'Enabled' if obstacles_avoid_switch else 'Disabled'}")
    print(f"Speed Level:           {speed_level}")
    print(f"UWB Switch:            {'On' if uwb_switch else 'Off'}")
    print(f"Volume:                {volume}/10")

    # Additional Sensors
    print(f"Temperature NTC1: {temperature_ntc1}°C")
    print(f"Power Voltage: {power_v}V")

    # Optionally, flush to ensure immediate output
    sys.stdout.flush()

