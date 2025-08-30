#!/usr/bin/python3
"""
Simple test to try sending sidereal time directly
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

def test_simple_approach():
    """Test simple approach - send sidereal time directly"""
    
    print("=== Simple Approach Test ===\n")
    
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
    
    # Get mount time information
    print("\n=== Mount Time Information ===")
    mount_local = mount_api.mount.interface.send_command(":GL#")
    mount_sidereal = mount_api.mount.interface.send_command(":GS#")
    
    print(f"Mount local time: '{mount_local}'")
    print(f"Mount sidereal time: '{mount_sidereal}'")
    
    # Get initial position
    initial_ra = mount_api.mount.interface.send_command(":GR#")
    print(f"Initial RA: '{initial_ra}'")
    
    # Try sending the exact sidereal time we want
    target_sidereal = "19:02:18"
    
    print(f"\n=== Testing Direct Sidereal Time ===")
    print(f"Target sidereal time: {target_sidereal}")
    
    # Set coordinates using target sidereal time directly
    ra_response = mount_api.mount.interface.send_command(f":Sr{target_sidereal}#")
    dec_response = mount_api.mount.interface.send_command(":Sd+32:45:17#")
    
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
        
        print(f"Final RA: '{final_ra}'")
        
        # Check if we got close to our target
        if "19:02" in final_ra:
            print("✅ SUCCESS! Mount went to approximately 19:02 RA!")
        else:
            print("❌ Mount did not go to target RA")
    else:
        print("❌ Failed to set coordinates")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_simple_approach()
