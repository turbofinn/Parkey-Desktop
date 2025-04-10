from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFrame, QScrollArea, QMessageBox,
                             QListWidget, QListWidgetItem, QSizePolicy, QSpacerItem, QMenu)
from PyQt5.QtGui import QFont, QColor, QPixmap, QImage, QPainter
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon
import sys
import cv2
import numpy as np
import tensorflow as tf
import pytesseract
import re
import time  
import os
from api.ApiService import ApiService 
from api.ApiService import EnvConfig
import datetime
import json
# from middleui import ParkingApp 

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Use the resource_path function to locate the model file
model_path = resource_path("models/num_plate.pb")

save_directory = r'imges'

if not os.path.exists(save_directory):
    os.makedirs(save_directory)

class LogoutLabel(QLabel):
    """Custom QLabel class for home icon that emits a signal when clicked"""
    def __init__(self, text):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)  # Set cursor to pointing hand
        
    def mousePressEvent(self, event):
        # Override the mouse press event to handle click
        if event.button() == Qt.LeftButton:
            # Call the slot function directly
            if hasattr(self.parent().parent().parent(), 'navigate_to_login'):
                self.parent().parent().parent().navigate_to_login()
                self.close()
        super().mousePressEvent(event)


class CameraLabel(QLabel):
    """Custom QLabel class that emits a signal when clicked"""
    def __init__(self, text):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)  # Set cursor to pointing hand
        
    def mousePressEvent(self, event):
        # Override the mouse press event to emit our custom signal
        if event.button() == Qt.LeftButton:
            # Call the slot function directly
            if hasattr(self.parent().parent().parent(), 'show_camera_options'):
                self.parent().parent().parent().show_camera_options(event.globalPos())
        super().mousePressEvent(event)
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


