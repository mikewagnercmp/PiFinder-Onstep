#!/usr/bin/python3
"""
Test timezone conversion fix for AP mount
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'PiFinder'))

from PiFinder import mount_control
import logging
import time
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_ra_to_local_time(ra_hours, mount_local_time, mount_sidereal_time):
    """
    Convert RA coordinates to local time that mount will interpret correctly
    
    The mount interprets our RA input as local time, then converts to sidereal time.
    We need to send local time that will result in the desired sidereal time.
    """
    # Parse mount times
    local_parts = mount_local_time.strip('#').split(':')
    local_h = int(local_parts[0])
    local_m = int(local_parts[1])
    local_s = float(local_parts[2])
    
    sidereal_parts = mount_sidereal_time.strip('#').split(':')
    sidereal_h = int(sidereal_parts[0])
    sidereal_m = int(sidereal_parts[1])
    sidereal_s = float(sidereal_parts[2])
    
    # Convert to decimal hours
    local_decimal = local_h + local_m/60 + local_s/3600
    sidereal_decimal = sidereal_h + sidereal_m/60 + sidereal_s/3600
    ra_decimal = ra_hours
    
    # Calculate the difference between current sidereal and target RA
    sidereal_diff = ra_decimal - sidereal_decimal
    
    # Apply this difference to local time
    target_local_decimal = local_decimal + sidereal_diff
    
    # Handle 24-hour wrap-around
    target_local_decimal = target_local_decimal % 24
    
    # Convert back to HH:MM:SS format
    target_h = int(target_local_decimal)
    target_m = int((target_local_decimal - target_h) * 60)
    target_s = int(((target_local_decimal - target_h) * 60 - target_m) * 60)
    
    return f"{target_h:02d}:{target_m:02d}:{target_s:02d}"

def test_timezone_fix():
    """Test timezone conversion fix"""
    
    print("=== AP Mount Timezone Fix Test ===\n")
    
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
    mount_timezone = mount_api.mount.interface.send_command(":GG#")
    
    print(f"Mount local time: '{mount_local}'")
    print(f"Mount sidereal time: '{mount_sidereal}'")
    print(f"Mount timezone offset: '{mount_timezone}'")
    
    # Get initial position
    initial_ra = mount_api.mount.interface.send_command(":GR#")
    initial_dec = mount_api.mount.interface.send_command(":GD#")
    print(f"Initial RA: '{initial_ra}'")
    print(f"Initial DEC: '{initial_dec}'")
    
    # Test target coordinates (what we want to achieve)
    target_ra_hours = 19 + 2/60 + 18/3600  # 19:02:18 in decimal hours
    target_dec = "+32:45:17"
    
    print(f"\n=== Target Coordinates ===")
    print(f"Target RA: 19:02:18 ({target_ra_hours:.6f} hours)")
    print(f"Target DEC: {target_dec}")
    
    # Convert RA to local time
    converted_ra = convert_ra_to_local_time(target_ra_hours, mount_local, mount_sidereal)
    
    print(f"\n=== Timezone Conversion ===")
    print(f"Original RA (sidereal): 19:02:18")
    print(f"Converted RA (local): {converted_ra}")
    
    # Test the conversion
    print(f"\n=== Testing Converted Coordinates ===")
    
    # Set coordinates using converted RA
    ra_response = mount_api.mount.interface.send_command(f":Sr{converted_ra}#")
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
            print("✅ SUCCESS! Mount went to approximately 19:02 RA!")
        else:
            print("❌ Mount did not go to target RA")
    else:
        print("❌ Failed to set coordinates")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_timezone_fix()
