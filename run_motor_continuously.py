import argparse
import time

try:
    from pymodbus.client import ModbusSerialClient
except ImportError:
    print("Please install pymodbus: pip install pymodbus")
    exit(1)

# DA200A Vector Control VFD Registers & Constants
REG_BUS_SOURCE = 1820       # P4.10
REG_BUS_ENABLE = 1822       # P4.11
REG_SPEED_CMD = 1826        # P4.13
REG_ACCEL_TIME = 1108       # P0.54
REG_DECEL_TIME = 1110       # P0.55
DEVICE_ID = 1               # Default Modbus slave ID

VFD_RPM_SCALE = 10          # Speed commands are written in 0.1 RPM units

def write_u16(client, addr, value, label):
    """Write a single 16-bit register to the driver."""
    # Note: Depending on your pymodbus version, you might need to use `slave=DEVICE_ID` instead of `device_id=DEVICE_ID`
    kwargs = {'slave': DEVICE_ID} if hasattr(client, 'protocol') else {'device_id': DEVICE_ID}
    
    resp = client.write_register(addr, value & 0xFFFF, **kwargs)
    if resp is None or resp.isError():
        raise RuntimeError(f"Failed to write register {addr} ({label})")


def write_speed(client, rpm):
    """Write target speed in RPM using 32-bit wide register."""
    # Convert RPM to 0.1 RPM register value unit
    rpm = int(rpm)
    reg_value = rpm * VFD_RPM_SCALE  
    
    # Pack as two 16-bit words (Little Endian format for DA200A)
    u = reg_value & 0xFFFFFFFF
    lo = u & 0xFFFF
    hi = (u >> 16) & 0xFFFF
    
    kwargs = {'slave': DEVICE_ID} if hasattr(client, 'protocol') else {'device_id': DEVICE_ID}
    resp = client.write_registers(REG_SPEED_CMD, [lo, hi], **kwargs)
    
    if resp is None or resp.isError():
        raise RuntimeError(f"Failed to write speed command: {rpm} RPM")


def main():
    parser = argparse.ArgumentParser(description="Run DA200A Modbus Motor Continuously")
    parser.add_argument("--port", type=str, default="/dev/ttyUSB_LEFT", help="Serial port to the motor driver")
    parser.add_argument("--rpm", type=int, default=1000, help="Target RPM to spin the motor")
    parser.add_argument("--baudrate", type=int, default=19200, help="Baudrate for Modbus communication")
    args = parser.parse_args()

    client = ModbusSerialClient(
        port=args.port,
        baudrate=args.baudrate,
        parity="N",
        stopbits=1,
        bytesize=8,
        timeout=0.3,
        retries=1
    )

    if not client.connect():
        print(f"[ERROR] Failed to connect to Modbus driver at {args.port}")
        return

    print(f"[SUCCESS] Connected to {args.port}")
    print("Initializing Modbus communication settings...")
    
    try:
        # P4.10=1: Bus command source
        write_u16(client, REG_BUS_SOURCE, 1, "Bus Source")
        
        # P0.54=10 / P0.55=10: Set acceleration and deceleration time to 1.0s
        write_u16(client, REG_ACCEL_TIME, 10, "Accel Time")
        write_u16(client, REG_DECEL_TIME, 10, "Decel Time")

        print("Enabling Drive Bus...")
        # Start at 0 RPM
        write_speed(client, 0)
        
        # P4.11=1: Enable bus control
        write_u16(client, REG_BUS_ENABLE, 1, "Bus Enable")
        time.sleep(0.2)
        
    except RuntimeError as e:
        print(f"[ERROR] Motor Initialization Failed: {e}")
        client.close()
        return

    print("--------------------------------------------------")
    print(f"?? Motor is starting up at {args.rpm} RPM.")
    print("?? Press Ctrl+C directly in this terminal to STOP safely.")
    print("--------------------------------------------------")

    try:
        write_speed(client, args.rpm)
        
        # Keep the script running to hold the motor command
        # If the script exits, we wouldn't be able to catch the stop event cleanly
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[WARNING] Halting command received (Ctrl+C). Stopping motor SAFELY...")
    finally:
        try:
            write_speed(client, 0)
            time.sleep(0.1) # Give it a fraction of a second to send before closing
            print("[SUCCESS] Motor stopped successfully.")
        except Exception as e:
            print(f"[CRITICAL ERROR] Failed to stop motor cleanly: {e}")
            
        client.close()

if __name__ == "__main__":
    main()
