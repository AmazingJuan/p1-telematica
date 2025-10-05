from PyQt5 import QtCore, QtGui, QtWidgets


class WelcomeView(QtWidgets.QWidget):
    go_observer = QtCore.pyqtSignal()
    go_admin = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(30)

        # Icono de coche
        icon_label = QtWidgets.QLabel("🚗")
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 80px;")

        # Título
        title = QtWidgets.QLabel("Welcome to the Autonomous Vehicle Client")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 36px; font-weight: 700; color: #1a1a1a;")

        # Subtítulo
        subtitle = QtWidgets.QLabel("Select your connection mode")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #6c757d;")

        # Botones
        btn_obs = QtWidgets.QPushButton("Observer")
        btn_adm = QtWidgets.QPushButton("Administrator")

        # Estilo para botón primario
        primary_button_style = """
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

        # Estilo para botón secundario
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

        btn_obs.setStyleSheet(primary_button_style)
        btn_adm.setStyleSheet(secondary_button_style)

        for b in (btn_obs, btn_adm):
            b.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            b.setFixedWidth(300)
            b.setFixedHeight(50)

        # Conectar señales
        btn_obs.clicked.connect(self.go_observer.emit)
        btn_adm.clicked.connect(self.go_admin.emit)

        # Ensamblaje del layout
        layout.addStretch(1)
        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(30)
        layout.addWidget(btn_obs, alignment=QtCore.Qt.AlignCenter)
        layout.addSpacing(15)
        layout.addWidget(btn_adm, alignment=QtCore.Qt.AlignCenter)
        layout.addStretch(2)