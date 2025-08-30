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

class AstroPhysicsMount:
    """Wrapper class for AstroPhysicsInterface to provide mount-specific methods"""
    
    def __init__(self, host: str = "192.168.1.100", port: int = 23):
        self.host = host
        self.port = port
        self.interface = astro_physics_comm.AstroPhysicsInterface(host=host, port=port)
        self.connected = False
        
    def test_connection(self) -> bool:
        """Test if we can connect to the mount"""
        try:
            self.interface.connect()
            self.connected = True
            # Test with a simple command
            response = self.interface.send_command(":GR#")  # Get RA
            logger.info(f"Mount connection test successful: {response}")
            return True
        except Exception as e:
            logger.error(f"Mount connection test failed: {e}")
            self.connected = False
            return False
    
    def get_position(self) -> Optional[Tuple[float, float]]:
        """Get current mount position (RA, Dec) in degrees"""
        if not self.connected:
            return None
            
        try:
            # Get RA and Dec from mount
            ra_response = self.interface.send_command(":GR#")  # Get RA
            dec_response = self.interface.send_command(":GD#")  # Get Dec
            
            # Parse responses (format: HH:MM:SS# for RA, sDD:MM:SS# for Dec)
            ra_deg = self._parse_ra(ra_response)
            dec_deg = self._parse_dec(dec_response)
            
            if ra_deg is not None and dec_deg is not None:
                return (ra_deg, dec_deg)
            return None
            
        except Exception as e:
            logger.error(f"Error getting mount position: {e}")
            return None
    
    def sync_to_position(self, ra_deg: float, dec_deg: float) -> bool:
        """Sync mount to specified position"""
        if not self.connected:
            logger.warning("Cannot sync: mount not connected")
            return False
            
        try:
            # Convert degrees to mount format (HH:MM:SS and sDD:MM:SS)
            ra_str = self._degrees_to_ra(ra_deg)
            dec_str = self._degrees_to_dec(dec_deg)
            
            # Send sync command
            response = self.interface.send_command(f":CS{ra_str},{dec_str}#")
            
            # Check if sync was successful
            if response and "1" in response:
                logger.info(f"Sync successful to RA: {ra_str}, DEC: {dec_str}")
                return True
            else:
                logger.warning(f"Sync failed: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error syncing mount: {e}")
            return False
    
    def slew_to_position(self, ra_deg: float, dec_deg: float) -> bool:
        """Slew mount to specified position"""
        if not self.connected:
            logger.warning("Cannot slew: mount not connected")
            return False
            
        try:
            # Convert degrees to mount format
            ra_str = self._degrees_to_ra(ra_deg)
            dec_str = self._degrees_to_dec(dec_deg)
            
            # Send slew command
            response = self.interface.send_command(f":MS{ra_str},{dec_str}#")
            
            # Check if slew was successful
            if response and "1" in response:
                logger.info(f"Slew started to RA: {ra_str}, DEC: {dec_str}")
                return True
            else:
                logger.warning(f"Slew failed: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error slewing mount: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get mount status information"""
        if not self.connected:
            return {
                "connected": False,
                "mount_type": "astro_physics",
                "host": self.host,
                "port": self.port,
                "error": "Mount not connected"
            }
            
        try:
            # Get various status information
            tracking = self.interface.send_command(":ST#")  # Get tracking status
            slewing = self.interface.send_command(":MS#")   # Get slew status
            
            status = {
                "connected": True,
                "mount_type": "astro_physics",
                "host": self.host,
                "port": self.port,
                "tracking": tracking.strip('#') if tracking else "Unknown",
                "slewing": slewing.strip('#') if slewing else "Unknown"
            }
            
            # Get current position if available
            position = self.get_position()
            if position:
                status["ra_deg"] = position[0]
                status["dec_deg"] = position[1]
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting mount status: {e}")
            return {
                "connected": False,
                "mount_type": "astro_physics",
                "host": self.host,
                "port": self.port,
                "error": str(e)
            }
    
    def disconnect(self):
        """Disconnect from mount"""
        if self.interface:
            try:
                self.interface.close()
            except Exception as e:
                logger.error(f"Error disconnecting mount: {e}")
            finally:
                self.connected = False
    
    def _parse_ra(self, ra_str: str) -> Optional[float]:
        """Parse RA string (HH:MM:SS#) to degrees"""
        try:
            if not ra_str or '#' not in ra_str:
                return None
            ra_str = ra_str.strip('#')
            parts = ra_str.split(':')
            if len(parts) == 3:
                hours = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])
                return (hours + minutes/60 + seconds/3600) * 15  # Convert to degrees
            return None
        except Exception as e:
            logger.error(f"Error parsing RA '{ra_str}': {e}")
            return None
    
    def _parse_dec(self, dec_str: str) -> Optional[float]:
        """Parse Dec string (sDD:MM:SS#) to degrees"""
        try:
            if not dec_str or '#' not in dec_str:
                return None
            dec_str = dec_str.strip('#')
            sign = 1 if dec_str[0] != '-' else -1
            dec_str = dec_str.lstrip('+-')
            parts = dec_str.split(':')
            if len(parts) == 3:
                degrees = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])
                return sign * (degrees + minutes/60 + seconds/3600)
            return None
        except Exception as e:
            logger.error(f"Error parsing Dec '{dec_str}': {e}")
            return None
    
    def _degrees_to_ra(self, ra_deg: float) -> str:
        """Convert RA degrees to HH:MM:SS format"""
        hours = ra_deg / 15
        h = int(hours)
        m = int((hours - h) * 60)
        s = int(((hours - h) * 60 - m) * 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    
    def _degrees_to_dec(self, dec_deg: float) -> str:
        """Convert Dec degrees to sDD:MM:SS format"""
        sign = "+" if dec_deg >= 0 else "-"
        dec_deg = abs(dec_deg)
        d = int(dec_deg)
        m = int((dec_deg - d) * 60)
        s = int(((dec_deg - d) * 60 - m) * 60)
        return f"{sign}{d:02d}:{m:02d}:{s:02d}"

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
                self.mount = AstroPhysicsMount(
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
