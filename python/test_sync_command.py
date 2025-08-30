#!/usr/bin/python3
"""
Test script to debug sync command format
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'PiFinder'))

from PiFinder import mount_control
from PiFinder import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sync_command():
    """Test sync command format"""
    
    print("=== Sync Command Test ===\n")
    
    # Create mount API with correct IP
    try:
        mount_api = mount_control.MountControlAPI(
            mount_type="astro_physics",
            host="192.168.1.182",
            port=23
        )
        print(f"✅ Mount API created for astro_physics at 192.168.1.182:23")
    except Exception as e:
        print(f"❌ Failed to create mount API: {e}")
        return
    
    # Test connection
    if not mount_api.mount or not mount_api.mount.connected:
        print("❌ Mount not connected!")
        return
    
    print("✅ Mount is connected!")
    
    # Test coordinate conversion
    print("\n=== Testing Coordinate Conversion ===")
    
    # Test with some sample coordinates
    test_coordinates = [
        (0.0, 90.0),      # Current mount position
        (180.0, 0.0),     # Some other position
        (45.0, 30.0),     # Another position
    ]
    
    for ra_deg, dec_deg in test_coordinates:
        print(f"\nTesting RA: {ra_deg:.6f}°, DEC: {dec_deg:.6f}°")
        
        # Convert to mount format
        ra_str = mount_api.mount._degrees_to_ra(ra_deg)
        dec_str = mount_api.mount._degrees_to_dec(dec_deg)
        
        print(f"Converted to: RA='{ra_str}', DEC='{dec_str}'")
        
        # Test sync command format
        sync_command = f":CS{ra_str},{dec_str}#"
        print(f"Sync command: '{sync_command}'")
        
        # Test if mount accepts the command
        try:
            response = mount_api.mount.interface.send_command(sync_command)
            print(f"Mount response: '{response}'")
            
            if response and "1" in response:
                print("✅ Sync command accepted!")
            else:
                print("❌ Sync command failed or rejected")
                
        except Exception as e:
            print(f"❌ Error sending sync command: {e}")
    
    # Test actual sync
    print("\n=== Testing Actual Sync ===")
    try:
        # Use current mount position for sync test
        current_position = mount_api.get_position()
        if current_position:
            ra_deg, dec_deg = current_position
            print(f"Attempting sync to current position: RA={ra_deg:.6f}°, DEC={dec_deg:.6f}°")
            
            success, message = mount_api.sync_to_position(ra_deg, dec_deg)
            print(f"Sync result: success={success}, message='{message}'")
        else:
            print("❌ No current position available")
            
    except Exception as e:
        print(f"❌ Error during sync test: {e}")
    
    # Clean up
    try:
        mount_api.close()
        print("\n✅ Test completed successfully")
    except Exception as e:
        print(f"❌ Error closing mount API: {e}")

if __name__ == "__main__":
    test_sync_command()
