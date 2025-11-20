from xarm.wrapper import XArmAPI
import time

# Replace with your xArm5's actual IP address
XARM5_IP = '192.168.1.XXX'  # TODO: Set your xArm5 IP address here

def main():
    arm = XArmAPI(XARM5_IP)
    
    print(f"Connecting to xArm5 at {XARM5_IP}...")
    arm.connect()
    
    print("Enabling motion...")
    arm.motion_enable(enable=True)
    arm.set_mode(0)  # Position control mode
    arm.set_state(0) # Set to ready
    
    print("Moving to home position...")
    arm.set_servo_angle(angle=[0, 0, 0, 0, 0], speed=20, wait=True)
    time.sleep(1)
    
    # Example: Move to another position
    # print("Moving to another position...")
    # arm.set_servo_angle(angle=[0, -30, 30, 0, 0], speed=20, wait=True)
    # time.sleep(1)
    
    print("Disconnecting...")
    arm.disconnect()
    print("Done.")

if __name__ == "__main__":
    main()
