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
        self.initial_calibration_done = False  # Track if :CM# has been used this session
        
    def test_connection(self) -> bool:
        """Test if we can connect to the mount"""
        try:
            self.interface.connect()
            self.connected = True
            
            # Wait for mount to initialize and get valid coordinates
            import time
            max_retries = 5
            retry_delay = 1.0
            
            for attempt in range(max_retries):
                # Test with a simple command
                response = self.interface.send_command(":GR#")  # Get RA
                logger.info(f"Mount connection test attempt {attempt + 1}: {response}")
                
                # Check if we got valid coordinates (not 00:00:00)
                if response and response != "00:00:00#" and "00:00:00" not in response:
                    logger.info(f"Mount connection test successful: {response}")
                    # Reset calibration state on new connection
                    self.initial_calibration_done = False
                    logger.info("Reset initial calibration state - ready for :CM#")
                    return True
                else:
                    logger.info(f"Mount still initializing (attempt {attempt + 1}/{max_retries}), waiting {retry_delay}s...")
                    if attempt < max_retries - 1:  # Don't sleep on last attempt
                        time.sleep(retry_delay)
            
            # If we get here, mount didn't provide valid coordinates
            logger.warning("Mount connection test failed: mount did not provide valid coordinates after initialization")
            self.connected = False
            return False
            
        except Exception as e:
            logger.error(f"Mount connection test failed: {e}")
            self.connected = False
            return False
    
    def attempt_reconnection(self) -> bool:
        """Attempt to reconnect to the mount"""
        logger.info("Attempting to reconnect to mount...")
        try:
            # Close existing connection
            if hasattr(self, 'interface') and self.interface:
                self.interface.close()
            
            # Reinitialize the interface
            from PiFinder import tcp_interface
            self.interface = tcp_interface.TCPInterface(self.host, self.port)
            
            # Test the new connection
            return self.test_connection()
            
        except Exception as e:
            logger.error(f"Failed to reconnect to mount: {e}")
            self.connected = False
            return False
    
    def get_position(self) -> Optional[Tuple[float, float]]:
        """Get current mount position (RA, Dec) in degrees"""
        if not self.connected:
            logger.warning("Cannot get position: mount not connected")
            return None
            
        try:
            # Get RA and Dec from mount
            ra_response = self.interface.send_command(":GR#")  # Get RA
            dec_response = self.interface.send_command(":GD#")  # Get Dec
            
            # Debug: log raw responses
            logger.debug(f"Mount responses - RA: '{ra_response}', DEC: '{dec_response}'")
            
            # Check for invalid/initializing coordinates
            if ra_response == "00:00:00#" or "00:00:00" in ra_response:
                logger.debug("Mount returning invalid RA coordinates (00:00:00), mount may still be initializing")
                return None
            
            # Parse responses (format: HH:MM:SS# for RA, sDD:MM:SS# for Dec)
            ra_deg = self._parse_ra(ra_response)
            dec_deg = self._parse_dec(dec_response)
            
            if ra_deg is not None and dec_deg is not None:
                return (ra_deg, dec_deg)
            else:
                logger.warning(f"Failed to parse coordinates - RA: {ra_deg}, DEC: {dec_deg}")
                return None
            
        except Exception as e:
            logger.error(f"Error getting mount position: {e}")
            # Mark as disconnected on communication error
            self.connected = False
            return None
    
    def sync_to_position(self, ra_deg: float, dec_deg: float) -> tuple[bool, str]:
        """Sync mount to specified position"""
        if not self.connected:
            logger.warning("Cannot sync: mount not connected")
            return False, "Mount not connected"
            
        try:
            # PiFinder plate solve coordinates are in J2000 epoch
            # Astro Physics mounts typically use current epoch
            # Convert from J2000 to current epoch if needed
            from PiFinder.calc_utils import sf_utils
            from datetime import datetime
            
            # Get current datetime for epoch conversion
            from datetime import timezone
            current_dt = datetime.now(timezone.utc)
            logger.info(f"Mount sync: Current datetime: {current_dt}")
            
            # Convert from J2000 to current epoch
            from skyfield.positionlib import position_of_radec
            _p = position_of_radec(ra_hours=ra_deg/15.0, dec_degrees=dec_deg, epoch=sf_utils.ts.J2000)
            current_ra_h, current_dec, _ = _p.radec(epoch=sf_utils.ts.from_datetime(current_dt))
            
            # Convert to degrees
            current_ra_deg = current_ra_h._degrees
            current_dec_deg = current_dec.degrees
            
            logger.info(f"Mount sync: J2000 coordinates: {ra_deg:.6f}°, {dec_deg:.6f}°")
            logger.info(f"Mount sync: Current epoch coordinates: {current_ra_deg:.6f}°, {current_dec_deg:.6f}°")
            
            # Get mount's current sidereal time to understand coordinate interpretation
            mount_sidereal = self.interface.send_command(":GS#")
            mount_local = self.interface.send_command(":GL#")
            mount_timezone = self.interface.send_command(":GG#")
            
            logger.info(f"Mount sync: Mount sidereal time: '{mount_sidereal}'")
            logger.info(f"Mount sync: Mount local time: '{mount_local}'")
            logger.info(f"Mount sync: Mount timezone offset: '{mount_timezone}'")
            
            # Convert degrees to mount format (HH:MM:SS and sDD:MM:SS)
            # Convert to mount format without 12-hour offset
            ra_str = self._degrees_to_ra(current_ra_deg)
            dec_str = self._degrees_to_dec(current_dec_deg)
            
            logger.info(f"Mount sync: converting {current_ra_deg:.6f}°, {current_dec_deg:.6f}° to {ra_str}, {dec_str}")
            
            # Log the exact commands being sent
            ra_set_command = f":Sr{ra_str}#"
            dec_set_command = f":Sd{dec_str}#"
            logger.info(f"Mount sync: RA command: '{ra_set_command}'")
            logger.info(f"Mount sync: DEC command: '{dec_set_command}'")
            
            # Set the commanded coordinates first
            ra_set_command = f":Sr{ra_str}#"
            logger.info(f"Mount sync: setting RA with '{ra_set_command}'")
            ra_response = self.interface.send_command(ra_set_command)
            logger.info(f"Mount sync: RA set response '{ra_response}'")
            
            if ra_response != "1":
                logger.warning(f"Failed to set RA: {ra_response}")
                return False, f"Failed to set RA: {ra_response}"
            
            dec_set_command = f":Sd{dec_str}#"
            logger.info(f"Mount sync: setting DEC with '{dec_set_command}'")
            dec_response = self.interface.send_command(dec_set_command)
            logger.info(f"Mount sync: DEC set response '{dec_response}'")
            
            if dec_response != "1":
                logger.warning(f"Failed to set DEC: {dec_response}")
                return False, f"Failed to set DEC: {dec_response}"
            
            # Note: :GR# and :GD# return current position, not commanded position
            # The mount should have received our commanded coordinates via :Sr and :Sd
            logger.info("Mount sync: Commanded coordinates set via :Sr and :Sd")
            
            # Choose sync command based on whether initial calibration has been done
            if not self.initial_calibration_done:
                sync_command = ":CM#"
                logger.info(f"Mount sync: sending initial calibration command '{sync_command}'")
            else:
                sync_command = ":CMR#"
                logger.info(f"Mount sync: sending re-calibration command '{sync_command}'")
            
            response = self.interface.send_command(sync_command)
            logger.info(f"Mount sync: received response '{response}'")
            
            # Check if sync was successful - AP returns "Coordinates     Matched.        #"
            if response and "Matched" in response:
                logger.info(f"Sync successful to RA: {ra_str}, DEC: {dec_str}")
                
                # Wait for mount to settle after sync
                import time
                time.sleep(0.5)
                
                # Check if mount position updated
                new_position = self.get_position()
                if new_position:
                    new_ra, new_dec = new_position
                    logger.info(f"Mount position after sync: RA={new_ra:.2f}°, DEC={new_dec:.2f}°")
                    
                    # Check if position changed significantly
                    # Check if mount position changed significantly
                    # Note: mount position is in current epoch, but ra_deg/dec_deg are in J2000
                    # Convert mount position to J2000 for comparison
                    mount_p = position_of_radec(ra_hours=new_ra/15.0, dec_degrees=new_dec, epoch=sf_utils.ts.from_datetime(current_dt))
                    mount_ra_j2000, mount_dec_j2000, _ = mount_p.radec(epoch=sf_utils.ts.J2000)
                    mount_ra_j2000_deg = mount_ra_j2000._degrees
                    mount_dec_j2000_deg = mount_dec_j2000.degrees
                    
                    logger.info(f"Mount sync: Mount position (current epoch): RA={new_ra:.2f}°, DEC={new_dec:.2f}°")
                    logger.info(f"Mount sync: Mount position (J2000): RA={mount_ra_j2000_deg:.2f}°, DEC={mount_dec_j2000_deg:.2f}°")
                    
                    ra_diff = abs(mount_ra_j2000_deg - ra_deg)
                    dec_diff = abs(mount_dec_j2000_deg - dec_deg)
                    if ra_diff > 1.0 or dec_diff > 1.0:
                        logger.warning(f"Mount position did not update properly after sync!")
                        logger.warning(f"Expected (J2000): RA={ra_deg:.2f}°, DEC={dec_deg:.2f}°")
                        logger.warning(f"Actual (J2000): RA={mount_ra_j2000_deg:.2f}°, DEC={mount_dec_j2000_deg:.2f}°")
                    else:
                        logger.info(f"Mount position updated correctly! Difference: RA={ra_diff:.2f}°, DEC={dec_diff:.2f}°")
                
                return True, "Sync successful"
            else:
                logger.warning(f"Sync failed: {response}")
                return False, f"Sync failed: {response}"
                
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
        """Parse RA string (HH:MM:SS# or HH:MM.M#) to degrees"""
        try:
            if not ra_str or '#' not in ra_str:
                return None
            ra_str = ra_str.strip('#')
            
            # Handle HH:MM.M format (decimal minutes)
            if '.' in ra_str:
                parts = ra_str.split(':')
                if len(parts) == 2:
                    hours = float(parts[0])
                    minutes = float(parts[1])
                    return (hours + minutes/60) * 15  # Convert to degrees
            
            # Handle HH:MM:SS format
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
        """Parse Dec string (sDD:MM:SS# or sDD*MM:SS#) to degrees"""
        try:
            if not dec_str or '#' not in dec_str:
                return None
            dec_str = dec_str.strip('#')
            sign = 1 if dec_str[0] != '-' else -1
            dec_str = dec_str.lstrip('+-')
            
            # Handle DD*MM:SS format (asterisk separator)
            if '*' in dec_str:
                parts = dec_str.split('*')
                if len(parts) == 2:
                    degrees = float(parts[0])
                    mm_ss = parts[1].split(':')
                    if len(mm_ss) == 2:
                        minutes = float(mm_ss[0])
                        seconds = float(mm_ss[1])
                        return sign * (degrees + minutes/60 + seconds/3600)
            
            # Handle DD:MM:SS format (colon separator)
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
        """Convert Dec degrees to sDD*MM:SS format (Astro Physics LX200 format)"""
        sign = "+" if dec_deg >= 0 else "-"
        dec_deg = abs(dec_deg)
        d = int(dec_deg)
        m = int((dec_deg - d) * 60)
        s = int(((dec_deg - d) * 60 - m) * 60)
        return f"{sign}{d:02d}*{m:02d}:{s:02d}"
    
    def format_coordinates(self, ra_deg: float, dec_deg: float) -> tuple[str, str]:
        """Format coordinates for display in Astro Physics format (HH:MM:SS, sDD:MM:SS)"""
        if ra_deg is None or dec_deg is None:
            return "N/A", "N/A"
        
        # Convert RA degrees to HH:MM:SS
        ra_hours = ra_deg / 15
        ra_h = int(ra_hours)
        ra_m = int((ra_hours - ra_h) * 60)
        ra_s = int(((ra_hours - ra_h) * 60 - ra_m) * 60)
        ra_str = f"{ra_h:02d}:{ra_m:02d}:{ra_s:02d}"
        
        # Convert DEC degrees to sDD:MM:SS
        dec_sign = "+" if dec_deg >= 0 else "-"
        dec_abs = abs(dec_deg)
        dec_d = int(dec_abs)
        dec_m = int((dec_abs - dec_d) * 60)
        dec_s = int(((dec_abs - dec_d) * 60 - dec_m) * 60)
        dec_str = f"{dec_sign}{dec_d:02d}:{dec_m:02d}:{dec_s:02d}"
        
        return ra_str, dec_str

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
    
    def format_coordinates(self, ra_deg: float, dec_deg: float) -> tuple[str, str]:
        """Format coordinates for display in mount-specific format"""
        if not self.mount or not self.connection_status:
            return "N/A", "N/A"
        return self.mount.format_coordinates(ra_deg, dec_deg)
    
    def sync_to_position(self, ra_deg: float, dec_deg: float) -> tuple[bool, str]:
        """Sync mount to specified position"""
        if not self.mount or not self.connection_status:
            logger.warning("Cannot sync: mount not connected")
            return False, "Mount not connected"
            
        try:
            return self.mount.sync_to_position(ra_deg, dec_deg)
        except Exception as e:
            logger.error(f"Error syncing mount: {e}")
            return False, f"Error: {e}"
    
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
    
    def close(self):
        """Close the mount connection"""
        self.disconnect()
    
    def attempt_reconnection(self) -> bool:
        """Attempt to reconnect to the mount"""
        logger.info("MountControlAPI: Attempting to reconnect...")
        try:
            # Close existing connection
            self.disconnect()
            
            # Reinitialize mount connection
            self._init_mount()
            
            if self.mount and self.connection_status:
                logger.info("MountControlAPI: Successfully reconnected")
                return True
            else:
                logger.warning("MountControlAPI: Failed to reconnect")
                return False
                
        except Exception as e:
            logger.error(f"MountControlAPI: Error during reconnection: {e}")
            return False
