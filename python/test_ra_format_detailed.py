#!/usr/bin/python3
"""
Test different RA formats for AP mount
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

def test_ra_format_detailed():
    """Test different RA formats for AP mount"""
    
    print("=== AP Mount RA Format Test ===\n")
    
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
    
    # Test different RA formats for 19:02:18
    test_formats = [
        "19:02:18",      # What we're currently sending
        "19:02:18.0",    # With decimal seconds
        "19:02:18.00",   # With two decimal places
        "07:02:18",      # What mount seems to expect
        "07:02:18.0",    # With decimal seconds
        "19:02:18.1",    # Slightly different decimal
        "19:02:18.5",    # Half second
        "19:02:18.9",    # Almost full second
    ]
    
    for ra_format in test_formats:
        print(f"\n--- Testing RA format: {ra_format} ---")
        
        # Send RA command
        ra_command = f":Sr{ra_format}#"
        print(f"Sending: {ra_command}")
        response = mount_api.mount.interface.send_command(ra_command)
        print(f"Response: '{response}'")
        
        if response == "1":
            print("✅ RA set successfully")
            
            # Wait a moment
            time.sleep(0.5)
            
            # Check what mount reports as current position
            current_ra = mount_api.mount.interface.send_command(":GR#")
            print(f"Mount reports current RA: '{current_ra}'")
            
            # Parse the response to see what the mount actually did
            if current_ra and '#' in current_ra:
                ra_str = current_ra.strip('#')
                print(f"Parsed RA: {ra_str}")
                
                # Check if it matches what we sent
                if ra_str.startswith(ra_format.split('.')[0]):  # Compare without decimals
                    print("✅ Mount position matches what we sent!")
                else:
                    print("❌ Mount position does NOT match what we sent!")
        else:
            print("❌ RA set failed")
        
        time.sleep(1)  # Wait between tests
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_ra_format_detailed()
