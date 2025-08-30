#!/usr/bin/python3
"""
Test :CM# vs :CMR# commands for AP mount
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

def test_cm_vs_cmr():
    """Test :CM# vs :CMR# commands"""
    
    print("=== AP Mount :CM# vs :CMR# Test ===\n")
    
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
    print("\n=== Initial Position ===")
    initial_ra = mount_api.mount.interface.send_command(":GR#")
    initial_dec = mount_api.mount.interface.send_command(":GD#")
    print(f"Initial RA: '{initial_ra}'")
    print(f"Initial DEC: '{initial_dec}'")
    
    # Test coordinates to set
    test_ra = "19:02:18"
    test_dec = "+32:45:17"
    
    print(f"\n=== Testing with :CM# (Initial Calibration) ===")
    print(f"Setting coordinates to RA: {test_ra}, DEC: {test_dec}")
    
    # Set coordinates
    ra_response = mount_api.mount.interface.send_command(f":Sr{test_ra}#")
    dec_response = mount_api.mount.interface.send_command(f":Sd{test_dec}#")
    print(f"RA set response: '{ra_response}'")
    print(f"DEC set response: '{dec_response}'")
    
    if ra_response == "1" and dec_response == "1":
        print("✅ Coordinates set successfully")
        
        # Try :CM# (initial calibration)
        print("\nSending :CM# (initial calibration)...")
        cm_response = mount_api.mount.interface.send_command(":CM#")
        print(f":CM# response: '{cm_response}'")
        
        # Wait a moment
        time.sleep(2)
        
        # Check new position
        new_ra = mount_api.mount.interface.send_command(":GR#")
        new_dec = mount_api.mount.interface.send_command(":GD#")
        print(f"New RA: '{new_ra}'")
        print(f"New DEC: '{new_dec}'")
        
        # Check if position changed
        if new_ra != initial_ra or new_dec != initial_dec:
            print("✅ Position changed after :CM#!")
        else:
            print("❌ Position did NOT change after :CM#")
    else:
        print("❌ Failed to set coordinates")
    
    # Wait a bit
    time.sleep(3)
    
    # Test with :CMR# (re-calibration)
    print(f"\n=== Testing with :CMR# (Re-calibration) ===")
    print(f"Setting coordinates to RA: {test_ra}, DEC: {test_dec}")
    
    # Set coordinates again
    ra_response = mount_api.mount.interface.send_command(f":Sr{test_ra}#")
    dec_response = mount_api.mount.interface.send_command(f":Sd{test_dec}#")
    print(f"RA set response: '{ra_response}'")
    print(f"DEC set response: '{dec_response}'")
    
    if ra_response == "1" and dec_response == "1":
        print("✅ Coordinates set successfully")
        
        # Try :CMR# (re-calibration)
        print("\nSending :CMR# (re-calibration)...")
        cmr_response = mount_api.mount.interface.send_command(":CMR#")
        print(f":CMR# response: '{cmr_response}'")
        
        # Wait a moment
        time.sleep(2)
        
        # Check new position
        final_ra = mount_api.mount.interface.send_command(":GR#")
        final_dec = mount_api.mount.interface.send_command(":GD#")
        print(f"Final RA: '{final_ra}'")
        print(f"Final DEC: '{final_dec}'")
        
        # Check if position changed
        if final_ra != new_ra or final_dec != new_dec:
            print("✅ Position changed after :CMR#!")
        else:
            print("❌ Position did NOT change after :CMR#")
    else:
        print("❌ Failed to set coordinates")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_cm_vs_cmr()
