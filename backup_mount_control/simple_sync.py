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
        if not self.mount_api.mount or not self.mount_api.mount.connection_status:
            self.draw.text(
                (10, 40),
                "Mount not connected",
                font=self.fonts.base.font,
                fill=self.colors.get(128),
            )
            return

        # Get current position from last plate solve
        solution = self.shared_state.solution()
        if not solution:
            self.draw.text(
                (10, 40),
                "No position data",
                font=self.fonts.base.font,
                fill=self.colors.get(128),
            )
            return

        current_ra = solution.get("RA")
        current_dec = solution.get("Dec")

        if not current_ra or not current_dec:
            self.draw.text(
                (10, 40),
                "Invalid position",
                font=self.fonts.base.font,
                fill=self.colors.get(128),
            )
            return

        # Display current position from plate solve
        self.draw.text(
            (10, 40),
            f"RA: {current_ra:.2f}°",
            font=self.fonts.base.font,
            fill=self.colors.get(255),
        )
        self.draw.text(
            (10, 60),
            f"DEC: {current_dec:.2f}°",
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
            (10, 120),
            "Press RIGHT to sync",
            font=self.fonts.base.font,
            fill=self.colors.get(255),
        )

    def key_right(self):
        """Perform sync operation"""
        if not self.mount_api or not self.mount_api.mount:
            self.message("No mount connected", 2)
            return True

        if not self.mount_api.mount.connection_status:
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
            # Convert to mount format
            from PiFinder import calc_utils
            ra_str = calc_utils.ra_to_hms_str(current_ra)
            dec_str = calc_utils.dec_to_dms_str(current_dec)

            # Perform sync
            success, message = self.mount_api.sync_to_position(ra_str, dec_str)

            self.sync_result = success
            self.last_sync_time = time.time()

            if success:
                self.message("Sync successful!", 2)
            else:
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
