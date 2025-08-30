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

        # Title
        self.draw.text(
            (10, 10),
            "MOUNT SYNC",
            font=self.fonts.large.font,
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

        # Display coordinate headers
        self.draw.text(
            (10, 40),
            "Mount / Solved:",
            font=self.fonts.base.font,
            fill=self.colors.get(255),
        )

        # Display RA coordinates on one line
        ra_text = "RA: "
        if mount_ra is not None:
            ra_text += f"{mount_ra:.2f}°"
        else:
            ra_text += "N/A"
        ra_text += " / "
        if current_ra is not None:
            ra_text += f"{current_ra:.2f}°"
        else:
            ra_text += "N/A"
            
        self.draw.text(
            (10, 55),
            ra_text,
            font=self.fonts.base.font,
            fill=self.colors.get(255),
        )

        # Display DEC coordinates on one line
        dec_text = "DEC: "
        if mount_dec is not None:
            dec_text += f"{mount_dec:.2f}°"
        else:
            dec_text += "N/A"
        dec_text += " / "
        if current_dec is not None:
            dec_text += f"{current_dec:.2f}°"
        else:
            dec_text += "N/A"
            
        self.draw.text(
            (10, 70),
            dec_text,
            font=self.fonts.base.font,
            fill=self.colors.get(255),
        )

        # Display sync status
        if self.sync_in_progress:
            self.draw.text(
                (10, 90),
                "SYNCING...",
                font=self.fonts.large.font,
                fill=self.colors.get(255),
            )
        elif self.sync_result is not None:
            if self.sync_result:
                self.draw.text(
                    (10, 90),
                    "SYNC SUCCESS!",
                    font=self.fonts.large.font,
                    fill=self.colors.get(255),
                )
            else:
                self.draw.text(
                    (10, 90),
                    "SYNC FAILED",
                    font=self.fonts.large.font,
                    fill=self.colors.get(128),
                )

        # Display instructions
        self.draw.text(
            (10, 110),
            "Press RIGHT to sync",
            font=self.fonts.base.font,
            fill=self.colors.get(255),
        )

    def key_right(self):
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

    def key_left(self):
        """Go back"""
        return True

    def close(self):
        """Clean up resources"""
        if self.mount_api:
            self.mount_api.close()
        super().close()
