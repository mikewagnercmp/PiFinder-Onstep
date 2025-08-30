#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Mount Polling Service for PiFinder
Continuously polls mount coordinates and stores them in shared state
"""

import time
import logging
import threading
from typing import Optional, Tuple
from queue import Queue

from PiFinder import mount_control
from PiFinder import config

logger = logging.getLogger(__name__)

class MountPoller:
    """
    Background service that polls mount coordinates at regular intervals
    """
    
    def __init__(self, shared_state, poll_interval: float = 2.0):
        self.shared_state = shared_state
        self.poll_interval = poll_interval
        self.running = False
        self.thread = None
        self.mount_api = None
        self._init_mount_control()
        
    def _init_mount_control(self):
        """Initialize mount control if available"""
        try:
            # Get mount configuration
            mount_config = config.Config().get_option("mount_control", {})
            if mount_config and mount_config.get("mount_type"):
                self.mount_api = mount_control.MountControlAPI(
                    mount_type=mount_config.get("mount_type", "astro_physics"),
                    host=mount_config.get("host", "192.168.1.100"),
                    port=mount_config.get("port", 23)
                )
                logger.info("Mount poller initialized")
            else:
                logger.warning("No mount control configuration found for poller")
                
        except Exception as e:
            logger.error(f"Failed to initialize mount poller: {e}")
            self.mount_api = None
    
    def start(self):
        """Start the polling thread"""
        if self.running:
            logger.warning("Mount poller already running")
            return
            
        if not self.mount_api:
            logger.warning("No mount API available, poller not started")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
        logger.info("Mount poller started")
        
    def stop(self):
        """Stop the polling thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        logger.info("Mount poller stopped")
        
    def _poll_loop(self):
        """Main polling loop"""
        while self.running:
            try:
                if self.mount_api and self.mount_api.mount and self.mount_api.mount.connected:
                    # Get current mount position
                    mount_ra, mount_dec = self.mount_api.get_position()
                    
                    if mount_ra is not None and mount_dec is not None:
                        # Store in shared state
                        self.shared_state.set_mount_position((mount_ra, mount_dec))
                        logger.debug(f"Mount position updated: RA={mount_ra:.2f}°, DEC={mount_dec:.2f}°")
                    else:
                        # Clear mount position if not available
                        self.shared_state.set_mount_position(None)
                        logger.debug("Mount position not available")
                else:
                    # Clear mount position if not connected
                    self.shared_state.set_mount_position(None)
                    logger.debug("Mount not connected")
                    
            except Exception as e:
                logger.error(f"Error polling mount position: {e}")
                self.shared_state.set_mount_position(None)
                
            # Wait for next poll
            time.sleep(self.poll_interval)
            
    def close(self):
        """Clean up resources"""
        self.stop()
        if self.mount_api:
            self.mount_api.close()


def mount_poller_service(shared_state, poll_interval: float = 2.0):
    """
    Service function to run mount poller in a separate process
    """
    poller = MountPoller(shared_state, poll_interval)
    poller.start()
    
    try:
        # Keep the service running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        poller.close()
