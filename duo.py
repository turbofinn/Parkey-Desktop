from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import sys
from splash import ParkingAppSplash
from fourth import ParkingAppFourth
class ParkingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parkkey - Key to Parking")
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        self.setStyleSheet("background-color: #117554;")

        self.initUI()

    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 20)  # Added bottom margin to prevent sticking
        main_layout.setSpacing(70)  # Space between header and other components

        # Header layout with white background
        header_frame = QFrame()
        header_frame.setFixedHeight(150)
        header_frame.setStyleSheet("background-color: white; padding: 10px;")
        header_layout = QHBoxLayout()

        # Title image
        title_image = QLabel()
        pixmap = QPixmap("titlepage.png")
        title_image.setPixmap(pixmap)
        title_image.setScaledContents(True)
        title_image.setFixedSize(600, 150) 

        # Station name box
        station_frame = QFrame()
        station_frame.setStyleSheet("background-color: #C4D9FF; color: black; border-radius: 15px;")
        station_label = QLabel("Raipur Railway Station")
        station_label.setFont(QFont("Arial", 16, QFont.Bold))
        station_label.setAlignment(Qt.AlignCenter)

        station_layout = QVBoxLayout()
        station_layout.addWidget(station_label)
        station_frame.setLayout(station_layout)
        station_frame.setFixedSize(450, 100)

        header_layout.addWidget(title_image)
        header_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        header_layout.addWidget(station_frame)

        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Container frame for info boxes with margins
        info_container = QFrame()
        info_container.setStyleSheet("background-color: transparent;")
        info_container_layout = QVBoxLayout()
        info_container_layout.setContentsMargins(40, 0, 40, 0)  # Add left and right margins

        # Information layout
        info_layout = QHBoxLayout()
        info_layout.setSpacing(15)
        info_layout.setAlignment(Qt.AlignCenter)

        info_data = [
            ("Capacity", "100 Vehicles"),
            ("Charges", "20 Rs/Hours"),
            ("Available Space", "20 Vehicles"),
            ("Rating", "3 Star"),
        ]

        self.info_frames = []

        for title, value in info_data:
            info_frame = QFrame()
            info_frame.setFixedSize(400, 350)
            info_frame.setStyleSheet(
                "background-color: white; border-radius: 10px; padding: 5px; font-size:40px"
            )
            info_layout_inner = QVBoxLayout()

            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 12, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)

            value_label = QLabel(value)
            value_label.setFont(QFont("Arial", 10))
            value_label.setAlignment(Qt.AlignCenter)

            info_layout_inner.addWidget(title_label)
            info_layout_inner.addWidget(value_label)

            info_frame.setLayout(info_layout_inner)
            info_layout.addWidget(info_frame)
            self.info_frames.append(info_frame)

        info_container_layout.addLayout(info_layout)
        
        # Entry and Exit buttons layout - Moved up inside the info container
        button_layout = QHBoxLayout()
        button_layout.setSpacing(50)
        button_layout.setAlignment(Qt.AlignCenter)

        self.entry_button = QPushButton("Entry")
        self.entry_button.setFixedSize(250, 100)
        self.entry_button.setFont(QFont("Arial", 14))
        self.entry_button.setStyleSheet("background-color: #FF5733; color: white; padding: 10px; border-radius: 10px; font-size:36px")
        self.entry_button.clicked.connect(self.handle_entry_click)  
        
        self.exit_button = QPushButton("Exit")
        self.exit_button.setFixedSize(250, 100)
        self.exit_button.setFont(QFont("Arial", 14))
        self.exit_button.setStyleSheet("background-color: #FF5733; color: white; padding: 10px; border-radius: 10px; font-size:36px")
        self.exit_button.clicked.connect(self.handle_exit_click)  

        button_layout.addWidget(self.entry_button)
        button_layout.addSpacerItem(QSpacerItem(30, 20, QSizePolicy.Fixed, QSizePolicy.Minimum))
        button_layout.addWidget(self.exit_button)

        
        info_container_layout.addLayout(button_layout)
        
        info_container.setLayout(info_container_layout)
        main_layout.addWidget(info_container)

        self.setLayout(main_layout)

    def handle_entry_click(self):
        self.parking_window = ParkingAppSplash()
        self.parking_window.show()
        self.close()

    def handle_exit_click(self):
        self.parking_window = ParkingAppFourth()
        self.parking_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingApp()
    window.show()
    sys.exit(app.exec_())