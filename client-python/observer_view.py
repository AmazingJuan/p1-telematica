from PyQt5 import QtCore, QtGui, QtWidgets


class MetricCard(QtWidgets.QWidget):
    def __init__(self, title, value="—", color="#4a9eff"):
        super().__init__()
        self.color = color

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        # Estilo de la tarjeta de métrica
        self.setStyleSheet(f"""
            MetricCard {{
                background: white;
                border-radius: 16px;
                border-left: 4px solid {color};
            }}
        """)

        title_label = QtWidgets.QLabel(title)
        # Estilo del título
        title_label.setStyleSheet(f"color: #6c757d; font-size: 12px; font-weight: 600;")

        self.value_label = QtWidgets.QLabel(value)
        # Estilo del valor
        self.value_label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 700;")

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value):
        self.value_label.setText(value)


class ObserverView(QtWidgets.QWidget):
    
    back = QtCore.pyqtSignal()

    def __init__(self, socket_handler):
        super().__init__()
        self.socket_handler = socket_handler

        root = QtWidgets.QVBoxLayout(self)
        root.setSpacing(20)
        root.setContentsMargins(30, 30, 30, 30)

        # Encabezado
        header = QtWidgets.QHBoxLayout()
        self.role_label = QtWidgets.QLabel("👀 Observer Mode")
        self.role_label.setStyleSheet("font-size: 18px; color: #10b981; font-weight: 700;")

        btn_back = QtWidgets.QPushButton("← Back")
        btn_back.clicked.connect(self._on_back)
        
        # Estilo del botón secundario
        secondary_button_style = """
            QPushButton {
                background: white;
                color: #4a9eff;
                border: 2px solid #4a9eff;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #f0f7ff;
            }
            QPushButton:pressed {
                background: #e0f0ff;
            }
        """
        
        btn_back.setStyleSheet(secondary_button_style)
        btn_back.setFixedWidth(140)
        btn_back.setFixedHeight(40)
        btn_back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        header.addWidget(self.role_label)
        header.addStretch()
        header.addWidget(btn_back)

        # Cuadrícula de métricas
        metrics_layout = QtWidgets.QGridLayout()
        metrics_layout.setSpacing(15)

        self.speed_card = MetricCard("Speed", "—", "#4a9eff")
        self.battery_card = MetricCard("Battery", "—", "#10b981")
        self.temp_card = MetricCard("Temperature", "—", "#f59e0b")
        self.dir_card = MetricCard("Direction", "—", "#8b5cf6")

        metrics_layout.addWidget(self.speed_card, 0, 0)
        metrics_layout.addWidget(self.battery_card, 0, 1)
        metrics_layout.addWidget(self.temp_card, 1, 0)
        metrics_layout.addWidget(self.dir_card, 1, 1)

        # Contenedor del log
        log_container = QtWidgets.QWidget()
        log_container.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 16px;
            }
        """)
        log_layout = QtWidgets.QVBoxLayout(log_container)
        log_layout.setContentsMargins(20, 20, 20, 20)

        log_title = QtWidgets.QLabel("Event Log")
        log_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #1a1a1a;")

        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        # Estilo del área de log
        self.log.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                color: #2c3e50;
            }
        """)

        log_layout.addWidget(log_title)
        log_layout.addWidget(self.log)

        # Ensamblaje del layout
        root.addLayout(header)
        root.addLayout(metrics_layout)
        root.addWidget(log_container, 1)

        # Conectar señales del socket
        if self.socket_handler:
            self.socket_handler.telemetry_received.connect(self.on_telemetry)
            self.socket_handler.message_received.connect(self.on_message)
            self.socket_handler.disconnected.connect(self.on_disconnected)

    def _on_back(self):
        if self.socket_handler:
            self.socket_handler.disconnect_from_server()
        self.back.emit()

    @QtCore.pyqtSlot(dict)
    def on_telemetry(self, data):
        speed = data.get('speed', 0)
        battery = data.get('battery', 0)
        temperature = data.get('temperature', 0)
        direction = data.get('direction', 'STOP')

        self.speed_card.set_value(f"{speed:.2f} km/h")
        self.battery_card.set_value(f"{battery:.2f} %")
        self.temp_card.set_value(f"{temperature:.2f} °C")
        self.dir_card.set_value(direction)

        timestamp = QtCore.QTime.currentTime().toString('hh:mm:ss')
        self.log.append(
            f"<span style='color: #6c757d;'>{timestamp}</span> "
            f"<span style='color: #10b981;'>← TELEMETRY</span> "
            f"{speed:.2f} km/h | {battery:.2f} % | {temperature:.2f} °C | {direction}"
        )

    @QtCore.pyqtSlot(str)
    def on_message(self, message):
        timestamp = QtCore.QTime.currentTime().toString('hh:mm:ss')
        self.log.append(
            f"<span style='color: #6c757d;'>{timestamp}</span> "
            f"<span style='color: #6c757d;'>ℹ INFO</span> {message}"
        )

    @QtCore.pyqtSlot()
    def on_disconnected(self):
        timestamp = QtCore.QTime.currentTime().toString('hh:mm:ss')
        self.log.append(
            f"<span style='color: #6c757d;'>{timestamp}</span> "
            f"<span style='color: #ef4444;'>⚠ DISCONNECTED</span> Connection lost"
        )
