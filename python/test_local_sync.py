#!/usr/bin/python3
"""
Test mount sync locally with coordinates close to current position
Current mount: RA=2h28m, DEC=89°
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

def test_local_sync():
    """Test sync with coordinates close to current mount position"""
    
    print("=== Local Mount Sync Test ===\n")
    
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
    initial_position = mount_api.get_position()
    if initial_position:
        initial_ra, initial_dec = initial_position
        print(f"Initial RA: {initial_ra:.2f}° ({initial_ra/15:.2f}h)")
        print(f"Initial DEC: {initial_dec:.2f}°")
    else:
        print("❌ Could not get initial position")
        return
    
    # Test coordinates close to current position
    # Current: RA=2h28m (37°), DEC=89°
    # Test with small offsets
    test_coordinates = [
        (37.0, 89.0),      # Exact current position
        (37.5, 89.0),      # +0.5° RA
        (36.5, 89.0),      # -0.5° RA
        (37.0, 88.5),      # -0.5° DEC
        (37.0, 89.5),      # +0.5° DEC (if possible)
    ]
    
    for i, (test_ra, test_dec) in enumerate(test_coordinates):
        print(f"\n=== Test {i+1}: RA={test_ra:.1f}°, DEC={test_dec:.1f}° ===")
        
        # Test with :CM# (initial calibration)
        print(f"Testing :CM# (initial calibration)...")
        success, message = mount_api.sync_to_position(test_ra, test_dec)
        print(f"Result: {success}, Message: {message}")
        
        if success:
            # Wait and check new position
            time.sleep(2)
            new_position = mount_api.get_position()
            if new_position:
                new_ra, new_dec = new_position
                ra_diff = abs(new_ra - test_ra)
                dec_diff = abs(new_dec - test_dec)
                print(f"New position: RA={new_ra:.2f}°, DEC={new_dec:.2f}°")
                print(f"Difference: RA diff={ra_diff:.2f}°, DEC diff={dec_diff:.2f}°")
                
                if ra_diff < 1.0 and dec_diff < 1.0:
                    print("✅ Sync successful - position matches target")
                else:
                    print("⚠️  Sync completed but position doesn't match target")
            else:
                print("❌ Could not get new position")
        
        # Wait between tests
        time.sleep(3)
        
        # Test with :CMR# (re-calibration) - we'll need to modify the code temporarily
        print(f"Testing :CMR# (re-calibration)...")
        # For this test, we'll manually send the commands to test :CMR#
        try:
            # Convert to mount format
            ra_str = mount_api.mount._degrees_to_ra(test_ra)
            dec_str = mount_api.mount._degrees_to_dec(test_dec)
            
            print(f"Sending RA: {ra_str}, DEC: {dec_str}")
            
            # Set coordinates
            ra_response = mount_api.mount.interface.send_command(f":Sr{ra_str}#")
            dec_response = mount_api.mount.interface.send_command(f":Sd{dec_str}#")
            print(f"RA set: '{ra_response}', DEC set: '{dec_response}'")
            
            if ra_response == "1" and dec_response == "1":
                # Send :CMR# command
                cmr_response = mount_api.mount.interface.send_command(":CMR#")
                print(f":CMR# response: '{cmr_response}'")
                
                if "Matched" in cmr_response:
                    print("✅ :CMR# sync successful")
                    
                    # Wait and check position
                    time.sleep(2)
                    final_position = mount_api.get_position()
                    if final_position:
                        final_ra, final_dec = final_position
                        ra_diff = abs(final_ra - test_ra)
                        dec_diff = abs(final_dec - test_dec)
                        print(f"Final position: RA={final_ra:.2f}°, DEC={final_dec:.2f}°")
                        print(f"Difference: RA diff={ra_diff:.2f}°, DEC diff={dec_diff:.2f}°")
                else:
                    print("❌ :CMR# sync failed")
            else:
                print("❌ Failed to set coordinates for :CMR#")
                
        except Exception as e:
            print(f"❌ Error testing :CMR#: {e}")
        
        # Wait between tests
        time.sleep(3)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_local_sync()
