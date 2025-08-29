# Astro Physics Mount Communication Interface
# Supports Astro Physics mounts like Mach1, Mach2, etc.

import socket
import time
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

MAX_LEN = 64
SOCKET_TIMEOUT = 5.0
SERIAL_TIMEOUT = 3.0

class APConnectionError(Exception):
    pass

class APTimeoutError(Exception):
    pass

class APCommandError(Exception):
    pass

class AstroPhysicsInterface:
    """
    Communication interface for Astro Physics mounts.
    Supports both serial and TCP/IP connections.
    """
    
    def __init__(self, host: str = '', port: int = 0, serial_port: str = ''):
        self.host = host
        self.port = port
        self.serial_port = serial_port
        self.sock = None
        self.serial_conn = None
        self.connection_type = None
        
        # Determine connection type
        if host and port:
            self.connection_type = 'tcp'
        elif serial_port:
            self.connection_type = 'serial'
        else:
            raise APConnectionError("Must specify either host/port for TCP or serial_port for serial connection")
    
    def connect(self):
        """Establish connection to the mount"""
        if self.connection_type == 'tcp':
            self._connect_tcp()
        elif self.connection_type == 'serial':
            self._connect_serial()
    
    def _connect_tcp(self):
        """Connect via TCP/IP"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.settimeout(SOCKET_TIMEOUT)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to AP mount via TCP at {self.host}:{self.port}")
        except socket.error as e:
            raise APConnectionError(f"Could not connect to AP mount via TCP: {e}")
    
    def _connect_serial(self):
        """Connect via serial port"""
        try:
            import serial
            self.serial_conn = serial.Serial(
                port=self.serial_port,
                baudrate=9600,
                timeout=SERIAL_TIMEOUT,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            logger.info(f"Connected to AP mount via serial at {self.serial_port}")
        except ImportError:
            raise APConnectionError("pyserial not installed. Install with: pip install pyserial")
        except Exception as e:
            raise APConnectionError(f"Could not connect to AP mount via serial: {e}")
    
    def close(self):
        """Close the connection"""
        try:
            if self.sock:
                self.sock.close()
                self.sock = None
            if self.serial_conn:
                self.serial_conn.close()
                self.serial_conn = None
            logger.info("AP mount connection closed")
        except Exception as e:
            logger.error(f"Error closing AP mount connection: {e}")
    
    def send_command(self, command: str, delay: float = 0.1) -> str:
        """
        Send a command to the mount and return the response
        
        Args:
            command: The command to send (without # terminator)
            delay: Delay after sending command
            
        Returns:
            The mount's response
        """
        # Add # terminator if not present (Astro Physics protocol requirement)
        if not command.endswith('#'):
            command += '#'
        
        # Add carriage return for transmission
        command += '\r'
        
        try:
            if self.connection_type == 'tcp':
                return self._send_tcp_command(command, delay)
            elif self.connection_type == 'serial':
                return self._send_serial_command(command, delay)
        except Exception as e:
            logger.error(f"Error sending command '{command}': {e}")
            raise APCommandError(f"Failed to send command: {e}")
    
    def _send_tcp_command(self, command: str, delay: float) -> str:
        """Send command via TCP"""
        if not self.sock:
            self.connect()
        
        try:
            self.sock.sendall(command.encode('utf-8'))
            time.sleep(delay)
            return self._read_tcp_response()
        except socket.timeout:
            raise APTimeoutError("TCP command timeout")
        except Exception as e:
            raise APCommandError(f"TCP command error: {e}")
    
    def _send_serial_command(self, command: str, delay: float) -> str:
        """Send command via serial"""
        if not self.serial_conn:
            self.connect()
        
        try:
            self.serial_conn.write(command.encode('utf-8'))
            time.sleep(delay)
            return self._read_serial_response()
        except Exception as e:
            raise APCommandError(f"Serial command error: {e}")
    
    def _read_tcp_response(self) -> str:
        """Read response from TCP connection"""
        try:
            # Set a shorter timeout for reading responses
            original_timeout = self.sock.gettimeout()
            self.sock.settimeout(1.0)  # 1 second timeout for responses
            
            response = ""
            try:
                while True:
                    data = self.sock.recv(MAX_LEN)
                    if not data:
                        break
                    response += data.decode('utf-8', errors='ignore')
                    if response.endswith('#'):
                        break
            except socket.timeout:
                # Timeout is okay - some commands don't return responses
                pass
            
            # Restore original timeout
            self.sock.settimeout(original_timeout)
            
            return response.strip()
        except Exception as e:
            raise APCommandError(f"TCP read error: {e}")
    
    def _read_serial_response(self) -> str:
        """Read response from serial connection"""
        try:
            if self.serial_conn.in_waiting:
                data = self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8', errors='ignore')
                return data.strip()
            return ""
        except Exception as e:
            raise APCommandError(f"Serial read error: {e}")
    
    def is_connected(self) -> bool:
        """Check if connection is active"""
        if self.connection_type == 'tcp':
            return self.sock is not None
        elif self.connection_type == 'serial':
            return self.serial_conn is not None and self.serial_conn.is_open
        return False
