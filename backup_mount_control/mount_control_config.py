# Mount Control Configuration for PiFinder
# Provides configuration management for mount control features

import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class MountControlConfig:
    """Configuration for mount control features"""
    
    # Mount connection settings
    mount_type: str = "astro_physics"  # "astro_physics", "onstep", etc.
    host: str = "192.168.1.100"  # Mount IP address
    port: int = 23  # Default port for Astro Physics mounts
    serial_port: str = ""  # Serial port (if using serial connection)
    
    # Auto-sync settings
    auto_sync_enabled: bool = True
    sync_threshold_arcmin: float = 2.0  # Position error threshold for auto-sync
    sync_cooldown_minutes: int = 5  # Minimum time between syncs
    
    # Slew settings
    slew_timeout_minutes: int = 10  # Maximum time for slew to complete
    slew_completion_threshold_arcmin: float = 1.0  # Consider slew complete within this error
    
    # Monitoring settings
    position_update_interval_seconds: float = 2.0  # How often to update mount position
    status_update_interval_seconds: float = 5.0  # How often to update mount status
    
    # UI settings
    show_mount_control_in_menu: bool = True
    mount_control_menu_position: int = 5  # Position in main menu
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MountControlConfig':
        """Create configuration from dictionary"""
        return cls(**data)
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        try:
            # Validate mount type
            if self.mount_type not in ["astro_physics", "onstep"]:
                logger.error(f"Invalid mount type: {self.mount_type}")
                return False
            
            # Validate connection settings
            if self.mount_type == "astro_physics":
                if not self.host or not self.port:
                    logger.error("Host and port required for Astro Physics mount")
                    return False
                if self.port < 1 or self.port > 65535:
                    logger.error(f"Invalid port number: {self.port}")
                    return False
            
            # Validate thresholds
            if self.sync_threshold_arcmin <= 0:
                logger.error("Sync threshold must be positive")
                return False
            
            if self.slew_completion_threshold_arcmin <= 0:
                logger.error("Slew completion threshold must be positive")
                return False
            
            # Validate timeouts
            if self.sync_cooldown_minutes < 0:
                logger.error("Sync cooldown cannot be negative")
                return False
            
            if self.slew_timeout_minutes <= 0:
                logger.error("Slew timeout must be positive")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False

class MountControlConfigManager:
    """Manager for mount control configuration"""
    
    def __init__(self, config_file_path: str = None):
        self.config_file_path = config_file_path or "mount_control_config.json"
        self.config = MountControlConfig()
        self.load_config()
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            with open(self.config_file_path, 'r') as f:
                data = json.load(f)
                self.config = MountControlConfig.from_dict(data)
            
            if self.config.validate():
                logger.info("Mount control configuration loaded successfully")
                return True
            else:
                logger.error("Mount control configuration validation failed")
                return False
                
        except FileNotFoundError:
            logger.info("Mount control config file not found, using defaults")
            return self.save_config()  # Save default configuration
        except Exception as e:
            logger.error(f"Error loading mount control configuration: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file_path, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)
            logger.info("Mount control configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving mount control configuration: {e}")
            return False
    
    def load_from_pifinder_config(self, pifinder_config: dict) -> bool:
        """Load configuration from PiFinder config dictionary"""
        try:
            mount_config = pifinder_config.get("mount_control", {})
            if mount_config:
                self.config = MountControlConfig.from_dict(mount_config)
                if self.config.validate():
                    logger.info("Mount control configuration loaded from PiFinder config")
                    return True
                else:
                    logger.error("Mount control configuration validation failed")
                    return False
            else:
                logger.info("No mount control configuration in PiFinder config, using defaults")
                return True
        except Exception as e:
            logger.error(f"Error loading from PiFinder config: {e}")
            return False
    
    def get_config(self) -> MountControlConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, **kwargs) -> bool:
        """Update configuration with new values"""
        try:
            # Update configuration attributes
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    logger.warning(f"Unknown configuration key: {key}")
            
            # Validate updated configuration
            if self.config.validate():
                return self.save_config()
            else:
                logger.error("Configuration validation failed after update")
                return False
                
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    def get_mount_connection_params(self) -> Dict[str, Any]:
        """Get mount connection parameters"""
        params = {
            "mount_type": self.config.mount_type,
            "host": self.config.host,
            "port": self.config.port
        }
        
        if self.config.serial_port:
            params["serial_port"] = self.config.serial_port
        
        return params
    
    def get_auto_sync_params(self) -> Dict[str, Any]:
        """Get auto-sync parameters"""
        return {
            "auto_sync_enabled": self.config.auto_sync_enabled,
            "sync_threshold_arcmin": self.config.sync_threshold_arcmin,
            "sync_cooldown_minutes": self.config.sync_cooldown_minutes
        }
    
    def get_slew_params(self) -> Dict[str, Any]:
        """Get slew parameters"""
        return {
            "slew_timeout_minutes": self.config.slew_timeout_minutes,
            "slew_completion_threshold_arcmin": self.config.slew_completion_threshold_arcmin
        }

# Default configuration for different mount types
DEFAULT_CONFIGS = {
    "astro_physics": {
        "mount_type": "astro_physics",
        "host": "192.168.1.100",
        "port": 9996,
        "auto_sync_enabled": True,
        "sync_threshold_arcmin": 2.0,
        "sync_cooldown_minutes": 5,
        "slew_timeout_minutes": 10,
        "slew_completion_threshold_arcmin": 1.0
    },
    "onstep": {
        "mount_type": "onstep",
        "host": "192.168.1.100",
        "port": 9996,
        "auto_sync_enabled": True,
        "sync_threshold_arcmin": 2.0,
        "sync_cooldown_minutes": 5,
        "slew_timeout_minutes": 10,
        "slew_completion_threshold_arcmin": 1.0
    }
}

def create_default_config(mount_type: str = "astro_physics") -> MountControlConfig:
    """Create default configuration for specified mount type"""
    if mount_type not in DEFAULT_CONFIGS:
        logger.warning(f"Unknown mount type {mount_type}, using astro_physics defaults")
        mount_type = "astro_physics"
    
    return MountControlConfig.from_dict(DEFAULT_CONFIGS[mount_type])

def get_config_manager(config_file_path: str = None) -> MountControlConfigManager:
    """Get mount control configuration manager"""
    return MountControlConfigManager(config_file_path)
