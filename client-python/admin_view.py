from PyQt5 import QtCore, QtGui, QtWidgets
from observer_view import ObserverView


class AdminView(ObserverView): # VISTA DE ADMINISTRADOR
    
    def __init__(self, socket_handler):
        super().__init__(socket_handler)
        
        # Actualiza la etiqueta de rol
        self.role_label.setText("⚙️ Administrator Mode")
        self.role_label.setStyleSheet("font-size: 18px; color: #4a9eff; font-weight: 700;")

        # Crea el contenedor de controles
        controls_container = QtWidgets.QWidget()
        controls_container.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 16px;
            }""")
        
        controls_layout = QtWidgets.QVBoxLayout(controls_container)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setSpacing(15)

        controls_title = QtWidgets.QLabel("Control Panel")
        controls_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #1a1a1a;")

        # Primera fila de botones (controles de movimiento)
        buttons_row1 = QtWidgets.QHBoxLayout()
        buttons_row1.setSpacing(12)

        self.btn_up = QtWidgets.QPushButton("⬆ Speed Up")
        self.btn_down = QtWidgets.QPushButton("⬇ Slow Down")
        self.btn_left = QtWidgets.QPushButton("⬅ Turn Left")
        self.btn_right = QtWidgets.QPushButton("➡ Turn Right")

        control_button_style = """
            QPushButton {
                background: white;
                color: #2c3e50;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                padding: 14px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                border-color: #4a9eff;
                color: #4a9eff;
            }
            QPushButton:pressed {
                background: #f8f9fa;
            }
        """

        for b in (self.btn_up, self.btn_down, self.btn_left, self.btn_right):
            b.setStyleSheet(control_button_style)
            b.setFixedHeight(50)
            b.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            buttons_row1.addWidget(b)

        # Segunda fila de botones (cargar batería)
        buttons_row2 = QtWidgets.QHBoxLayout()
        buttons_row2.setSpacing(12)

        self.btn_charge = QtWidgets.QPushButton("🔋 Charge Battery")
        self.btn_charge.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10b981, stop:1 #059669);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #34d399, stop:1 #10b981);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #059669, stop:1 #047857);
            }""")
        
        self.btn_charge.setFixedHeight(50)
        self.btn_charge.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        buttons_row2.addWidget(self.btn_charge)

        # Tercera fila de botones (listar usuarios)
        buttons_row3 = QtWidgets.QHBoxLayout()
        buttons_row3.setSpacing(12)

        self.btn_list_users = QtWidgets.QPushButton("👥 List Connected Users")
        self.btn_list_users.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8b5cf6, stop:1 #7c3aed);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a78bfa, stop:1 #8b5cf6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7c3aed, stop:1 #6d28d9);
            }""")
        
        self.btn_list_users.setFixedHeight(50)
        self.btn_list_users.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        buttons_row3.addWidget(self.btn_list_users)

        # Ensambla el layout de controles
        controls_layout.addWidget(controls_title)
        controls_layout.addLayout(buttons_row1)
        controls_layout.addLayout(buttons_row2)
        controls_layout.addLayout(buttons_row3)

        # Inserta el panel de controles antes del log (en la posición 2)
        self.layout().insertWidget(2, controls_container)

        # Conecta las señales de los botones
        self.btn_up.clicked.connect(lambda: self._send_command("SPEED UP"))
        self.btn_down.clicked.connect(lambda: self._send_command("SLOW DOWN"))
        self.btn_left.clicked.connect(lambda: self._send_command("TURN LEFT"))
        self.btn_right.clicked.connect(lambda: self._send_command("TURN RIGHT"))
        self.btn_charge.clicked.connect(lambda: self._send_command("RECHARGE BATTERY"))
        self.btn_list_users.clicked.connect(lambda: self._send_command("LIST USERS"))

    def _send_command(self, cmd):
        
        if self.socket_handler:
            self.socket_handler.send_command(cmd)
            
            # Registra el comando en el log
            timestamp = QtCore.QTime.currentTime().toString('hh:mm:ss')
            cmd_display = {"SPEED UP": "⬆ SPEED UP", "SLOW DOWN": "⬇ SLOW DOWN", "TURN LEFT": "⬅ TURN LEFT", "TURN RIGHT": "➡ TURN RIGHT", "RECHARGE BATTERY": "🔋 RECHARGE BATTERY", "LIST USERS": "👥 LIST USERS"}.get(cmd, cmd)
            
            self.log.append(
                f"<span style='color: #6c757d;'>{timestamp}</span> "
                f"<span style='color: #4a9eff;'>→ CMD</span> {cmd_display}"
            )