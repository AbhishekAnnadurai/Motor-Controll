# Motor Control System

A complete setup for running the DA200A Vector Control Variable Frequency Drive (VFD) via Modbus serial communication, integrated with an Arduino ultrasonic sensor for automatic safety halting.

## Features
- **Continuous Motor Control**: Scripts run endlessly to keep your motor humming smoothly.
- **Modbus Serial RTU**: Drives parameter writing correctly for the DA200A Vector System.
- **Safety Interlock**: Automatically monitors distance from an Arduino ultrasonic sensor. If an object breaches the 50cm threshold, the motor gracefully brakes until it's removed.

## Hardware Setup
- **Motor Control**: The VFD is attached via a USB-Serial interface adapter.
- **Ultrasonic**: An Arduino running the `arduino/ultrasonic_detection/ultrasonic_detection.ino` code is plugged into a separate USB port.

## Installation

### Windows setup
1. Open a command prompt
2. `pip install -r requirements.txt`

### Ubuntu/Linux setup
1. Install system prerequisites:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git
   ```
2. Enable serial port access. **You must relogin after running this constraint:**
   ```bash
   sudo usermod -a -G dialout $USER
   ```
3. Set up the repo environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

1. Open your Arduino IDE, load up the `.ino` file from the `arduino/` folder, and flash it to the board. Ensure you take note of what port it connects to (e.g., `COM3` on Windows or `/dev/ttyUSB1` on Linux).
2. Connect your Motor adapter and note its port as well.
3. Run the Python control script from within the source folder:

```bash
# Windows Example
python src/run_motor_continuously.py --port COM_MOTOR --arduino-port COM_ARDUINO --rpm 1000

# Linux Example
python src/run_motor_continuously.py --port /dev/ttyUSB0 --arduino-port /dev/ttyACM0 --rpm 1000
```
*(Remember to swap in the genuine port ids)*
