#!/usr/bin/python3
"""
Test script to find correct AP mount commands for coordinate setting and syncing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'PiFinder'))

from PiFinder import mount_control
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ap_commands():
    """Test various AP mount commands"""
    
    print("=== AP Mount Commands Test ===\n")
    
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
    
    # Test various commands
    commands_to_test = [
        ":GR#",      # Get RA
        ":GD#",      # Get DEC
        ":ST#",      # Get tracking status
        ":MS#",      # Get slew status
        ":CM#",      # Calibrate mount
        ":CMR#",     # Re-calibrate mount
        ":Sr00:00:00#",  # Set RA (try setting to 00:00:00)
        ":Sd+90:00:00#", # Set DEC (try setting to +90:00:00)
        ":CS00:00:00,+90:00:00#",  # Try the original sync command
    ]
    
    for command in commands_to_test:
        print(f"\nTesting command: '{command}'")
        try:
            response = mount_api.mount.interface.send_command(command)
            print(f"Response: '{response}'")
            
            if response:
                if "Coordinates matched" in response:
                    print("✅ Command successful (sync)")
                elif "1" in response:
                    print("✅ Command successful (1)")
                elif "0" in response:
                    print("⚠️  Command returned 0")
                else:
                    print("ℹ️  Command executed")
            else:
                print("❌ No response")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test the sync sequence
    print("\n=== Testing Sync Sequence ===")
    try:
        # First set the coordinates
        print("Setting RA to 00:00:00...")
        ra_response = mount_api.mount.interface.send_command(":Sr00:00:00#")
        print(f"RA set response: '{ra_response}'")
        
        print("Setting DEC to +90:00:00...")
        dec_response = mount_api.mount.interface.send_command(":Sd+90:00:00#")
        print(f"DEC set response: '{dec_response}'")
        
        # Then sync
        print("Sending sync command...")
        sync_response = mount_api.mount.interface.send_command(":CMR#")
        print(f"Sync response: '{sync_response}'")
        
        if "Coordinates matched" in sync_response:
            print("✅ Sync sequence successful!")
        else:
            print("❌ Sync sequence failed")
            
    except Exception as e:
        print(f"❌ Error in sync sequence: {e}")
    
    # Clean up
    try:
        mount_api.close()
        print("\n✅ Test completed successfully")
    except Exception as e:
        print(f"❌ Error closing mount API: {e}")

if __name__ == "__main__":
    test_ap_commands()
