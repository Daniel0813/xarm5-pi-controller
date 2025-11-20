from xarm.wrapper import XArmAPI
import time

# Replace with your xArm5's actual IP address
XARM5_IP = '192.168.1.231'  
# xArm5 factory home position (safe starting position)
HOME_POSITION = [103.7, -24.3, -1.9, 26.2, 14.8]

def print_joint_info():
    """Display joint information and movement directions"""
    print("\n=== xArm5 Joint Information ===")
    print("Joint 1 (Base):     + = clockwise (viewed from top)")
    print("Joint 2 (Shoulder): + = forward tilt")
    print("Joint 3 (Elbow):    + = upward bend") 
    print("Joint 4 (Wrist1):   + = clockwise rotation")
    print("Joint 5 (Wrist2):   + = clockwise rotation")
    print("All angles in degrees, typical range: -180 to +180")
    print("================================\n")

def get_current_position(arm):
    """Get and display current joint positions"""
    try:
        angles = arm.get_servo_angle()
        if angles[0] == 0:  # Success
            print(f"Current joint positions: {[round(a, 1) for a in angles[1]]}")
            return angles[1]
        else:
            print("Error getting current position")
            return None
    except Exception as e:
        print(f"Error getting position: {e}")
        return None

def move_single_joint(arm, current_angles):
    """Interactive function to move a single joint"""
    print_joint_info()
    
    # Get current position
    current = get_current_position(arm)
    if current is None:
        return False
        
    try:
        # Get joint selection
        print("Select joint to move (1-5) or 0 to return to menu:")
        joint_num = int(input("Joint number: "))
        
        if joint_num == 0:
            return True
        if joint_num < 1 or joint_num > 5:
            print("Invalid joint number. Must be 1-5.")
            return True
            
        # Get movement amount
        print(f"Current angle for Joint {joint_num}: {round(current[joint_num-1], 1)}°")
        angle_change = float(input("Enter angle change in degrees (+/-): "))
        
        # Safety check
        if abs(angle_change) > 30:
            print("Warning: Large movement detected!")
            confirm = input("Are you sure? (y/N): ").lower()
            if confirm != 'y':
                print("Movement cancelled.")
                return True
        
        # Calculate new position
        new_angles = current.copy()
        new_angles[joint_num-1] += angle_change
        
        # Safety limits check
        if abs(new_angles[joint_num-1]) > 180:
            print("Error: New angle would exceed safe limits (-180 to +180)")
            return True
        
        # Get speed
        speed = float(input("Enter movement speed (1-30 degrees/sec, recommended 5-10): "))
        speed = max(1, min(30, speed))  # Clamp to safe range
        
        print(f"Moving Joint {joint_num} by {angle_change}° at {speed}°/s...")
        print(f"New position will be: {[round(a, 1) for a in new_angles]}")
        
        # Execute movement
        ret = arm.set_servo_angle(angle=new_angles, speed=speed, wait=True)
        
        if ret == 0:
            print("✓ Movement completed successfully!")
        else:
            print(f"✗ Movement failed with error code: {ret}")
            
        return True
        
    except ValueError:
        print("Invalid input. Please enter numbers only.")
        return True
    except Exception as e:
        print(f"Error during movement: {e}")
        return True

def initialize_arm(arm):
    """Initialize arm safely and move to home position"""
    print(f"Connecting to xArm5 at {XARM5_IP}...")
    arm.connect()
    
    # Check arm state
    state = arm.get_state()
    print(f"Current arm state: {state}")
    
    # Clear any errors first
    print("Clearing any errors...")
    arm.clean_error()
    
    print("Enabling motion...")
    arm.motion_enable(enable=True)
    arm.set_mode(0)  # Position control mode
    arm.set_state(0) # Set to ready
    
    # Wait and check state again
    time.sleep(1)
    state = arm.get_state()
    print(f"Arm state after setup: {state}")
    
    if state[1] != 0:  # Check if there are errors
        print(f"Error detected: {state[1]}. Clearing errors...")
        arm.clean_error()
        arm.set_state(0)
        time.sleep(1)
    
    # Automatically move to home position for safety
    print("Moving to factory home position...")
    print(f"Target position: {HOME_POSITION}")
    ret = arm.set_servo_angle(angle=HOME_POSITION, speed=10, wait=True)
    
    if ret == 0:
        print("✓ Successfully moved to factory home position!")
        time.sleep(1)
        return True
    else:
        print(f"✗ Failed to reach home position, error code: {ret}")
        print("Warning: Continuing without home position - be extra careful!")
        return True

def main():
    arm = XArmAPI(XARM5_IP)
    
    try:
        # Initialize arm
        if not initialize_arm(arm):
            print("Failed to initialize arm")
            return
        
        print("\n=== xArm5 Interactive Controller ===")
        print("Use this tool to safely move individual joints")
        print("====================================")
        
        while True:
            print("\nOptions:")
            print("1. Move single joint")
            print("2. Go to home position (all joints to 0°)")
            print("3. Show current position")
            print("4. Exit")
            
            try:
                choice = input("\nEnter choice (1-4): ").strip()
                
                if choice == '1':
                    if not move_single_joint(arm, None):
                        break
                        
                elif choice == '2':
                    print("Moving to factory home position...")
                    print(f"Target position: {HOME_POSITION}")
                    ret = arm.set_servo_angle(angle=HOME_POSITION, speed=10, wait=True)
                    if ret == 0:
                        print("✓ Factory home position reached successfully!")
                    else:
                        print(f"✗ Failed to reach home position, error code: {ret}")
                        
                elif choice == '3':
                    get_current_position(arm)
                    
                elif choice == '4':
                    print("Exiting...")
                    break
                    
                else:
                    print("Invalid choice. Please enter 1-4.")
                    
            except KeyboardInterrupt:
                print("\n\nExiting due to Ctrl+C...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    except Exception as e:
        print(f"Error connecting to arm: {e}")
    
    finally:
        try:
            print("Disconnecting...")
            arm.disconnect()
            print("Done.")
        except:
            pass

if __name__ == "__main__":
    main()
