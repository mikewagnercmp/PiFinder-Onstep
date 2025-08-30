#!/usr/bin/python
# -*- coding:utf-8 -*-
# mypy: ignore-errors
"""
Simple Sync UI Module for PiFinder
Allows users to sync the mount to PiFinder's current plate solve position
"""

from PiFinder.ui.base import UIModule
import logging
import time

logger = logging.getLogger(__name__)

class UISimpleSync(UIModule):
    """
    Simple Sync UI - Sync mount to current PiFinder position
    """

    __help_name__ = "simple_sync"
    __title__ = "SYNC"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Sync state
        self.sync_in_progress = False
        self.last_sync_time = None
        self.sync_result = None
        
        # Mount control
        self.mount_api = None
        self._init_mount_control()

    def _init_mount_control(self):
        """Initialize mount control if available"""
        try:
            from PiFinder import mount_control
            
            # Get mount configuration
            mount_config = self.config_object.get_option("mount_control", {})
            if mount_config and mount_config.get("mount_type"):
                self.mount_api = mount_control.MountControlAPI(
                    mount_type=mount_config.get("mount_type", "astro_physics"),
                    host=mount_config.get("host", "192.168.1.100"),
                    port=mount_config.get("port", 23)
                )
                logger.info("Mount control initialized for simple sync")
            else:
                logger.warning("No mount control configuration found")
                
        except Exception as e:
            logger.error(f"Failed to initialize mount control: {e}")
            self.mount_api = None

    def update(self, force=True):
        """Update the display"""
        logger.debug("Simple sync UI: update() called")
        
        # Clear Screen
        self.clear_screen()

        # Title (using smaller font to save space)
        self.draw.text(
            (10, 5),
            "MOUNT SYNC",
            font=self.fonts.base.font,
            fill=self.colors.get(255),
        )

        # Check if mount is available
        if not self.mount_api:
            self.draw.text(
                (10, 40),
                "No mount connected",
                font=self.fonts.base.font,
                fill=self.colors.get(128),
            )
            self.draw.text(
                (10, 60),
                "Check mount config",
                font=self.fonts.base.font,
                fill=self.colors.get(128),
            )
            return

        # Check if mount is connected
        if not self.mount_api.mount or not self.mount_api.mount.connected:
            self.draw.text(
                (10, 40),
                "Mount not connected",
                font=self.fonts.base.font,
                fill=self.colors.get(128),
            )
            return

        # Get current position from last plate solve
        solution = self.shared_state.solution()
        current_ra = None
        current_dec = None
        
        if solution:
            current_ra = solution.get("RA")
            current_dec = solution.get("Dec")

        # Get current mount position from shared state
        mount_position = self.shared_state.mount_position()
        mount_ra = None
        mount_dec = None
        
        if mount_position:
            mount_ra, mount_dec = mount_position
            logger.info(f"Simple sync UI: Got mount position RA={mount_ra:.2f}°, DEC={mount_dec:.2f}°")
        else:
            logger.warning("Simple sync UI: No mount position in shared state")
        
        # Log the coordinate comparison
        if current_ra is not None and current_dec is not None and mount_ra is not None and mount_dec is not None:
            ra_diff = abs(current_ra - mount_ra)
            dec_diff = abs(current_dec - mount_dec)
            logger.info(f"Simple sync UI: Coordinate diff - RA: {ra_diff:.2f}°, DEC: {dec_diff:.2f}°")
            if ra_diff > 1.0 or dec_diff > 1.0:
                logger.warning(f"Simple sync UI: Large coordinate difference detected!")
                
        # Log sync timing info
        if hasattr(self, 'last_sync_time') and self.last_sync_time:
            time_since_sync = time.time() - self.last_sync_time
            logger.info(f"Simple sync UI: Time since last sync: {time_since_sync:.1f}s")

        # Display coordinate headers (moved up to save space)
        self.draw.text(
            (10, 25),
            "Mount / Solved:",
            font=self.fonts.base.font,
            fill=self.colors.get(255),
        )

        # Display RA coordinates on separate lines
        ra_text = "RA: "
        if mount_ra is not None:
            # Convert RA degrees to HH:MM:SS
            ra_hours = mount_ra / 15
            ra_h = int(ra_hours)
            ra_m = int((ra_hours - ra_h) * 60)
            ra_s = int(((ra_hours - ra_h) * 60 - ra_m) * 60)
            ra_text += f"{ra_h:02d}:{ra_m:02d}:{ra_s:02d}"
        else:
            ra_text += "N/A"
            
        self.draw.text(
            (10, 40),
            ra_text,
            font=self.fonts.base.font,
            fill=self.colors.get(255),
        )

        # Display solved RA on next line (indented)
        solved_ra_text = "     "
        if current_ra is not None:
            # Convert RA degrees to HH:MM:SS
            ra_hours = current_ra / 15
            ra_h = int(ra_hours)
            ra_m = int((ra_hours - ra_h) * 60)
            ra_s = int(((ra_hours - ra_h) * 60 - ra_m) * 60)
            solved_ra_text += f"{ra_h:02d}:{ra_m:02d}:{ra_s:02d}"
        else:
            solved_ra_text += "N/A"
            
        self.draw.text(
            (10, 55),
            solved_ra_text,
            font=self.fonts.base.font,
            fill=self.colors.get(255),
        )

        # Display DEC coordinates on separate lines
        dec_text = "DEC: "
        if mount_dec is not None:
            # Convert DEC degrees to DD:MM:SS
            dec_sign = "+" if mount_dec >= 0 else "-"
            dec_abs = abs(mount_dec)
            dec_d = int(dec_abs)
            dec_m = int((dec_abs - dec_d) * 60)
            dec_s = int(((dec_abs - dec_d) * 60 - dec_m) * 60)
            dec_text += f"{dec_sign}{dec_d:02d}:{dec_m:02d}:{dec_s:02d}"
        else:
            dec_text += "N/A"
            
        self.draw.text(
            (10, 70),
            dec_text,
            font=self.fonts.base.font,
            fill=self.colors.get(255),
        )

        # Display solved DEC on next line (indented)
        solved_dec_text = "     "
        if current_dec is not None:
            # Convert DEC degrees to DD:MM:SS
            dec_sign = "+" if current_dec >= 0 else "-"
            dec_abs = abs(current_dec)
            dec_d = int(dec_abs)
            dec_m = int((dec_abs - dec_d) * 60)
            dec_s = int(((dec_abs - dec_d) * 60 - dec_m) * 60)
            solved_dec_text += f"{dec_sign}{dec_d:02d}:{dec_m:02d}:{dec_s:02d}"
        else:
            solved_dec_text += "N/A"
            
        self.draw.text(
            (10, 85),
            solved_dec_text,
            font=self.fonts.base.font,
            fill=self.colors.get(255),
        )

        # Display sync status (using smaller font)
        if self.sync_in_progress:
            self.draw.text(
                (10, 100),
                "SYNCING...",
                font=self.fonts.base.font,
                fill=self.colors.get(255),
            )
        elif self.sync_result is not None:
            if self.sync_result:
                self.draw.text(
                    (10, 100),
                    "SYNC SUCCESS!",
                    font=self.fonts.base.font,
                    fill=self.colors.get(255),
                )
            else:
                self.draw.text(
                    (10, 100),
                    "SYNC FAILED",
                    font=self.fonts.base.font,
                    fill=self.colors.get(128),
                )

        # Display instructions
        self.draw.text(
            (10, 115),
            "Press ENTER to sync",
            font=self.fonts.base.font,
            fill=self.colors.get(255),
        )

    def key_enter(self):
        """Perform sync operation"""
        if not self.mount_api or not self.mount_api.mount:
            self.message("No mount connected", 2)
            return True

        if not self.mount_api.mount.connected:
            self.message("Mount not connected", 2)
            return True

        solution = self.shared_state.solution()
        if not solution:
            self.message("No position data", 2)
            return True

        current_ra = solution.get("RA")
        current_dec = solution.get("Dec")

        if not current_ra or not current_dec:
            self.message("Invalid position", 2)
            return True

        # Start sync
        self.sync_in_progress = True
        self.sync_result = None
        self.message("Syncing...", 1)

        try:
            logger.info(f"Attempting sync to RA: {current_ra:.6f}°, DEC: {current_dec:.6f}°")
            
            # Perform sync with degrees (mount handles conversion internally)
            success, message = self.mount_api.sync_to_position(current_ra, current_dec)

            logger.info(f"Sync result: success={success}, message='{message}'")

            self.sync_result = success
            self.last_sync_time = time.time()

            if success:
                logger.info("Simple sync UI: Sync operation completed successfully")
                self.message("Sync successful!", 2)
            else:
                logger.error(f"Simple sync UI: Sync operation failed: {message}")
                self.message(f"Sync failed: {message}", 3)

        except Exception as e:
            logger.error(f"Sync error: {e}")
            self.sync_result = False
            self.message("Sync error", 3)

        finally:
            self.sync_in_progress = False

        return True

    def key_right(self):
        """Right button - do nothing to prevent accidental syncs"""
        return False

    def key_left(self):
        """Go back"""
        return True

    def close(self):
        """Clean up resources"""
        if self.mount_api:
            self.mount_api.close()
        super().close()
