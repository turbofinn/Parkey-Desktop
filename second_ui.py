from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import sys
from entry_ui import ParkingAppSplash
from exit_ui import ParkingAppFourth
from api.ApiService import ApiService
from api.ApiService import EnvConfig
class ParkingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parkkey - Key to Parking")
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        self.setStyleSheet("background-color: #117554;")
        env_config = EnvConfig()
        self.api_service = ApiService(env_config)
        
  
        self.availableSpace = "Loading..."
        self.capacity = "Loading..."
        self.rating = "Loading..."
        self.charges = "20 Rs/Hours"  
        self.parkingName = "Loading..."

        self.initUI()  
        self.calllemployeedetails() 

    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 20)
        main_layout.setSpacing(70)

        # Header layout
        header_frame = QFrame()
        header_frame.setFixedHeight(150)
        header_frame.setStyleSheet("background-color: white; padding: 10px;")
        header_layout = QHBoxLayout()

        # Title image
        title_image = QLabel()
        pixmap = QPixmap('assets/titlepage.png')
        title_image.setPixmap(pixmap)
        title_image.setScaledContents(True)
        title_image.setFixedSize(600, 150) 

        # Station name box
        station_frame = QFrame()
        station_frame.setStyleSheet("background-color: #C4D9FF; color: black; border-radius: 15px;")
        self.station_label = QLabel()
        self.station_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.station_label.setAlignment(Qt.AlignCenter)

        station_layout = QVBoxLayout()
        station_layout.addWidget(self.station_label)
        station_frame.setLayout(station_layout)
        station_frame.setFixedSize(450, 100)

        header_layout.addWidget(title_image)
        header_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        header_layout.addWidget(station_frame)

        header_frame.setLayout(header_layout)
        main_layout.addWidget(header_frame)

        # Container frame for info boxes
        info_container = QFrame()
        info_container.setStyleSheet("background-color: transparent;")
        info_container_layout = QVBoxLayout()
        info_container_layout.setContentsMargins(40, 0, 40, 0)

        # Information layout
        info_layout = QHBoxLayout()
        info_layout.setSpacing(15)
        info_layout.setAlignment(Qt.AlignCenter)

        # Define labels as instance variables for dynamic updates
        self.capacity_label = QLabel(self.capacity)
        self.availableSpace_label = QLabel(self.availableSpace)
        self.rating_label = QLabel(self.rating)
        self.charges_label = QLabel(self.charges)

        # Data for info boxes
        info_data = [
            ("Capacity", self.capacity_label),
            ("Charges", self.charges_label),
            ("Available Space", self.availableSpace_label),
            ("Rating", self.rating_label),
        ]

        # Creating info boxes
        for title, label in info_data:
            info_frame = QFrame()
            info_frame.setFixedSize(400, 350)
            info_frame.setStyleSheet(
                "background-color: white; border-radius: 10px; padding: 5px; font-size:40px"
            )
            info_layout_inner = QVBoxLayout()

            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 12, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)

            label.setFont(QFont("Arial", 10))
            label.setAlignment(Qt.AlignCenter)

            info_layout_inner.addWidget(title_label)
            info_layout_inner.addWidget(label)

            info_frame.setLayout(info_layout_inner)
            info_layout.addWidget(info_frame)

        info_container_layout.addLayout(info_layout)
        
        # Entry and Exit buttons layout
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

    def calllemployeedetails(self):
            """Fetch parking details and update UI dynamically."""
            response = self.api_service.employeeDetails()

            parkingID = response.get('parkingSpaceID')
            if not parkingID:
                print("Error: parkingSpaceID not found!")
                return  

            parkingdetres = self.api_service.parkingSpaceDetails(parkingID)
            

            self.availableSpace = parkingdetres.get('availableSpace', "N/A")
            self.capacity = parkingdetres.get('totalSpace', "N/A")
            self.rating = parkingdetres.get('rating', "N/A")
            self.parkingName = parkingdetres.get('parkingName', "N/A")

            self.capacity_label.setText(str(self.capacity))
            self.availableSpace_label.setText(str(self.availableSpace))
            self.rating_label.setText(str(self.rating))
            self.station_label.setText(self.parkingName)

            


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingApp()
    window.show()
    sys.exit(app.exec_())
