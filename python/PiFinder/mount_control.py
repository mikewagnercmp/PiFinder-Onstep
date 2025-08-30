#!/usr/bin/python
# -*- coding:utf-8 -*-
# mypy: ignore-errors
"""
Mount Control API for PiFinder
Provides interface for controlling telescope mounts
"""

import logging
import time
from typing import Optional, Dict, Any, Tuple
from . import astro_physics_comm

logger = logging.getLogger(__name__)

class MountControlAPI:
    """API for controlling telescope mounts"""
    
    def __init__(self, mount_type: str = "astro_physics", host: str = "192.168.1.100", port: int = 23):
        self.mount_type = mount_type
        self.host = host
        self.port = port
        self.mount = None
        self.connection_status = False
        
        # Initialize mount connection
        self._init_mount()
    
    def _init_mount(self):
        """Initialize mount connection based on type"""
        try:
            if self.mount_type == "astro_physics":
                self.mount = astro_physics_comm.AstroPhysicsMount(
                    host=self.host,
                    port=self.port
                )
                # Test connection
                self.connection_status = self.mount.test_connection()
                if self.connection_status:
                    logger.info(f"Connected to Astro Physics mount at {self.host}:{self.port}")
                else:
                    logger.warning(f"Failed to connect to Astro Physics mount at {self.host}:{self.port}")
                    
            elif self.mount_type == "onstep":
                # TODO: Implement OnStep mount support
                logger.warning("OnStep mount support not yet implemented")
                self.connection_status = False
                
            else:
                logger.error(f"Unsupported mount type: {self.mount_type}")
                self.connection_status = False
                
        except Exception as e:
            logger.error(f"Error initializing mount: {e}")
            self.connection_status = False
    
    def get_position(self) -> Optional[Tuple[float, float]]:
        """Get current mount position (RA, Dec) in degrees"""
        if not self.mount or not self.connection_status:
            return None
            
        try:
            return self.mount.get_position()
        except Exception as e:
            logger.error(f"Error getting mount position: {e}")
            return None
    
    def sync_to_position(self, ra_deg: float, dec_deg: float) -> bool:
        """Sync mount to specified position"""
        if not self.mount or not self.connection_status:
            logger.warning("Cannot sync: mount not connected")
            return False
            
        try:
            return self.mount.sync_to_position(ra_deg, dec_deg)
        except Exception as e:
            logger.error(f"Error syncing mount: {e}")
            return False
    
    def slew_to_position(self, ra_deg: float, dec_deg: float) -> bool:
        """Slew mount to specified position"""
        if not self.mount or not self.connection_status:
            logger.warning("Cannot slew: mount not connected")
            return False
            
        try:
            return self.mount.slew_to_position(ra_deg, dec_deg)
        except Exception as e:
            logger.error(f"Error slewing mount: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get mount status information"""
        if not self.mount or not self.connection_status:
            return {
                "connected": False,
                "mount_type": self.mount_type,
                "host": self.host,
                "port": self.port,
                "error": "Mount not connected"
            }
            
        try:
            status = self.mount.get_status()
            status.update({
                "connected": True,
                "mount_type": self.mount_type,
                "host": self.host,
                "port": self.port
            })
            return status
        except Exception as e:
            logger.error(f"Error getting mount status: {e}")
            return {
                "connected": False,
                "mount_type": self.mount_type,
                "host": self.host,
                "port": self.port,
                "error": str(e)
            }
    
    def disconnect(self):
        """Disconnect from mount"""
        if self.mount:
            try:
                self.mount.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting mount: {e}")
            finally:
                self.mount = None
                self.connection_status = False
