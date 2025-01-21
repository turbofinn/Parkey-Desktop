from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt
import sys

class ParkingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parkkey - Key to Parking")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #2ECC71;")

        self.initUI()

    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Top header layout
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)  # Center align the header elements

        # Logo and title
        logo_label = QLabel()
        logo_pixmap = QPixmap("titlepage.png")  # Replace with your logo image path
        logo_label.setPixmap(logo_pixmap)
        logo_label.setFixedSize(200, 200)  # Set width and height of the titlepage.png image
        logo_label.setScaledContents(True)

        location_label = QLabel("Raipur railway station")
        location_label.setFont(QFont("Arial", 14))
        location_label.setStyleSheet("background-color: #D0EAF2; color: black; padding: 5px; border-radius: 5px;")
        location_label.setAlignment(Qt.AlignCenter)
        location_label.setFixedSize(200, 200)  # Set width and height of the location label to match logo

        header_layout.addWidget(logo_label)
        header_layout.addWidget(location_label)

        main_layout.addLayout(header_layout)

        # Information layout
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)

        info_data = [
            ("Capacity", "100 Vehicles"),
            ("Charges", "20 Rs/Hours"),
            ("Available space", "20 Vehicles"),
            ("Rating", "3 Star"),
        ]

        for title, value in info_data:
            info_frame = QFrame()
            info_frame.setStyleSheet(
                "background-color: white; border-radius: 10px; padding: 10px;"
            )
            info_layout_inner = QVBoxLayout()

            icon_label = QLabel()
            icon_pixmap = QPixmap("icon.png")  # Replace with the specific icon path
            icon_label.setPixmap(icon_pixmap)
            icon_label.setFixedSize(40, 40)
            icon_label.setScaledContents(True)
            icon_label.setAlignment(Qt.AlignCenter)

            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 12, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)

            value_label = QLabel(value)
            value_label.setFont(QFont("Arial", 10))
            value_label.setAlignment(Qt.AlignCenter)

            info_layout_inner.addWidget(icon_label)
            info_layout_inner.addWidget(title_label)
            info_layout_inner.addWidget(value_label)

            info_frame.setLayout(info_layout_inner)
            info_layout.addWidget(info_frame)

        main_layout.addLayout(info_layout)

        # Entry and Exit buttons
        button_layout = QHBoxLayout()
        entry_button = QPushButton("Entry")
        entry_button.setFont(QFont("Arial", 14))
        entry_button.setStyleSheet("background-color: #FF5733; color: white; padding: 10px; border-radius: 10px;")

        exit_button = QPushButton("Exit")
        exit_button.setFont(QFont("Arial", 14))
        exit_button.setStyleSheet("background-color: #FF5733; color: white; padding: 10px; border-radius: 10px;")

        button_layout.addWidget(entry_button)
        button_layout.addWidget(exit_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingApp()
    window.show()
    sys.exit(app.exec_())
