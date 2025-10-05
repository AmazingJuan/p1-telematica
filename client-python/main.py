import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from welcome_view import WelcomeView
from observer_view import ObserverView
from admin_view import AdminView
from socket_handler import SocketHandler

# Estilos globales

GLOBAL_STYLE = """
    QWidget {
        background: #f8f9fa;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    QLabel {
        color: #1a1a1a;
    }
"""

PRIMARY_BUTTON = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a9eff, stop:1 #357ae8);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 600;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5ba8ff, stop:1 #4a9eff);
    }
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #357ae8, stop:1 #2869d4);
    }
"""

SECONDARY_BUTTON = """
    QPushButton {
        background: white;
        color: #4a9eff;
        border: 2px solid #4a9eff;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 600;
    }
    QPushButton:hover {background: #f0f7ff;
    }
    QPushButton:pressed {background: #e0f0ff;
    }
"""


class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autonomous Vehicle Client")
        self.resize(900, 700)
        self.setStyleSheet(GLOBAL_STYLE)
        
        # Manejador de sockets
        self.socket_handler = SocketHandler(self)
        
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Crear vistas
        self.welcome = WelcomeView()
        self.observer = ObserverView(self.socket_handler)
        self.admin = AdminView(self.socket_handler)
        
        # Agregar vistas al stack
        self.stack.addWidget(self.welcome)
        self.stack.addWidget(self.observer)
        self.stack.addWidget(self.admin)
        
        # Conectar señales
        self.welcome.go_observer.connect(self._connect_as_observer)
        self.welcome.go_admin.connect(self._ask_password)
        self.observer.back.connect(lambda: self.stack.setCurrentWidget(self.welcome))
        self.admin.back.connect(lambda: self.stack.setCurrentWidget(self.welcome))
        
        self.socket_handler.auth_failed.connect(self._on_auth_failed)
        self.socket_handler.admin_authenticated.connect(self._on_admin_authenticated)
        
        # Comenzar en la vista de bienvenida
        self.stack.setCurrentWidget(self.welcome)
        
        self.host = "localhost"
        self.port = 5000
        self.admin_password = "admin123"
    
    def _connect_as_observer(self):
        
        if not self._ask_connection_settings():
            return
        
        # Conectar al servidor
        if self.socket_handler.connect_to_server(self.host, self.port):
            self.stack.setCurrentWidget(self.observer)
        else:
            self._show_error("Connection Failed", "Could not connect to the server")
    
    def _ask_connection_settings(self):
        """Solicitar al usuario el host y el puerto"""
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Connection Settings")
        dlg.setModal(True)
        dlg.setFixedWidth(400)
        dlg.setStyleSheet("""
            QDialog {background: white;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(dlg)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QtWidgets.QLabel("🔌 Server Connection")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1a1a1a;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        
        host_label = QtWidgets.QLabel("Host:")
        host_label.setStyleSheet("font-size: 13px; color: #6c757d;")
        le_host = QtWidgets.QLineEdit(self.host)
        le_host.setPlaceholderText("localhost or IP address")
        le_host.setStyleSheet("""
            QLineEdit {
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4a9eff;
            }
        """)
        
        
        port_label = QtWidgets.QLabel("Port:")
        port_label.setStyleSheet("font-size: 13px; color: #6c757d;")
        le_port = QtWidgets.QLineEdit(str(self.port))
        le_port.setPlaceholderText("Port number")
        le_port.setStyleSheet("""
            QLineEdit {
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4a9eff;
            }
        """)
        
        # Botones
        
        btn_ok = QtWidgets.QPushButton("Connect")
        btn_ok.setStyleSheet(PRIMARY_BUTTON)
        btn_ok.setFixedHeight(45)
        btn_ok.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_ok.setDefault(True)
        
        btn_cancel = QtWidgets.QPushButton("Cancel")
        btn_cancel.setStyleSheet(SECONDARY_BUTTON)
        btn_cancel.setFixedHeight(45)
        btn_cancel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        btn_ok.clicked.connect(dlg.accept)
        btn_cancel.clicked.connect(dlg.reject)
        
        buttons = QtWidgets.QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_ok)
        
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(host_label)
        layout.addWidget(le_host)
        layout.addWidget(port_label)
        layout.addWidget(le_port)
        layout.addSpacing(10)
        layout.addLayout(buttons)
        
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            try:
                self.host = le_host.text().strip()
                self.port = int(le_port.text().strip())
                return True
            except ValueError:
                self._show_error("Invalid Input", "Port must be a valid number")
                return False
        return False
    
    def _ask_password(self):
        
        if not self._ask_connection_settings():
            return
    
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Authentication")
        dlg.setModal(True)
        dlg.setFixedWidth(400)
        dlg.setStyleSheet("""
            QDialog {background: white;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(dlg)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QtWidgets.QLabel("🔐 Administrator Access")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1a1a1a;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        
        subtitle = QtWidgets.QLabel("Enter your password to continue")
        subtitle.setStyleSheet("font-size: 13px; color: #6c757d;")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        
        le = QtWidgets.QLineEdit()
        le.setEchoMode(QtWidgets.QLineEdit.Password)
        le.setPlaceholderText("Password")
        le.setStyleSheet("""
            QLineEdit {
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QLineEdit:focus {border-color: #4a9eff;}
        """)
        
        btn_ok = QtWidgets.QPushButton("Sign In")
        btn_ok.setStyleSheet(PRIMARY_BUTTON)
        btn_ok.setFixedHeight(45)
        btn_ok.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_ok.setDefault(True)
        
        btn_cancel = QtWidgets.QPushButton("Cancel")
        btn_cancel.setStyleSheet(SECONDARY_BUTTON)
        btn_cancel.setFixedHeight(45)
        btn_cancel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        btn_ok.clicked.connect(dlg.accept)
        btn_cancel.clicked.connect(dlg.reject)
        
        buttons = QtWidgets.QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_ok)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addWidget(le)
        layout.addSpacing(10)
        layout.addLayout(buttons)
        
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            password = le.text()
            
            self._pending_password = password
            
            # Conectar al servidor con la contraseña
            if self.socket_handler.connect_to_server(self.host, self.port, password):
                    # Esperar la respuesta de autenticación
                pass
            else:
                self._show_error("Connection Failed", "Could not connect to the server")
    
    def _on_admin_authenticated(self):
        self.stack.setCurrentWidget(self.admin)
    
    def _on_auth_failed(self):
        self._show_error("Authentication Failed", "Incorrect password")
        self.stack.setCurrentWidget(self.observer)
    
    def _show_error(self, title, message):
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background: white;
            }
            QPushButton {
                background: #4a9eff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #5ba8ff;
            }
        """)
        msg.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Autonomous Vehicle Client")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()