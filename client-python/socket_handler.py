import socket
import json
import threading
from PyQt5 import QtCore


class SocketHandler(QtCore.QObject):
    """Handles TCP socket communication with the car server"""
    
    # Signals
    connected = QtCore.pyqtSignal()
    disconnected = QtCore.pyqtSignal()
    telemetry_received = QtCore.pyqtSignal(dict)
    message_received = QtCore.pyqtSignal(str)
    admin_authenticated = QtCore.pyqtSignal()
    auth_failed = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.socket = None
        self.running = False
        self.reader_thread = None
        self.is_admin = False
        
    def connect_to_server(self, host, port, password=None):
        """Connect to the server and optionally authenticate as admin"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.running = True
            
            # Start reader thread
            self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.reader_thread.start()
            
            # If password is provided, authenticate as admin
            if password:
                self._pending_auth = password
            else:
                self._pending_auth = None
            
            self.connected.emit()
            return True
            
        except Exception as e:
            self.message_received.emit(f"Connection error: {str(e)}")
            return False
    
    def _read_loop(self):
        """Background thread that reads data from the server"""
        buffer = ""
        
        try:
            while self.running and self.socket:
                try:
                    data = self.socket.recv(4096).decode('utf-8')
                    if not data:
                        break
                    
                    buffer += data
                    lines = buffer.split('\n')
                    buffer = lines[-1]  # Keep incomplete line in buffer
                    
                    for line in lines[:-1]:
                        line = line.strip()
                        if line:
                            self._process_line(line)
                            
                except socket.timeout:
                    continue
                except Exception as e:
                    self.message_received.emit(f"Read error: {str(e)}")
                    break
                    
        finally:
            self.running = False
            self.disconnected.emit()
    
    def _process_line(self, line):
        """Process a line received from the server"""
        # Check for observer mode message
        if "You are observer" in line or "you are observer" in line.lower():
            self.message_received.emit("Connected as observer")
            self.is_admin = False
            
            # Try to authenticate if password was provided
            if self._pending_auth:
                self.send_command(f"AUTH {self._pending_auth}")
                self._pending_auth = None
            return
        
        # Check for admin welcome message
        if "Welcome ADMIN" in line or "welcome admin" in line.lower() or "You are now admin" in line or "you are now admin" in line.lower():
            self.is_admin = True
            self.message_received.emit("Authenticated as administrator")
            self.admin_authenticated.emit()
            return
        
        # Check for authentication failure
        if "Invalid password" in line or "invalid password" in line.lower():
            self.is_admin = False
            self.auth_failed.emit()
            return
        
        # Try to parse as JSON (telemetry data)
        if line.startswith('{'):
            try:
                data = json.loads(line)
                self.telemetry_received.emit(data)
                return
            except json.JSONDecodeError:
                pass
        
        # If not JSON or special message, emit as general message
        self.message_received.emit(line)
    
    def send_command(self, command):
        if self.socket and self.running:
            try:
                self.socket.sendall((command + '\n').encode('utf-8'))
            except Exception as e:
                self.message_received.emit(f"Send error: {str(e)}")
    
    def disconnect_from_server(self):
        """Disconnect from the server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.is_admin = False
