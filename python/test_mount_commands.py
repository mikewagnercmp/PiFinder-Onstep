#!/usr/bin/python3
"""
Test script to debug mount communication
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

def test_mount_connection():
    """Test basic mount connection and commands"""
    
    print("=== Mount Communication Test ===\n")
    
    # Get mount configuration
    mount_config = config.Config().get_option("mount_control", {})
    print(f"Mount config: {mount_config}")
    
    if not mount_config or not mount_config.get("mount_type"):
        print("❌ No mount configuration found!")
        return
    
    # Try with configured settings first
    print(f"\n=== Testing with configured settings ===")
    print(f"Host: {mount_config.get('host')}, Port: {mount_config.get('port')}")
    
    # Create mount API with configured settings
    try:
        mount_api = mount_control.MountControlAPI(
            mount_type=mount_config.get("mount_type", "astro_physics"),
            host=mount_config.get("host", "192.168.1.100"),
            port=mount_config.get("port", 23)
        )
        print(f"✅ Mount API created for {mount_config.get('mount_type')} at {mount_config.get('host')}:{mount_config.get('port')}")
    except Exception as e:
        print(f"❌ Failed to create mount API: {e}")
        return
    
    # Test connection
    if not mount_api.mount or not mount_api.mount.connected:
        print("❌ Mount not connected with configured settings!")
        
        # Try with the IP we saw in the logs
        print(f"\n=== Testing with IP from logs (192.168.1.182:23) ===")
        try:
            mount_api = mount_control.MountControlAPI(
                mount_type="astro_physics",
                host="192.168.1.182",
                port=23
            )
            print(f"✅ Mount API created for astro_physics at 192.168.1.182:23")
        except Exception as e:
            print(f"❌ Failed to create mount API with log IP: {e}")
            return
        
        if not mount_api.mount or not mount_api.mount.connected:
            print("❌ Mount not connected with log IP either!")
            return
    else:
        print("✅ Mount is connected with configured settings!")
    
    print("✅ Mount is connected!")
    
    # Test basic commands
    print("\n=== Testing Basic Commands ===")
    
    try:
        # Test RA command
        print("\nTesting :GR# (Get RA)...")
        ra_response = mount_api.mount.interface.send_command(":GR#")
        print(f"RA Response: '{ra_response}'")
        
        # Test DEC command
        print("\nTesting :GD# (Get DEC)...")
        dec_response = mount_api.mount.interface.send_command(":GD#")
        print(f"DEC Response: '{dec_response}'")
        
        # Test tracking status
        print("\nTesting :ST# (Get tracking status)...")
        tracking_response = mount_api.mount.interface.send_command(":ST#")
        print(f"Tracking Response: '{tracking_response}'")
        
        # Test slew status
        print("\nTesting :MS# (Get slew status)...")
        slew_response = mount_api.mount.interface.send_command(":MS#")
        print(f"Slew Response: '{slew_response}'")
        
    except Exception as e:
        print(f"❌ Error testing commands: {e}")
        return
    
    # Test get_position method
    print("\n=== Testing get_position() ===")
    try:
        position = mount_api.get_position()
        print(f"get_position() result: {position}")
        
        if position:
            ra_deg, dec_deg = position
            print(f"✅ Successfully got position: RA={ra_deg:.2f}°, DEC={dec_deg:.2f}°")
        else:
            print("❌ get_position() returned None")
            
    except Exception as e:
        print(f"❌ Error in get_position(): {e}")
    
    # Test parsing methods directly
    print("\n=== Testing Parsing Methods ===")
    try:
        if ra_response and dec_response:
            ra_deg = mount_api.mount._parse_ra(ra_response)
            dec_deg = mount_api.mount._parse_dec(dec_response)
            print(f"Parsed RA: {ra_deg}")
            print(f"Parsed DEC: {dec_deg}")
        else:
            print("❌ No responses to parse")
            
    except Exception as e:
        print(f"❌ Error parsing coordinates: {e}")
    
    # Clean up
    try:
        mount_api.close()
        print("\n✅ Test completed successfully")
    except Exception as e:
        print(f"❌ Error closing mount API: {e}")

if __name__ == "__main__":
    test_mount_connection()
