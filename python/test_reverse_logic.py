#!/usr/bin/python3
"""
Test reverse logic based on observed pattern
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'PiFinder'))

from PiFinder import mount_control
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_reverse_logic():
    """Test reverse logic based on observed pattern"""
    
    print("=== Reverse Logic Test ===\n")
    
    # Create mount API
    try:
        mount_api = mount_control.MountControlAPI(
            mount_type="astro_physics",
            host="192.168.1.182",
            port=23
        )
        print(f"✅ Mount API created")
    except Exception as e:
        print(f"❌ Failed to create mount API: {e}")
        return
    
    if not mount_api.mount or not mount_api.mount.connected:
        print("❌ Mount not connected!")
        return
    
    print("✅ Mount is connected!")
    
    # Get initial position
    initial_ra = mount_api.mount.interface.send_command(":GR#")
    print(f"Initial RA: '{initial_ra}'")
    
    # Based on our observations:
    # Sending 19:02:18 -> Mount goes to 07:02:21
    # So to get to 19:02:18, we should send 07:02:18
    
    target_ra = "07:02:18"  # Try sending this to get to 19:02:18
    target_dec = "+32:45:17"
    
    print(f"\n=== Testing Reverse Logic ===")
    print(f"Sending RA: {target_ra} (hoping to get to 19:02:18)")
    print(f"Sending DEC: {target_dec}")
    
    # Set coordinates
    ra_response = mount_api.mount.interface.send_command(f":Sr{target_ra}#")
    dec_response = mount_api.mount.interface.send_command(f":Sd{target_dec}#")
    
    print(f"RA set response: '{ra_response}'")
    print(f"DEC set response: '{dec_response}'")
    
    if ra_response == "1" and dec_response == "1":
        print("✅ Coordinates set successfully")
        
        # Send sync command
        sync_response = mount_api.mount.interface.send_command(":CM#")
        print(f"Sync response: '{sync_response}'")
        
        # Wait and check final position
        time.sleep(2)
        final_ra = mount_api.mount.interface.send_command(":GR#")
        final_dec = mount_api.mount.interface.send_command(":GD#")
        
        print(f"Final RA: '{final_ra}'")
        print(f"Final DEC: '{final_dec}'")
        
        # Check if we got close to our target
        if "19:02" in final_ra:
            print("✅ SUCCESS! Reverse logic worked!")
        else:
            print("❌ Reverse logic did not work")
    else:
        print("❌ Failed to set coordinates")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_reverse_logic()
