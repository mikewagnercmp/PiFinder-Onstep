#!/usr/bin/python3
"""
Test mount time format and timezone
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'PiFinder'))

from PiFinder import mount_control
import logging
import time
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mount_time():
    """Test mount time format and timezone"""
    
    print("=== AP Mount Time Test ===\n")
    
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
    
    # Check mount time settings
    print("\n=== Mount Time Settings ===")
    
    # Get local time
    local_time = mount_api.mount.interface.send_command(":GL#")
    print(f"Mount local time: '{local_time}'")
    
    # Get sidereal time
    sidereal_time = mount_api.mount.interface.send_command(":GS#")
    print(f"Mount sidereal time: '{sidereal_time}'")
    
    # Get timezone offset
    timezone_offset = mount_api.mount.interface.send_command(":GG#")
    print(f"Mount timezone offset: '{timezone_offset}'")
    
    # Get current system time
    now = datetime.now()
    print(f"System local time: {now.strftime('%H:%M:%S')}")
    
    # Calculate expected offset
    print(f"\n=== Time Analysis ===")
    print(f"Current EDT offset: UTC-4 hours")
    print(f"Current EST offset: UTC-5 hours")
    
    # Test different RA formats
    print(f"\n=== Testing RA Format Interpretation ===")
    
    test_cases = [
        ("19:02:18", "19 hours 2 minutes 18 seconds"),
        ("07:02:18", "7 hours 2 minutes 18 seconds"),
        ("15:02:18", "15 hours 2 minutes 18 seconds (19:02:18 - 4 hours)"),
    ]
    
    for ra_format, description in test_cases:
        print(f"\n--- Testing {ra_format} ({description}) ---")
        
        # Send RA command
        ra_command = f":Sr{ra_format}#"
        print(f"Sending: {ra_command}")
        response = mount_api.mount.interface.send_command(ra_command)
        print(f"Response: '{response}'")
        
        if response == "1":
            print("✅ RA set successfully")
            
            # Wait a moment
            time.sleep(0.5)
            
            # Check what mount reports
            current_ra = mount_api.mount.interface.send_command(":GR#")
            print(f"Mount reports RA: '{current_ra}'")
            
            # Send sync command
            sync_response = mount_api.mount.interface.send_command(":CM#")
            print(f"Sync response: '{sync_response}'")
            
            # Wait and check final position
            time.sleep(1)
            final_ra = mount_api.mount.interface.send_command(":GR#")
            print(f"Final RA: '{final_ra}'")
        else:
            print("❌ RA set failed")
        
        time.sleep(1)  # Wait between tests
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_mount_time()
