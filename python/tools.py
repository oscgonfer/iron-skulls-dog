from config import *
import datetime
import sys

def std_out(msg, priority=False):
    if DEBUG or priority:
        if TIMESTAMP:
            print (f"{datetime.datetime.now()}: {msg}")
        else:
            print (msg)

def display_data(message):

    # Extracting data from the message
    imu_state = message['imu_state']['rpy']
    motor_state = message['motor_state']
    bms_state = message['bms_state']
    foot_force = message['foot_force']
    temperature_ntc1 = message['temperature_ntc1']
    power_v = message['power_v']

    # Clear the entire screen and reset cursor position to top
    sys.stdout.write("\033[H\033[J")

    # Print the Go2 Robot Status
    print("Go2 Robot Status (LowState)")
    print("===========================")

    # IMU State (RPY)
    print(f"IMU - RPY: Roll: {imu_state[0]}, Pitch: {imu_state[1]}, Yaw: {imu_state[2]}")

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

    # Additional Sensors
    print(f"Temperature NTC1: {temperature_ntc1}°C")
    print(f"Power Voltage: {power_v}V")

    # Optionally, flush to ensure immediate output
    sys.stdout.flush()

