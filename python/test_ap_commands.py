#!/usr/bin/python3
"""
Test various AP mount commands
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
        ":GR#",   # Get RA (current position)
        ":GD#",   # Get DEC (current position)
        ":GX#",   # Get extended status
        ":GX00#", # Get extended status 00
        ":GX01#", # Get extended status 01
        ":GX02#", # Get extended status 02
        ":GX03#", # Get extended status 03
        ":GX04#", # Get extended status 04
        ":GX05#", # Get extended status 05
        ":GX06#", # Get extended status 06
        ":GX07#", # Get extended status 07
        ":GX08#", # Get extended status 08
        ":GX09#", # Get extended status 09
        ":GX0A#", # Get extended status 0A
        ":GX0B#", # Get extended status 0B
        ":GX0C#", # Get extended status 0C
        ":GX0D#", # Get extended status 0D
        ":GX0E#", # Get extended status 0E
        ":GX0F#", # Get extended status 0F
        ":GX10#", # Get extended status 10
        ":GX11#", # Get extended status 11
        ":GX12#", # Get extended status 12
        ":GX13#", # Get extended status 13
        ":GX14#", # Get extended status 14
        ":GX15#", # Get extended status 15
        ":GX16#", # Get extended status 16
        ":GX17#", # Get extended status 17
        ":GX18#", # Get extended status 18
        ":GX19#", # Get extended status 19
        ":GX1A#", # Get extended status 1A
        ":GX1B#", # Get extended status 1B
        ":GX1C#", # Get extended status 1C
        ":GX1D#", # Get extended status 1D
        ":GX1E#", # Get extended status 1E
        ":GX1F#", # Get extended status 1F
        ":GX20#", # Get extended status 20
        ":GX21#", # Get extended status 21
        ":GX22#", # Get extended status 22
        ":GX23#", # Get extended status 23
        ":GX24#", # Get extended status 24
        ":GX25#", # Get extended status 25
        ":GX26#", # Get extended status 26
        ":GX27#", # Get extended status 27
        ":GX28#", # Get extended status 28
        ":GX29#", # Get extended status 29
        ":GX2A#", # Get extended status 2A
        ":GX2B#", # Get extended status 2B
        ":GX2C#", # Get extended status 2C
        ":GX2D#", # Get extended status 2D
        ":GX2E#", # Get extended status 2E
        ":GX2F#", # Get extended status 2F
        ":GX30#", # Get extended status 30
        ":GX31#", # Get extended status 31
        ":GX32#", # Get extended status 32
        ":GX33#", # Get extended status 33
        ":GX34#", # Get extended status 34
        ":GX35#", # Get extended status 35
        ":GX36#", # Get extended status 36
        ":GX37#", # Get extended status 37
        ":GX38#", # Get extended status 38
        ":GX39#", # Get extended status 39
        ":GX3A#", # Get extended status 3A
        ":GX3B#", # Get extended status 3B
        ":GX3C#", # Get extended status 3C
        ":GX3D#", # Get extended status 3D
        ":GX3E#", # Get extended status 3E
        ":GX3F#", # Get extended status 3F
    ]
    
    for command in commands_to_test:
        print(f"\n--- Testing command: {command} ---")
        response = mount_api.mount.interface.send_command(command)
        print(f"Response: '{response}'")
        time.sleep(0.1)  # Small delay between commands
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_ap_commands()
