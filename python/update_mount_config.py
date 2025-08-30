#!/usr/bin/python3
"""
Script to update mount configuration with correct IP address
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'PiFinder'))

from PiFinder import config
import json

def update_mount_config():
    """Update mount configuration with correct IP"""
    
    print("=== Updating Mount Configuration ===\n")
    
    # Load current config
    cfg = config.Config()
    current_config = cfg.get_option("mount_control", {})
    
    print(f"Current mount config: {current_config}")
    
    # Update with correct IP
    updated_config = current_config.copy()
    updated_config.update({
        "host": "192.168.1.182",
        "port": 23
    })
    
    print(f"Updated mount config: {updated_config}")
    
    # Save the updated config
    cfg.set_option("mount_control", updated_config)
    
    print("\n✅ Mount configuration updated successfully!")
    print("   Host: 192.168.1.182")
    print("   Port: 23")
    print("\nPlease restart PiFinder for changes to take effect.")

if __name__ == "__main__":
    update_mount_config()
