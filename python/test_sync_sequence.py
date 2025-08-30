#!/usr/bin/python3
"""
Test script to debug sync sequence and coordinate updates
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

def test_sync_sequence():
    """Test sync sequence and coordinate updates"""
    
    print("=== Sync Sequence Test ===\n")
    
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
    
    # Test coordinates to sync to (simulating different plate solves)
    test_coordinates = [
        (285.22, 32.69),  # First plate solve
        (105.35, 49.69),  # Second plate solve
        (180.0, 0.0),     # Third plate solve
    ]
    
    for i, (ra_deg, dec_deg) in enumerate(test_coordinates, 1):
        print(f"\n=== Test {i}: Syncing to RA={ra_deg:.2f}°, DEC={dec_deg:.2f}° ===")
        
        # Get mount position before sync
        print("Getting mount position before sync...")
        position_before = mount_api.get_position()
        if position_before:
            ra_before, dec_before = position_before
            print(f"Mount position before: RA={ra_before:.2f}°, DEC={dec_before:.2f}°")
        else:
            print("❌ Could not get mount position before sync")
            continue
        
        # Perform sync
        print(f"Performing sync to RA={ra_deg:.2f}°, DEC={dec_deg:.2f}°...")
        success, message = mount_api.sync_to_position(ra_deg, dec_deg)
        print(f"Sync result: success={success}, message='{message}'")
        
        if success:
            # Wait a moment for mount to process
            time.sleep(2)
            
            # Get mount position after sync
            print("Getting mount position after sync...")
            position_after = mount_api.get_position()
            if position_after:
                ra_after, dec_after = position_after
                print(f"Mount position after: RA={ra_after:.2f}°, DEC={dec_after:.2f}°")
                
                # Check if coordinates changed
                ra_diff = abs(ra_after - ra_before)
                dec_diff = abs(dec_after - dec_before)
                print(f"Coordinate change: RA diff={ra_diff:.2f}°, DEC diff={dec_diff:.2f}°")
                
                if ra_diff > 0.1 or dec_diff > 0.1:
                    print("✅ Mount coordinates changed significantly")
                else:
                    print("⚠️  Mount coordinates didn't change much")
            else:
                print("❌ Could not get mount position after sync")
        else:
            print("❌ Sync failed")
        
        # Wait between tests
        time.sleep(3)
    
    # Clean up
    try:
        mount_api.close()
        print("\n✅ Test completed successfully")
    except Exception as e:
        print(f"❌ Error closing mount API: {e}")

if __name__ == "__main__":
    test_sync_sequence()