class ParkingAppSplash(QMainWindow):
    def __init__(self):
        super().__init__()
        QApplication.instance().setStyleSheet("""
            QToolTip {
                background-color: #0674B4;
                color: white;
                border: 1px solid #0674B4;
                border-radius: 4px;
                padding: 3px;
                font-weight: bold;
            }
        """)
        self.setWindowTitle("Raipur Railways Parking")
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        # self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #0674B4;")
        
        # Initialize variables from original code
        self.cap = None  
        self.timer = None  
        self.sess = None
        self.input_tensor = None
        self.detection_boxes = None
        self.detection_scores = None
        self.detection_classes = None
        self.num_detections = None
        self.detected_number_plate = ""
        self.entry_time = ""
        self.current_number_plate = ""
        self.entered_mobile_number = ""
        self.current_camera_index = 0  # Default to webcam (index 0)
        self.env_config = EnvConfig()
        self.api_service = ApiService(self.env_config)
        
        self.initUI()

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
        user_icon = QLabel()
        # Load your image (replace with your actual image path)
        img_path = resource_path("assets/titlepage.png")
        pixmap = QPixmap(img_path)  # e.g., "assets/profile.png"
        # Create circular mask for rounded effect
        mask = QPixmap(pixmap.size())
        mask.fill(Qt.transparent)
        painter = QPainter(mask)
        painter.setBrush(Qt.white)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(mask.rect(), 30, 30)  # Match your 30px border-radius
        painter.end()

        # Apply the mask and styling
        pixmap.setMask(mask.createMaskFromColor(Qt.transparent))
        user_icon.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # 40x40 to account for padding
        user_icon.setStyleSheet("""
            background-color: #e0e0e0;
            border-radius: 30px;
            padding: 10px;
        """)

        # Keep the rest the same
        user_icon.setFixedSize(60, 60)
        user_icon.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(user_icon, 0, Qt.AlignCenter)

        sidebar_layout.addStretch(1)  # Adjusted stretch to balance layout

        # Middle icons (centered)
        middle_icons_layout = QVBoxLayout()
        middle_icons_layout.setSpacing(20)

        home_icon = HomeLabel("🏠")
        home_icon.setStyleSheet("""
            font-size: 30px;
            background-color: #e0e0e0;
            border-radius: 30px;
            color: white;
            padding: 10px;
        """)
        home_icon.setFixedSize(60, 60)
        home_icon.setAlignment(Qt.AlignCenter)
        middle_icons_layout.addWidget(home_icon, 0, Qt.AlignCenter)

        # Replace the QLabel with our custom CameraLabel class
        camera_icon = CameraLabel("📹")
        camera_icon.setStyleSheet("""
            font-size: 30px;
            background-color: #e0e0e0;
            border-radius: 30px;
            color: white;
            padding: 10px;
        """)
        camera_icon.setFixedSize(60, 60)
        camera_icon.setAlignment(Qt.AlignCenter)
        middle_icons_layout.addWidget(camera_icon, 0, Qt.AlignCenter)

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
        middle_icons_layout.addWidget(mic_icon, 0, Qt.AlignCenter)

        stats_icon = QLabel("📊")
        stats_icon.setStyleSheet("""
            font-size: 30px;
            background-color: #e0e0e0;
            border-radius: 30px;
            color: white;
            padding: 10px;
        """)
        stats_icon.setFixedSize(60, 60)
        stats_icon.setAlignment(Qt.AlignCenter)
        middle_icons_layout.addWidget(stats_icon, 0, Qt.AlignCenter)

        sidebar_layout.addStretch(2)  # Ensure centering
        sidebar_layout.addLayout(middle_icons_layout)  # Add middle icons as a separate layout
        sidebar_layout.addStretch(2)  # Ensure centering

        # User profile button at bottom
        profile = LogoutLabel("🔓")
        profile.setStyleSheet("""
            font-size: 30px; 
            color: red; 
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
        content_layout.setContentsMargins(15, 10, 15, 10)
        content_layout.setSpacing(20)
        
        # Top header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(60, 0, 20, 0)
        
        title_label = QLabel("Raipur Railways Parking")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        header_layout.addWidget(title_label)
        

        
        content_layout.addWidget(header_widget)
        
        # Date and entry time display
        date_time_widget = QWidget()
        date_time_layout = QHBoxLayout(date_time_widget)
        date_time_layout.setContentsMargins(62, 0, 0, 0)
        date_time_layout.setSpacing(5)
        
        date_label = QLabel(datetime.datetime.now().strftime("%d %b %Y"))
        date_label.setStyleSheet("color: #666; font-size: 14px;")
        date_time_layout.addWidget(date_label)
        
        dot_label = QLabel()
        dot_label.setFixedSize(10, 10)
        dot_label.setStyleSheet("background-color: red; border-radius: 5px;")
        date_time_layout.addWidget(dot_label)
        
        self.entry_time_display = QLabel("Entry time --:--")
        self.entry_time_display.setStyleSheet("color: #666; font-size: 14px;")
        date_time_layout.addWidget(self.entry_time_display)
        date_time_layout.addStretch()
        
        content_layout.addWidget(date_time_widget)
        
        # Live camera feed
        camera_frame = QFrame()
        camera_layout = QVBoxLayout(camera_frame)
        camera_layout.setContentsMargins(0, 0, 0, 0)

        # Create a container for the camera and overlay
        camera_container = QWidget()
        camera_container_layout = QHBoxLayout(camera_container)
        camera_container_layout.setContentsMargins(0, 0, 0, 0)

        # Vehicle image (camera feed)
        self.vehicle_image = QLabel()
        self.vehicle_image.setAlignment(Qt.AlignCenter)
        self.vehicle_image.setStyleSheet("""
            background-color: black;
            border: 8px solid white;
            border-radius: 16px;
        """)
        self.vehicle_image.setFixedSize(1000, 550)
        self.vehicle_image.setScaledContents(True)

        # Add the vehicle image to the container
        camera_container_layout.addWidget(self.vehicle_image)

        # Add the container to the main camera layout
        camera_layout.addWidget(camera_container)

        # Add status label to vehicle image
        self.status_label = QLabel(self.vehicle_image)
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(100, 100, 100, 0.7);  /* Semi-transparent gray */
                border-radius: 4px;
                font-size: 12px;
                padding: 5px;
                font-weight:600;                        
                border : none;
            }
        """)
        self.status_label.setText("Status: Ready")
        self.status_label.adjustSize()
        self.status_label.move(10, self.vehicle_image.height() - self.status_label.height() - 10)

        content_layout.addWidget(camera_frame)

        plate_frame = QFrame()
        plate_frame.setFixedSize(990, 80)
        plate_frame.setStyleSheet("background-color: #0674B4; border-radius: 6px;")
        plate_layout = QHBoxLayout(plate_frame)
        plate_layout.setContentsMargins(15, 10, 15, 10)
        plate_layout.setSpacing(30)  # Increased spacing between elements

        # Add the detected image display to the left
        self.detected_image = QLabel()
        self.detected_image.setFixedSize(200, 60)
        self.detected_image.setStyleSheet("background-color: white; border-radius: 4px;")
        self.detected_image.setAlignment(Qt.AlignCenter)
        plate_layout.addWidget(self.detected_image, alignment=Qt.AlignLeft)

        # Create horizontal layout to hold the label and emoji buttons
        vehicle_type_layout = QHBoxLayout()
        vehicle_type_layout.setContentsMargins(0, 0, 0, 0)
        vehicle_type_layout.setSpacing(0)  # Reduced spacing between label and buttons

        # Create a container widget for the entire vehicle type section
        vehicle_type_container = QWidget()
        vehicle_type_container.setFixedWidth(380)  # Set your desired fixed width here
        vehicle_type_container.setLayout(vehicle_type_layout)

        # Vehicle type label
        vehicle_type_label = QLabel("Vehicle Type:")
        vehicle_type_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        vehicle_type_layout.addWidget(vehicle_type_label, alignment=Qt.AlignLeft)

        # Widget + layout for the buttons
        radio_buttons_widget = QWidget()
        radio_buttons_layout = QHBoxLayout(radio_buttons_widget)
        radio_buttons_layout.setContentsMargins(0, 0, 0, 0)
        radio_buttons_layout.setSpacing(20)  # Increased spacing between buttons

        # Create the emoji buttons
        self.bike_radio = QPushButton("🏍️")
        self.car_radio = QPushButton("🚗")
        self.truck_radio = QPushButton("🚚")
        self.cycle_radio = QPushButton("🚲")

        # Tooltips
        self.bike_radio.setToolTip("Bike")
        self.car_radio.setToolTip("Car")
        self.truck_radio.setToolTip("Truck")
        self.cycle_radio.setToolTip("Cycle")

        # Button style
        radio_style = """
            QPushButton {
                background-color: white;
                border-radius: 25px;
                padding: 5px;
                font-size: 24px;
                width: 50px;
                height: 50px;
                color: #0674B4;
                border: 2px solid #e0e0e0;
            }
            QPushButton:checked {
                background-color:#90EE90;
                color: white;
                border: 2px solid white;
            }
        """
        

        # Apply style, make checkable, add to layout
        for btn in [self.bike_radio, self.car_radio, self.truck_radio, self.cycle_radio]:
            btn.setStyleSheet(radio_style)
            btn.setCheckable(True)
            btn.setFixedSize(50, 50)
            radio_buttons_layout.addWidget(btn)
            btn.clicked.connect(self.handle_vehicle_type_selection)

        # Default selected button
        self.bike_radio.setChecked(True)
        self.current_vehicle_type = "Bike"

        # Add the buttons beside the label
        vehicle_type_layout.addWidget(radio_buttons_widget, alignment=Qt.AlignLeft)


        # Add the vehicle type widget to the main plate layout
        plate_layout.addWidget(vehicle_type_container)

        content_layout.addWidget(plate_frame, alignment=Qt.AlignCenter)
        # content_layout.addWidget(plate_frame, alignment=Qt.AlignCenter)

        
        # Input fields section
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #0674B4; border-radius: 6px;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 10, 15, 10)
        input_frame.setFixedSize(990, 80)
        input_layout.setSpacing(40)  # Increased spacing for better separation

        # Set a fixed width for all input fields
        input_field_width = 250  

        # Number plate input
        plate_widget = QWidget()
        plate_layout = QVBoxLayout(plate_widget)
        plate_layout.setContentsMargins(0, 0, 0, 0)
        plate_layout.setSpacing(5)

        plate_label = QLabel("Number Plate:")
        plate_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        plate_layout.addWidget(plate_label)

        self.left_box_input = QLineEdit()
        self.left_box_input.setFixedSize(input_field_width, 36)
        self.left_box_input.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px 8px; font-size: 16px;")
        plate_layout.addWidget(self.left_box_input)

        input_layout.addWidget(plate_widget)
        self.left_box_input.textChanged.connect(self.handle_number_plate_edit)

        # Mobile number input
        mobile_widget = QWidget()
        mobile_layout = QVBoxLayout(mobile_widget)
        mobile_layout.setContentsMargins(0, 0, 0, 0)
        mobile_layout.setSpacing(5)

        mobile_label = QLabel("Mobile Number:")
        mobile_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        mobile_layout.addWidget(mobile_label)

        self.right_box_input = QLineEdit()
        self.right_box_input.setFixedSize(input_field_width, 36)
        self.right_box_input.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px 8px; font-size: 16px;")
        mobile_layout.addWidget(self.right_box_input)

        input_layout.addWidget(mobile_widget)

        # Entry charges display
        charges_widget = QWidget()
        charges_layout = QVBoxLayout(charges_widget)
        charges_layout.setContentsMargins(0, 0, 0, 0)
        charges_layout.setSpacing(5)

        charges_label = QLabel("Entry Charges:")
        charges_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        charges_layout.addWidget(charges_label)

        self.entry_fees_display = QLabel()
        self.entry_fees_display.setFixedSize(input_field_width, 36)
        self.entry_fees_display.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px 8px; font-size: 16px; font-weight: bold;")
        self.entry_fees_display.setAlignment(Qt.AlignCenter)
        charges_layout.addWidget(self.entry_fees_display)

        input_layout.addWidget(charges_widget)

        content_layout.addWidget(input_frame, alignment=Qt.AlignCenter)


        # Action buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(10, 10, 10, 5)
        button_layout.setSpacing(20)

        # Button style function
        def get_button_style(bg_color):
            return f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: white;
                    border-radius: 22px;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 12px;
                }}
                QPushButton:hover {{
                    background-color: {bg_color[:-1]}D;
                }}
                QPushButton:pressed {{
                    background-color: {bg_color[:-1]}A;
                }}
                QPushButton:disabled {{
                    background-color: #888888;
                }}
            """

        self.automatic_button = QPushButton("Start")
        self.automatic_button.setFixedSize(150, 45)
        self.automatic_button.setStyleSheet(get_button_style("#007bff"))
        button_layout.addWidget(self.automatic_button)

        self.entry_button = QPushButton("Park Vehicle")
        self.entry_button.setFixedSize(150, 45)
        self.entry_button.setStyleSheet(get_button_style("#1a8539"))
        button_layout.addWidget(self.entry_button)

        self.manual_button = QPushButton("Stop")
        self.manual_button.setFixedSize(150, 45)
        self.manual_button.setStyleSheet(get_button_style("#dc3545"))
        button_layout.addWidget(self.manual_button)

        content_layout.addWidget(button_widget)
        main_layout.addWidget(content_area, 1)

        # Right sidebar for recent entries and exits
         # Modifications to the right sidebar
        vehicle_sidebar = QWidget()
        vehicle_sidebar.setFixedWidth(550)
        vehicle_sidebar.setStyleSheet("background-color: white; border-radius: 15px;")
        vehicle_layout = QVBoxLayout(vehicle_sidebar)
        vehicle_layout.setContentsMargins(10, 10, 10, 10)
        vehicle_layout.setSpacing(10)
         
        # Recent Entry section
        recent_entry_label = QLabel("Recent Entry")
        recent_entry_label.setFont(QFont("Arial", 14, QFont.Bold))
        recent_entry_label.setAlignment(Qt.AlignCenter)
        recent_entry_label.setStyleSheet("color: #666; margin-bottom: 5px; padding: 3px;")
        vehicle_layout.addWidget(recent_entry_label)
        
        self.recent_entry_list = QListWidget()
        self.recent_entry_list.setStyleSheet("""
        QListWidget {
            border: none;
            background-color: transparent;
            font-size: 14px;
        }
        QListWidget::item {
            border-bottom: 1px solid #ddd;
            padding: 8px 5px;
        }
        QListWidget::item:first-child {
            border-top: 1px solid #ddd;
        }
    """)
        vehicle_layout.addWidget(self.recent_entry_list)
        
        # New Message Log section
        message_log_label = QLabel("Message Log")
        message_log_label.setFont(QFont("Arial", 14, QFont.Bold))
        message_log_label.setAlignment(Qt.AlignCenter)
        message_log_label.setStyleSheet("color: #666; margin-bottom: 5px; padding: 3px;")
        vehicle_layout.addWidget(message_log_label)
        
        self.message_log_list = QListWidget()
        self.message_log_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                font-size: 14px;
            }
            QListWidget::item {
                border-bottom: 1px solid #ddd;
                padding: 5px;
            }
            QListWidget::item:first-child {
                border-top: 1px solid #ddd;
            }
        """)
        vehicle_layout.addWidget(self.message_log_list)
        
        main_layout.addWidget(vehicle_sidebar)
        
        # Connect button events
        self.automatic_button.clicked.connect(self.start_camera)
        self.manual_button.clicked.connect(self.stop_camera)
        self.entry_button.clicked.connect(self.submit_entry)
        self.right_box_input.textChanged.connect(self.store_mobile_number)
        # At the end of initUI method
        self.update_recent_entries()
        
    def handle_vehicle_type_selection(self):
        """Handle mutual exclusion for vehicle type emoji buttons"""
        sender = self.sender()
        
        # First check if any button is currently checked
        any_checked = False
        for btn in [self.bike_radio, self.car_radio, self.truck_radio, self.cycle_radio]:
            if btn != sender and btn.isChecked():
                any_checked = True
                btn.setChecked(False)  # Uncheck the previously selected button
        
        # Always set the sender to checked
        sender.setChecked(True)
        
        # Store the selected vehicle type
        if sender == self.bike_radio:
            self.current_vehicle_type = "Bike"
        elif sender == self.car_radio:
            self.current_vehicle_type = "Car"
        elif sender == self.truck_radio:
            self.current_vehicle_type = "Truck"
        elif sender == self.cycle_radio:
            self.current_vehicle_type = "Cycle"
        
        print(f"Vehicle type selected: {self.current_vehicle_type}")
        # Update entry fees based on vehicle type if needed
        # self.update_entry_fees_for_vehicle_type()
    def update_status(self, message):
        """Update the status text at the bottom of the camera feed"""
        self.status_label.setText(f"Status: {message}")
        self.status_label.adjustSize()
        self.status_label.move(10, self.vehicle_image.height() - self.status_label.height() - 10)
        self.status_label.show()

    def navigate_to_login(self):
        """Navigate back to the home/previous page"""
        from new_app import ParkKeyUI
        # You can put any code here to navigate to the previous page
        # self.show_popup("Navigating to home page...")
        
        self.home_window = ParkKeyUI()
        self.home_window.show()
        self.close()

    def navigate_to_home(self):
        """Navigate back to the home/previous page"""
        from middleui import ParkingApp
        # You can put any code here to navigate to the previous page
        self.show_popup("Navigating to home page...")
        
        self.home_window = ParkingApp()
        self.home_window.show()
        self.close() 

    def show_camera_options(self, position):
        """Show camera selection popup menu when camera icon is clicked"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #3b7be9;
                color: white;
            }
        """)
        
        # Add menu options
        webcam_action = menu.addAction("Webcam (Default)")
        external_camera_action = menu.addAction("External Camera")
        
        # Show the menu at the cursor position
        action = menu.exec_(position)
        
        # Handle the selected action
        if action == webcam_action:
            self.current_camera_index = 0
            self.show_popup("Selected webcam as camera source")
            if self.cap and self.cap.isOpened():
                self.stop_camera()
                self.start_camera()
        elif action == external_camera_action:
            self.current_camera_index = 1  # Typically external cameras get index 1
            self.show_popup("Selected external camera as camera source")
            if self.cap and self.cap.isOpened():
                self.stop_camera()
                self.start_camera()

    def keyPressEvent(self, event):
        """Close the camera on pressing 'Q'"""
        if event.key() == Qt.Key_Q:
            self.stop_camera()

    def start_camera(self):
        """Start the camera and begin detecting number plates."""
        self.update_status("Starting camera...")
        # Change button text to indicate operation in progress
        self.automatic_button.setText("Starting...")
        self.automatic_button.setEnabled(False)
        
        # Process events to update the UI immediately
        QApplication.processEvents()
        
        self.cap = cv2.VideoCapture(self.current_camera_index)  # Use the selected camera index
        
        if not self.cap.isOpened():
            print(f"Error: Cannot access camera with index {self.current_camera_index}")
            self.show_popup(f"Camera with index {self.current_camera_index} not available. Try ancycle camera.")
            self.automatic_button.setText("Start")
            self.automatic_button.setEnabled(True)
            self.update_status("Camera failed to start")
            return

        # Load the TensorFlow model
        with tf.io.gfile.GFile(model_path, 'rb') as f:
            graph_def = tf.compat.v1.GraphDef()
            graph_def.ParseFromString(f.read())

        # Create a TensorFlow session and import the graph
        self.sess = tf.compat.v1.Session()
        tf.import_graph_def(graph_def, name="")
        self.show_popup(f"Camera {self.current_camera_index} started successfully")

        # Get tensor references
        self.input_tensor = self.sess.graph.get_tensor_by_name('image_tensor:0')
        self.detection_boxes = self.sess.graph.get_tensor_by_name('detection_boxes:0')
        self.detection_scores = self.sess.graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.sess.graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.sess.graph.get_tensor_by_name('num_detections:0')

        # Set up a QTimer to update the vehicle image every frame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame_with_detection)
        self.timer.start(30) 
        
        # Enable entry button after camera is started
        self.entry_button.setEnabled(True)
        
        # Reset button text
        self.automatic_button.setText("Start")
        self.automatic_button.setEnabled(True)
        self.update_status("Live")

    def stop_camera(self):
        """Stop the camera feed and close OpenCV windows."""
        self.update_status("Stopping camera...")
        # Change button text to indicate operation in progress
        self.manual_button.setText("Stopping...")
        self.manual_button.setEnabled(False)
        
        # Process events to update the UI immediately
        QApplication.processEvents()
        
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        
        if hasattr(self, 'cap') and self.cap is not None and self.cap.isOpened():
            self.cap.release()
            self.cap = None  
            print("Camera stopped.")
        else:
            print("Camera was not running.")

        if hasattr(self, 'sess'):
            self.sess.close()  
            print("TensorFlow session closed.")
        self.show_popup(f"Camera {self.current_camera_index} stopped successfully")
        
        # Only clear camera-related fields
        self.detected_image.clear()
        self.left_box_input.clear()
        self.right_box_input.clear()
        self.entry_fees_display.clear()
        self.entry_time_display.setText("Entry time --:--")
        for btn in [self.car_radio, self.truck_radio, self.cycle_radio]:
            btn.setChecked(False)
        self.bike_radio.setChecked(True)
        self.current_vehicle_type = "Bike"
        cv2.destroyAllWindows()
        
        # Reset button text
        self.manual_button.setText("Stop")
        self.manual_button.setEnabled(True)
        self.update_status("Camera stopped")

    def update_frame_with_detection(self):
        """Capture a frame, run number plate detection, and display the result."""
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Failed to grab frame")
            self.timer.stop()
            self.cap.release()
            return

        # Preprocess the frame for the model
        input_frame = cv2.resize(frame, (300, 300))  
        input_frame = np.expand_dims(input_frame, axis=0) 

        # Run inference
        outputs = self.sess.run(
            [self.num_detections, self.detection_boxes, self.detection_scores, self.detection_classes],
            feed_dict={self.input_tensor: input_frame}
        )

        # Process the predictions
        num_detected = int(outputs[0][0])
        for i in range(num_detected):
            score = outputs[2][0][i]
            if score > 0.5:  
                box = outputs[1][0][i]

                # Convert box coordinates to pixel values
                h, w, _ = frame.shape
                y1, x1, y2, x2 = int(box[0] * h), int(box[1] * w), int(box[2] * h), int(box[3] * w)

                # Draw the bounding box and label before OCR
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "Processing OCR...", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Crop the region of interest (ROI)
                roi = frame[y1:y2, x1:x2]

                try:
                    if roi.size > 0:
                        # Preprocess the ROI for Tesseract
                        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                        roi_thresh = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

                        # Perform OCR with Tesseract
                        custom_config = r'--oem 3 --psm 6'  
                        text = pytesseract.image_to_string(roi_thresh, config=custom_config)

                        cleaned_text = re.sub(r'[^A-Za-z0-9]', '', text)
                        pattern = r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$'
                        
                        if re.match(pattern, cleaned_text):
                            
                            DetectedNumberPlate = cleaned_text.strip() 
                            filename = f"{save_directory}/plate_{time.time()}.jpg"
                            cv2.imwrite(filename, roi) 
                            self.update_detected_image(filename)
                          
                            self.update_vehicle_details(DetectedNumberPlate)
                            timing = datetime.datetime.now().strftime("%I:%M %p")
                            self.update_entry_time(timing)  
                            self.update_mobile_number(DetectedNumberPlate)
                            self.show_popup(f"Number plate detected: {DetectedNumberPlate}")


                    else:
                        print("Ignored Invalid ROI due to size 0")
                except Exception as e:
                    print(f"Error with OCR: {e}")
        

        # Convert the frame to RGB format for PyQt
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.vehicle_image.setPixmap(pixmap.scaled(self.vehicle_image.width(), self.vehicle_image.height(), Qt.KeepAspectRatio))

    def update_detected_image(self, image_path):
        """Update the detected image display in the UI."""
        pixmap = QPixmap(image_path)
        self.detected_image.setPixmap(pixmap.scaled(self.detected_image.width(), self.detected_image.height(), Qt.KeepAspectRatio))
        self.detected_image.setAlignment(Qt.AlignCenter)

    def update_vehicle_details(self, number_plate):
        """Update the verify vehicle details input field with the detected number plate."""
        self.detected_number_plate = number_plate  # Store the originally detected plate
        self.current_number_plate = number_plate   # Initial value of current plate is same as detected
        self.left_box_input.setText(self.current_number_plate)


    def handle_number_plate_edit(self):
        """Handle changes to the number plate input field"""
        edited_text = self.left_box_input.text().strip()
        
        # Don't process if field is being cleared or is empty
        if not edited_text:
            return
            
        if edited_text != self.current_number_plate:
            self.current_number_plate = edited_text
            
            # Only show message if we had a previous detected plate
            if self.detected_number_plate:
                self.show_popup("Number plate edited manually. Checking database...")
            
            # Clear related fields that would need to be recalculated
            self.entry_fees_display.clear()
            
            # Try to fetch vehicle details with the new plate number
            if len(edited_text) >= 6:  # Only try if the plate number seems long enough
                try:
                    self.update_mobile_number(edited_text)
                except Exception as e:
                    print(f"Error fetching updated vehicle details: {str(e)}")
                    self.show_popup("Please enter mobile number manually")

    def update_entry_time(self, timing):
        self.entry_time = timing
        self.entry_time_display.setText(f"Entry time {timing}")

    
    def update_mobile_number(self, number_plate):
        try:
            # Use the current_number_plate instead of the parameter
            vehicle_no = str(self.current_number_plate)
            response_data = self.api_service.getVehicleDetails(vehicle_no)  

            print("API Response:", response_data)

            if response_data:
                if 'errorMessage' in response_data:
                    # Vehicle not found in the system
                    self.show_popup("Vehicle not present in the system.\nPlease enter the mobile number manually.")
                    self.right_box_input.clear()
                    self.entry_fees_display.clear()
                    self.entered_mobile_number = ""
                    self.right_box_input.setFocus()
                    try:
                        self.right_box_input.textChanged.disconnect()
                    except TypeError:
                        pass
                    self.right_box_input.textChanged.connect(self.store_mobile_number)
                else:
                    # Vehicle found - Populate mobile number and entry fees
                    mobile_number = response_data.get("mobileNo", "")
                    entry_fee = str(response_data.get('totalParkingCharges', '0'))
                    
                    # Update UI fields
                    self.entered_mobile_number = mobile_number
                    self.right_box_input.setText(self.entered_mobile_number)
                    self.entry_fees_display.setText(f"{entry_fee} Rs")

            else:
                self.show_popup("No data received from server. Please try again.")

        except Exception as e:
            print("Error fetching vehicle details:", str(e))
            self.show_popup(f"An error occurred: {str(e)}")


    # def update_recent_entries(self):
    #     try:
    #         # Clear existing items
    #         self.recent_entry_list.clear()
            
    #         # Get employee ID
    #         employee_id = self.env_config.get_employeeID()
    #         if not employee_id:
    #             self.show_popup("Employee ID not set")
    #             return

    #         # Get recent entries from API
    #         response = self.api_service.get_parking_space_stats(employee_id)
    #         print("API Response:", response)
            
    #         if not response or 'entryVehicleList' not in response:
    #             self.recent_entry_list.addItem("No recent entries found")
    #             return

    #         # Sort entries by date (newest first)
    #         entries = sorted(
    #             response['entryVehicleList'],
    #             key=lambda x: datetime.datetime.strptime(
    #                 x['updatedDate'].replace('\u202f', ' '),
    #                 "%b %d, %Y, %I:%M:%S %p"
    #             ),
    #             reverse=True
    #         )

    #         # Add entries to the list (show last 5 entries)
    #         # 
    #         for entry in entries[:5]:
    #             vehicle_no = entry.get('vehicleNo', 'N/A')
    #             mobile_no = entry.get('customerNo', 'N/A')
    #             duration = entry.get('parkingDuration', 'N/A')
    #             charges = entry.get('parkingCharge', 'N/A')
                
    #             # Create the item widget
    #             item_widget = QWidget()
    #             layout = QHBoxLayout(item_widget)
                
    #             # Left side - Vehicle and Mobile
    #             left_label = QLabel(f"{vehicle_no}\nMobile: {mobile_no[:4]}XXXXX{mobile_no[-1:]}")
    #             left_label.setFont(QFont("Arial", 11))
                
    #             # Right side - Duration and Charges with labels
    #             right_widget = QWidget()
    #             right_layout = QVBoxLayout(right_widget)
                
    #             duration_label = QLabel(f"Duration: {duration}")
    #             charges_label = QLabel(f"Charges: ₹{charges}")
                
    #             for label in [duration_label, charges_label]:
    #                 label.setFont(QFont("Arial", 10))
    #                 label.setStyleSheet("color: #0674B4;")
    #                 right_layout.addWidget(label)
                
    #             right_layout.setSpacing(5)  # Increased spacing between duration and charges
    #             right_layout.setContentsMargins(0, 0, 10, 0)
                
    #             # Add widgets to main layout
    #             layout.addWidget(left_label)
    #             layout.addStretch()
    #             layout.addWidget(right_widget)
    #             layout.setContentsMargins(10, 12, 10, 12)  # Increased vertical padding
                
    #             # Create list item
    #             item = QListWidgetItem()
    #             # Set a fixed height for each item
    #             custom_size = QSize(item_widget.sizeHint().width(), 80)  # Increased height to 80px
    #             item.setSizeHint(custom_size)
    #             self.recent_entry_list.addItem(item)
    #             self.recent_entry_list.setItemWidget(item, item_widget)

    #         # Add spacing between items in the list
    #         self.recent_entry_list.setSpacing(5)
    #     except Exception as e:
    #         self.show_popup(f"Error loading entries: {str(e)}")
    #         print(f"Error in update_recent_entries: {e}")
    def update_recent_entries(self):
        try:
            # Clear existing items
            self.recent_entry_list.clear()

            # Get employee ID
            employee_id = self.env_config.get_employeeID()
            if not employee_id:
                self.show_popup("Employee ID not set")
                return

            # Get recent entries from API
            response = self.api_service.get_parking_space_stats(employee_id)
            print("API Response:", response)

            if not response or 'entryVehicleList' not in response:
                self.recent_entry_list.addItem("No recent entries found")
                return

            # Sort entries by date (newest first)
            entries = sorted(
                response['entryVehicleList'],
                key=lambda x: datetime.datetime.strptime(
                    x['updatedDate'].replace('\u202f', ' '),
                    "%b %d, %Y, %I:%M:%S %p"
                ),
                reverse=True
            )

            # Function to parse duration like "6 days and 1 hours" to "145:00:00 hrs"
            import re

            def parse_duration_to_hms(duration_str):
                try:
                    days = hours = minutes = seconds = 0

                    if 'day' in duration_str:
                        day_match = re.search(r'(\d+)\s*day', duration_str)
                        if day_match:
                            days = int(day_match.group(1))

                    if 'hour' in duration_str:
                        hour_match = re.search(r'(\d+)\s*hour', duration_str)
                        if hour_match:
                            hours = int(hour_match.group(1))

                    if 'minute' in duration_str:
                        min_match = re.search(r'(\d+)\s*minute', duration_str)
                        if min_match:
                            minutes = int(min_match.group(1))

                    if 'second' in duration_str:
                        sec_match = re.search(r'(\d+)\s*second', duration_str)
                        if sec_match:
                            seconds = int(sec_match.group(1))

                    total_hours = days * 24 + hours
                    return f"{total_hours:02d}:{minutes:02d}:{seconds:02d} hrs"
                except:
                    return "Invalid Duration"

            # Add entries to the list (show last 5 entries)
            for entry in entries[:5]:
                vehicle_no = entry.get('vehicleNo', 'N/A')
                mobile_no = entry.get('customerNo', 'N/A')
                charges = entry.get('parkingCharge', 'N/A')

                # Format the duration
                raw_duration = entry.get('parkingDuration')
                duration = parse_duration_to_hms(raw_duration) if raw_duration else 'N/A'

                # Create the item widget
                item_widget = QWidget()
                layout = QHBoxLayout(item_widget)

                # Left side - Vehicle and Mobile
                left_label = QLabel(f"{vehicle_no}\nMobile: {mobile_no[:4]}XXXXX{mobile_no[-1:]}")
                left_label.setFont(QFont("Arial", 11))

                # Right side - Duration and Charges with labels
                right_widget = QWidget()
                right_layout = QVBoxLayout(right_widget)

                duration_label = QLabel(f"Duration: {duration}")
                charges_label = QLabel(f"Charges: ₹{charges}")

                for label in [duration_label, charges_label]:
                    label.setFont(QFont("Arial", 10))
                    label.setStyleSheet("color: #0674B4;")
                    right_layout.addWidget(label)

                right_layout.setSpacing(5)
                right_layout.setContentsMargins(0, 0, 10, 0)

                # Add widgets to main layout
                layout.addWidget(left_label)
                layout.addStretch()
                layout.addWidget(right_widget)
                layout.setContentsMargins(10, 12, 10, 12)

                # Create list item
                item = QListWidgetItem()
                custom_size = QSize(item_widget.sizeHint().width(), 80)
                item.setSizeHint(custom_size)
                self.recent_entry_list.addItem(item)
                self.recent_entry_list.setItemWidget(item, item_widget)

            self.recent_entry_list.setSpacing(5)
        except Exception as e:
            self.show_popup(f"Error loading entries: {str(e)}")
            print(f"Error in update_recent_entries: {e}")


    def store_mobile_number(self):
        """Store the manually entered mobile number in a variable."""
        self.entered_mobile_number = self.right_box_input.text().strip()
    
   
    def submit_entry(self):
        # Disable the entry button and show loading state
        self.entry_button.setEnabled(False)
        self.entry_button.setText("Please wait...")

        # Force UI update
        QApplication.processEvents()

        # Get the latest values from the input fields
        self.current_number_plate = self.left_box_input.text().strip()
        self.entered_mobile_number = self.right_box_input.text().strip()

        if self.entered_mobile_number and self.current_number_plate:
            try:
                self.show_popup("Processing vehicle entry...")
                QApplication.processEvents()

                # Make API call to create customer
                response = self.api_service.createCustomer("EMPLOYEE_APP", self.entered_mobile_number, self.current_number_plate,self.current_vehicle_type)

                # Handle possible API errors in response
                if isinstance(response, dict) and 'errorMessage' in response:
                    self.show_popup(f"API Error: {response['errorMessage']}")
                    return

                entry_fee_value = f"{response.get('initialCharge', 'N/A')} Rs/h"
                self.entry_fees_display.setText(entry_fee_value)
                parkingTicketVal = response.get('parkingTicketID')

                self.show_popup("Confirming ticket...")
                QApplication.processEvents()

                # Confirm the ticket
                confirmation = self.api_service.confirmTicket(parkingTicketVal)
                print(confirmation)

                # Handle confirmation errors
                if isinstance(confirmation, dict) and 'errorMessage' in confirmation:
                    self.show_popup(f"Ticket confirmation error: {confirmation['errorMessage']}")
                    return

                # Success message
                self.show_popup("Added vehicle successfully")

                # Clear all fields and update UI
                self.clear_fields_after_entry()
                self.update_recent_entries()

            except Exception as e:
                error_message = str(e)
                print(f"Error submitting entry: {error_message}")

                # Error type detection from message
                if "500" in error_message:
                    self.show_popup("Server error (500): The server encountered an internal error")
                elif "400" in error_message:
                    self.show_popup("Bad request (400): Please check your input data")
                elif "401" in error_message or "403" in error_message:
                    self.show_popup("Authentication error: Please check your credentials")
                else:
                    self.show_popup(f"Error submitting entry: {error_message}")

            finally:
                self.entry_button.setText("Park Vehicle")
                self.entry_button.setEnabled(True)

        else:
            print("Error: Mobile number or vehicle number is missing.")
            self.show_popup("Please enter both mobile number and vehicle number")
            self.entry_button.setText("Park Vehicle")
            self.entry_button.setEnabled(True)
    def clear_fields_after_entry(self):
        """Clear all input fields and reset UI after successful entry"""
        try:
            self.left_box_input.textChanged.disconnect(self.handle_number_plate_edit)
        except TypeError:
            pass

        self.left_box_input.clear()
        self.right_box_input.clear()
        self.entry_fees_display.clear()
        self.entry_time_display.setText("Entry time --:--")
        self.detected_image.clear()

        self.current_number_plate = ""
        self.entered_mobile_number = ""
        self.detected_number_plate = ""

        for btn in [self.car_radio, self.truck_radio, self.cycle_radio]:
            btn.setChecked(False)
        self.bike_radio.setChecked(True)
        self.current_vehicle_type = "Bike"

        self.left_box_input.textChanged.connect(self.handle_number_plate_edit)



            
    def show_popup(self, message):
        """
        Instead of showing a dialog, log the message in the message log list
        and optionally maintain a max number of messages. 
        Most recent messages will appear at the top.
        """
        # Add the message to the message log list (insert at position 0)
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        log_item = QListWidgetItem(f"{current_time}: {message}")
        
        # Optional: Set color based on message type
        if "error" in message.lower():
            log_item.setForeground(QColor('red'))
        elif "success" in message.lower():
            log_item.setForeground(QColor('green'))
        elif "processing" in message.lower() or "please wait" in message.lower() or "confirming" in message.lower():
            log_item.setForeground(QColor('blue'))
        
        # Insert at the top of the list
        self.message_log_list.insertItem(0, log_item)
        
        # Optional: Limit the number of messages (e.g., keep last 10)
        if self.message_log_list.count() > 10:
            self.message_log_list.takeItem(self.message_log_list.count() - 1)  # Remove the oldest item
        
        # Scroll to the top of the list (where new items appear)
        self.message_log_list.scrollToTop()
        
        # Force the UI to update
        QApplication.processEvents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingAppSplash()
    window.show()
    sys.exit(app.exec_())