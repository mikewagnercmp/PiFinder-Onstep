#!/usr/bin/python3
"""
Test AP mount command formats
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

def test_ap_format():
    """Test AP mount command formats"""
    
    print("=== AP Mount Format Test ===\n")
    
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
    
    # Test different RA formats
    test_ra_values = [
        "19:32:25",  # What we're sending
        "07:32:25",  # What mount seems to expect
        "19:32:25.0",  # With decimal
        "07:32:25.0",  # With decimal
    ]
    
    for ra_format in test_ra_values:
        print(f"\n--- Testing RA format: {ra_format} ---")
        
        # Send RA command
        ra_command = f":Sr{ra_format}#"
        print(f"Sending: {ra_command}")
        response = mount_api.mount.interface.send_command(ra_command)
        print(f"Response: '{response}'")
        
        if response == "1":
            print("✅ RA set successfully")
            
            # Check what mount thinks we set
            commanded_ra = mount_api.mount.interface.send_command(":GR#")
            print(f"Mount reports commanded RA: '{commanded_ra}'")
        else:
            print("❌ RA set failed")
        
        time.sleep(1)  # Wait between tests
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_ap_format()
