from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QScrollArea, QSizePolicy, QSpacerItem, QPushButton)
from PyQt5.QtGui import QFont, QColor, QPixmap, QImage
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import sys
import os
import datetime
from new_entry_ui import ParkingAppSplash
from new_exit_ui import ParkingAppFourth
from api.ApiService import ApiService
from api.ApiService import EnvConfig

class HomeLabel(QLabel):
    """Custom QLabel class for home icon that emits a signal when clicked"""
    def __init__(self, text):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)  # Set cursor to pointing hand
        
    def mousePressEvent(self, event):
        # Override the mouse press event to handle click
        if event.button() == Qt.LeftButton:
            # Call the slot function directly
            if hasattr(self.parent().parent().parent(), 'navigate_to_home'):
                self.parent().parent().parent().navigate_to_home()
        super().mousePressEvent(event)


def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class   ParkingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parkkey - Key to Parking")
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        self.setStyleSheet("background-color: #0674B4;")
    
        # Initialize API service (from first snippet)
        env_config = EnvConfig()
        self.api_service = ApiService(env_config)
        
        # Initialize data variables (from first snippet)
        self.availableSpace = "Loading..."
        self.capacity = "Loading..."
        self.rating = "Loading..."
        self.charges = "20 Rs/Hours"  
        self.parkingName = "Loading..."
        
        self.initUI()
        self.calllemployeedetails()  # Fetch data after UI initialization

    def initUI(self):
        # Main layout with padding
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(22, 22, 22, 22)
        main_layout.setSpacing(22)
        
        # Left sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(140)
        sidebar.setStyleSheet("background-color: white; border-radius: 15px;")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_layout.setSpacing(20)

        # User icon at top
        user_icon = QLabel("👤")
        user_icon.setStyleSheet("""
            font-size: 30px;
            background-color: #3b7be9;
            border-radius: 30px;
            color: white;
            padding: 10px;
        """)
        user_icon.setFixedSize(60, 60)
        user_icon.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(user_icon, 0, Qt.AlignCenter)

        # Add stretch to push middle icons to center
        sidebar_layout.addStretch(2)  # Increased stretch

        # Middle icons (centered)
        middle_icons = []

        home_icon = HomeLabel("⏻")
        home_icon.setStyleSheet("""
            font-size: 30px;
            background-color: #e0e0e0;
            border-radius: 30px;
            color: red;
            padding: 10px;
        """)
        home_icon.setFixedSize(60, 60)
        home_icon.setAlignment(Qt.AlignCenter)
        middle_icons.append(home_icon)

        camera_icon = QLabel("📹")
        camera_icon.setStyleSheet("""
            font-size: 30px;
            background-color: #3b7be9;
            border-radius: 30px;
            color: white;
            padding: 10px;
        """)
        camera_icon.setFixedSize(60, 60)
        camera_icon.setAlignment(Qt.AlignCenter)
        middle_icons.append(camera_icon)

        mic_icon = QLabel("🎙️")
        mic_icon.setStyleSheet("""
            font-size: 30px;
            background-color: #e0e0e0;
            border-radius: 30px;
            color: white;
            padding: 10px;
        """)
        mic_icon.setFixedSize(60, 60)
        mic_icon.setAlignment(Qt.AlignCenter)
        middle_icons.append(mic_icon)

        stats_icon = QLabel("📊")
        stats_icon.setStyleSheet("""
            font-size: 30px;
            background-color: #f26e56;
            border-radius: 30px;
            color: white;
            padding: 10px;
        """)
        stats_icon.setFixedSize(60, 60)
        stats_icon.setAlignment(Qt.AlignCenter)
        middle_icons.append(stats_icon)

        # Add all middle icons to layout
        for icon in middle_icons:
            sidebar_layout.addWidget(icon, 0, Qt.AlignCenter)

        # Add another stretch below to balance
        sidebar_layout.addStretch(2)  # Increased stretch

        # User profile button at bottom
        profile = QLabel("👤")
        profile.setStyleSheet("""
            font-size: 30px; 
            color: #555555; 
            background-color: #e0e0e0; 
            border-radius: 30px;
            border: 3px solid white;
            padding: 10px;
        """)
        profile.setFixedSize(60, 60)
        profile.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(profile, 0, Qt.AlignCenter)

        main_layout.addWidget(sidebar)

        
        # Main content area
        content_area = QWidget()
        content_area.setStyleSheet("background-color: white; border-radius: 15px;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)
        
        # Header section
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 0, 10, 0)
        header_layout.setSpacing(0)
        
        # Left side - Title and date
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
       
        self.title_label = QLabel(self.parkingName)
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_layout.addWidget(self.title_label)
        
        # Date and time
        date_time_widget = QWidget()
        date_time_layout = QHBoxLayout(date_time_widget)
        date_time_layout.setContentsMargins(0, 0, 0, 120)
        date_time_layout.setSpacing(10)
        
        current_date = datetime.datetime.now().strftime("%d %b %Y")
        date_label = QLabel(current_date)
        date_label.setStyleSheet("color: #666; font-size: 16px;")
        date_time_layout.addWidget(date_label)
        
        dot_label = QLabel()
        dot_label.setFixedSize(8, 8)
        dot_label.setStyleSheet("background-color: red; border-radius: 4px;")
        date_time_layout.addWidget(dot_label)
        
        current_time = datetime.datetime.now().strftime("%H:%M")
        entry_time_label = QLabel(f"Current time {current_time}")
        entry_time_label.setStyleSheet("color: #666; font-size: 16px;")
        date_time_layout.addWidget(entry_time_label)
        date_time_layout.addStretch()
        
        title_layout.addWidget(date_time_widget)
        header_layout.addWidget(title_widget, 1)  # Give it stretch factor
        
        # Right side - Entry and Exit buttons
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(15)  # Space between buttons
        
        # Entry button - Red with rounded corners
        entry_button = QPushButton("Entry")
        entry_button.setStyleSheet("""
            QPushButton {
                background-color: #ff3b30;
                color: white;
                border-radius: 25px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #ff291f;
            }
        """)
        entry_button.setFixedHeight(50)
        entry_button.setFixedWidth(200)
        entry_button.clicked.connect(self.handle_entry_click)
        buttons_layout.addWidget(entry_button)

        # Exit button - Green with rounded corners
        exit_button = QPushButton("Exit")
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #0e9f51;
                color: white;
                border-radius: 25px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #0c8a46;
            }
        """)
        exit_button.setFixedHeight(50)
        exit_button.setFixedWidth(200)
        exit_button.clicked.connect(self.handle_exit_click)
        buttons_layout.addWidget(exit_button)
        
        # Align buttons with the title
        buttons_widget.setFixedHeight(80)
        header_layout.addWidget(buttons_widget, 0, Qt.AlignRight | Qt.AlignTop)
        
        content_layout.addWidget(header_widget)
        content_layout.addSpacing(-10)
        
        # Main illustration - Parking image
        parking_image_frame = QFrame()
        parking_image_layout = QVBoxLayout(parking_image_frame)
        parking_image_layout.setContentsMargins(0, 0, 0, 0)
        parking_image_layout.setAlignment(Qt.AlignCenter)
        
        parking_image = QLabel()
        # Try to load the title image from assets as in the first snippet
        try:
            placeholder_image = QPixmap('assets/secondpage.png')
        except:
            # Fallback to a placeholder if image not found
            placeholder_image = QPixmap(600, 400)
            placeholder_image.fill(Qt.lightGray)
        
        parking_image.setPixmap(placeholder_image)
        parking_image.setScaledContents(True)
        parking_image.setStyleSheet("border-radius: 15px;")
        parking_image.setFixedHeight(400)
        parking_image.setFixedWidth(1100)
        # parking_image.setAlignment(Qt.AlignTop)
        parking_image_layout.addWidget(parking_image)
        
        content_layout.addWidget(parking_image_frame)
        content_layout.addSpacing(0)
        
        # Dashboard cards section
        dashboard_widget = QWidget()
        dashboard_layout = QHBoxLayout(dashboard_widget)
        dashboard_layout.setContentsMargins(10, 10, 10, 10)  
        dashboard_layout.setSpacing(10)
        
        # Function to create dashboard cards
        def create_dashboard_card(title, subtitle, value_var):
            card = QFrame()
            card.setStyleSheet("""
                background-color:#369FFF ;
                border-radius: 25px;
                color: white;
            """)
            
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 20, 15, 20)
            
            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 16, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(title_label)
            
            subtitle_label = QLabel(subtitle)
            subtitle_label.setFont(QFont("Arial",12))
            subtitle_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(subtitle_label)
            
            value_label = QLabel(str(value_var))
            value_label.setFont(QFont("Arial", 22, QFont.Bold))
            value_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(value_label)
            
            return card, value_label  # Return the card and label for updating later
        
        # Create dashboard cards with the values from first snippet
        self.space_available_card, self.availableSpace_label = create_dashboard_card(
            "Space Available", "Cars", self.availableSpace)
        dashboard_layout.addWidget(self.space_available_card)
        
        self.parking_charges_card, self.charges_label = create_dashboard_card(
            "Parking Charges", "Per Hour", self.charges)
        dashboard_layout.addWidget(self.parking_charges_card)
        
        self.rating_card, self.rating_label = create_dashboard_card(
            "Our Service", "Rating", self.rating)
        dashboard_layout.addWidget(self.rating_card)
        
        self.total_capacity_card, self.capacity_label = create_dashboard_card(
            "Total capacity", "Cars", self.capacity)
        dashboard_layout.addWidget(self.total_capacity_card)
        
        content_layout.addWidget(dashboard_widget)
        main_layout.addWidget(content_area, 1)

    def navigate_to_home(self):
        """Navigate back to the home/previous page"""
        from new_app import ParkKeyUI
        # You can put any code here to navigate to the previous page
        self.show_popup("Navigating to home page...")
        
        self.home_window = ParkKeyUI()
        self.home_window.show()
        self.close()

    # Functions from the first snippet
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
        
        # Update the instance variables
        self.availableSpace = parkingdetres.get('availableSpace', "N/A")
        self.capacity = parkingdetres.get('totalSpace', "N/A")
        self.rating = parkingdetres.get('rating', "N/A")
        self.parkingName = parkingdetres.get('parkingName', "N/A")

        # Update the UI labels with the new data
        self.capacity_label.setText(str(self.capacity))
        self.availableSpace_label.setText(str(self.availableSpace))
        self.rating_label.setText(str(self.rating))
         # Apply capitalization when updating the title
        parkingName = self.parkingName.strip()
        self.title_label.setText(parkingName.title())
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingApp()
    window.show()
    sys.exit(app.exec_())