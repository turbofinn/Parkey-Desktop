from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QListWidget, QMessageBox, QListWidgetItem, 
                            QLineEdit, QSizePolicy, QSpacerItem, QFrame, QScrollArea)
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QTimer, QSize
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

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

save_directory = r'imges'

if not os.path.exists(save_directory):
    os.makedirs(save_directory)


class ParkingManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize variables
        self.cap = None  
        self.timer = None
        self.sess = None
        self.input_tensor = None
        self.detection_boxes = None
        self.detection_scores = None
        self.detection_classes = None
        self.num_detections = None
        self.detected_number_plate = ""
        self.exit_time = ""
        self.current_number_plate = ""
        self.entered_OTP = ""
        self.parkingTicketIDVal = None
        
        # Initialize API service
        env_config = EnvConfig()
        self.api_service = ApiService(env_config)
        
        # Setup UI
        self.setupUI()
    
    def setupUI(self):
        # Set window properties
        self.setWindowTitle("Raipur Railways Parking Management System")
        self.setGeometry(100, 100, 1250, 750)
        self.setStyleSheet("background-color: #04968b;")
        
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        
        # Left sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(170)
        sidebar.setStyleSheet("background-color: white; border-radius: 15px;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 15, 0, 15)
        sidebar_layout.setSpacing(20)
        
        # Sidebar icons
        icon_colors = ["#3b7be9", "#e0e0e0", "#3b7be9", "#e0e0e0", "#f26e56"]
        
        # Add top icon
        top_icon = QPushButton()
        top_icon.setFixedSize(30, 30)
        top_icon.setStyleSheet(f"background-color: {icon_colors[0]}; border-radius: 15px;")
        sidebar_layout.addWidget(top_icon, 0, Qt.AlignCenter)
        
        sidebar_layout.addStretch(1)
        
        # Add middle icons
        for color in icon_colors[1:4]:
            icon_btn = QPushButton()
            icon_btn.setFixedSize(30, 30)
            icon_btn.setStyleSheet(f"background-color: {color}; border-radius: 15px;")
            sidebar_layout.addWidget(icon_btn, 0, Qt.AlignCenter)
        
        sidebar_layout.addStretch(5)
        
        # User profile at bottom
        profile_btn = QPushButton()
        profile_btn.setFixedSize(38, 38)
        profile_btn.setStyleSheet("background-color: #e0e0e0; border-radius: 19px; border: 2px solid white;")
        sidebar_layout.addWidget(profile_btn, 0, Qt.AlignCenter)
        
        main_layout.addWidget(sidebar)
        
        # Center content area
        content_area = QWidget()
        content_area.setStyleSheet("background-color: white; border-radius: 15px;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(15, 10, 15, 10)
        content_layout.setSpacing(15)
        # Removed the maximum width restriction to allow more flexibility
        # content_area.setMaximumWidth(1050)

        # Header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("Parking Management System")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        header_layout.addWidget(title_label)

        back_btn = QPushButton("Back to home")
        back_btn.setStyleSheet("color: #3b7be9; border: none; font-size: 14px;")
        back_btn.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(back_btn, alignment=Qt.AlignRight)

        content_layout.addWidget(header_widget)

        # Date and time
        date_time_widget = QWidget()
        date_time_layout = QHBoxLayout(date_time_widget)
        date_time_layout.setContentsMargins(0, 0, 0, 0)
        date_time_layout.setSpacing(5)

        current_date = datetime.datetime.now().strftime("%d %b %Y")
        date_label = QLabel(current_date)
        date_label.setStyleSheet("color: #666; font-size: 14px;")
        date_time_layout.addWidget(date_label)

        dot_label = QLabel()
        dot_label.setFixedSize(10, 10)
        dot_label.setStyleSheet("background-color: red; border-radius: 5px;")
        date_time_layout.addWidget(dot_label)

        self.time_display = QLabel("Exit time --:--")
        self.time_display.setStyleSheet("color: #666; font-size: 14px;")
        date_time_layout.addWidget(self.time_display)
        date_time_layout.addStretch()

        content_layout.addWidget(date_time_widget)

        # Camera feed - Removed the gray background frame and integrated directly
        # The camera feed now directly shows in the content area
        self.vehicle_image = QLabel()
        self.vehicle_image.setScaledContents(True)
        self.vehicle_image.setAlignment(Qt.AlignCenter)
        self.vehicle_image.setStyleSheet("""
            background-color: black;
            border: 8px solid white;
            border-radius: 10px;
        """)
        self.vehicle_image.setFixedSize(1000, 550)  # Using fixed size instead of minimum size

        # Adding a container to hold both the image and the Live label
        camera_container = QWidget()
        camera_container_layout = QVBoxLayout(camera_container)
        camera_container_layout.setContentsMargins(0, 0, 0, 0)
        camera_container_layout.addWidget(self.vehicle_image, alignment=Qt.AlignCenter)

        # Live label
        live_label = QLabel("Live")
        live_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.6); color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;")
        live_label.setFixedSize(35, 18)
        # Position the live label over the camera feed at the bottom left
        # camera_container_layout.addWidget(live_label, alignment=Qt.AlignBottom | Qt.AlignLeft)

        content_layout.addWidget(camera_container, alignment=Qt.AlignCenter)

        # Detected license plate display
        detected_plate_frame = QFrame()
        detected_plate_frame.setFixedHeight(60)
        detected_plate_frame.setStyleSheet("background-color: #04968b; border-radius: 8px;")
        detected_plate_layout = QHBoxLayout(detected_plate_frame)

        # Detected plate container
        detected_container = QFrame()
        detected_container.setStyleSheet("background-color: white; border-radius: 6px;")
        detected_container.setFixedHeight(40)
        detected_container_layout = QHBoxLayout(detected_container)
        detected_container_layout.setContentsMargins(10, 5, 10, 5)

        detected_label = QLabel("Detected:")
        detected_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        detected_container_layout.addWidget(detected_label)

        self.detected_text = QLabel()
        self.detected_text.setStyleSheet("font-size: 14px;")
        detected_container_layout.addWidget(self.detected_text)

        detected_plate_layout.addWidget(detected_container)

        # Detected plate image
        self.detected_image = QLabel()
        self.detected_image.setFixedSize(170, 80)
        self.detected_image.setStyleSheet("background-color: white; border-radius: 6px;")
        self.detected_image.setAlignment(Qt.AlignCenter)
        detected_plate_layout.addWidget(self.detected_image)

        content_layout.addWidget(detected_plate_frame)
        # Input fields
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #04968b; border-radius: 8px;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 10, 15, 10)
        input_layout.setSpacing(20)
        
        # Vehicle number input
        vehicle_widget = QWidget()
        vehicle_layout = QVBoxLayout(vehicle_widget)
        vehicle_layout.setContentsMargins(0, 0, 0, 0)
        vehicle_layout.setSpacing(5)
        
        vehicle_label = QLabel("Vehicle Number:")
        vehicle_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        vehicle_layout.addWidget(vehicle_label)
        
        self.left_box_input = QLineEdit()
        self.left_box_input.setFixedHeight(30)
        self.left_box_input.setStyleSheet("""
            background-color: white;
            border-radius: 5px;
            padding: 5px 8px;
            font-size: 14px;
        """)
        vehicle_layout.addWidget(self.left_box_input)
        
        input_layout.addWidget(vehicle_widget)
        
        # OTP input
        otp_widget = QWidget()
        otp_layout = QVBoxLayout(otp_widget)
        otp_layout.setContentsMargins(0, 0, 0, 0)
        otp_layout.setSpacing(5)
        
        otp_label = QLabel("Exit OTP:")
        otp_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        otp_layout.addWidget(otp_label)
        
        self.right_box_input = QLineEdit()
        self.right_box_input.setFixedHeight(30)
        self.right_box_input.setStyleSheet("""
            background-color: white;
            border-radius: 5px;
            padding: 5px 8px;
            font-size: 14px;
        """)
        otp_layout.addWidget(self.right_box_input)
        
        input_layout.addWidget(otp_widget)
        
        # Exit charges
        charges_widget = QWidget()
        charges_layout = QVBoxLayout(charges_widget)
        charges_layout.setContentsMargins(0, 0, 0, 0)
        charges_layout.setSpacing(5)
        
        charges_label = QLabel("Exit Charges:")
        charges_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        charges_layout.addWidget(charges_label)
        
        self.entry_fees_display = QLineEdit()
        self.entry_fees_display.setFixedHeight(30)
        self.entry_fees_display.setReadOnly(True)
        self.entry_fees_display.setStyleSheet("""
            background-color: white;
            border-radius: 5px;
            padding: 5px 8px;
            font-size: 14px;
            font-weight: bold;
        """)
        charges_layout.addWidget(self.entry_fees_display)
        
        input_layout.addWidget(charges_widget)
        
        content_layout.addWidget(input_frame)
        
        # Action buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 10, 0, 5)
        button_layout.setSpacing(15)

        # Add stretch before buttons to push them toward center
        button_layout.addStretch()

        # Function to generate button styles
        def get_button_style(bg_color):
            return f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: white;
                    border-radius: 20px;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background-color: {bg_color}CC;
                }}
            """

        self.automatic_button = QPushButton("Start")
        self.automatic_button.setFixedSize(150, 40)
        self.automatic_button.setStyleSheet(get_button_style("#007bff"))
        button_layout.addWidget(self.automatic_button)

        self.manual_button = QPushButton("Stop")
        self.manual_button.setFixedSize(150, 40)
        self.manual_button.setStyleSheet(get_button_style("#dc3545"))
        button_layout.addWidget(self.manual_button)

        self.entry_button = QPushButton("Exit Vehicle")
        self.entry_button.setFixedSize(150, 40)
        self.entry_button.setStyleSheet(get_button_style("#1a8539"))
        button_layout.addWidget(self.entry_button)

        # Add stretch after buttons to push them toward center
        button_layout.addStretch()

        # Set alignment to center the button widget itself
        content_layout.addWidget(button_widget, alignment=Qt.AlignCenter)
        main_layout.addWidget(content_area, 1)
        
        # Right sidebar for entry and exit lists
        info_sidebar = QWidget()
        info_sidebar.setFixedWidth(600)
        info_sidebar.setStyleSheet("background-color: white; border-radius: 15px;")
        info_layout = QVBoxLayout(info_sidebar)
        info_layout.setContentsMargins(15, 15, 15, 15)
        info_layout.setSpacing(15)
        
        # Recent Entry section
        entry_widget = QWidget()
        entry_layout = QVBoxLayout(entry_widget)
        entry_layout.setContentsMargins(0, 0, 0, 0)
        entry_layout.setSpacing(5)
        
        entry_header = QLabel("Recent Entry")
        entry_header.setFont(QFont("Arial", 14, QFont.Bold))
        entry_header.setAlignment(Qt.AlignCenter)
        entry_layout.addWidget(entry_header)
        
        self.recent_entry_list = QListWidget()
        self.recent_entry_list.setStyleSheet("""
            background-color: #f5f5f5;
            border-radius: 8px;
            padding: 5px;
            font-size: 13px;
        """)
        entry_layout.addWidget(self.recent_entry_list)
        
        info_layout.addWidget(entry_widget)
        
        # Recent Exit section
        exit_widget = QWidget()
        exit_layout = QVBoxLayout(exit_widget)
        exit_layout.setContentsMargins(0, 0, 0, 0)
        exit_layout.setSpacing(5)
        
        exit_header = QLabel("Recent Exit")
        exit_header.setFont(QFont("Arial", 14, QFont.Bold))
        exit_header.setAlignment(Qt.AlignCenter)
        exit_layout.addWidget(exit_header)
        
        self.recent_exit_list = QListWidget()
        self.recent_exit_list.setStyleSheet("""
            background-color: #f5f5f5;
            border-radius: 8px;
            padding: 5px;
            font-size: 13px;
        """)
        exit_layout.addWidget(self.recent_exit_list)
        
        info_layout.addWidget(exit_widget)
        
        main_layout.addWidget(info_sidebar)
        
        # Connect signals to slots
        self.automatic_button.clicked.connect(self.start_camera)
        self.manual_button.clicked.connect(self.stop_camera)
        self.entry_button.clicked.connect(self.finalexit)
        
    def keyPressEvent(self, event):
        """Close the camera on pressing 'Q'"""
        if event.key() == Qt.Key_Q:
            self.stop_camera()

    def start_camera(self):
        """Start the camera and begin detecting number plates."""
        self.cap = cv2.VideoCapture(0)  
        self.entry_button.setEnabled(True)
        if not self.cap.isOpened():
            print("Error: Cannot access the camera")
            return

        # Load the TensorFlow model
        with tf.io.gfile.GFile(model_path, 'rb') as f:
            graph_def = tf.compat.v1.GraphDef()
            graph_def.ParseFromString(f.read())

        # Create a TensorFlow session and import the graph
        self.sess = tf.compat.v1.Session()
        tf.import_graph_def(graph_def, name="")

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

    def stop_camera(self):
        """Stop the camera feed and close OpenCV windows."""
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
            
        # Clear all fields
        self.right_box_input.clear()
        self.entry_fees_display.clear()
        self.recent_entry_list.clear()
        self.left_box_input.clear()
        self.recent_exit_list.clear()
        self.time_display.setText("Exit time --:--")
        self.detected_image.clear()
        self.detected_text.clear()
        cv2.destroyAllWindows()
        
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
            if score > 0.5:  # Confidence threshold
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
                            self.update_exit_time(timing)  
                            self.getVehicleData(DetectedNumberPlate)

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
        self.detected_number_plate = number_plate 
        self.current_number_plate = number_plate
        self.left_box_input.setText(self.current_number_plate)
        self.detected_text.setText(number_plate)

    def handle_number_plate_edit(self):
        """Handle changes to the number plate input field"""
        edited_text = self.left_box_input.text().strip()
        if edited_text != self.current_number_plate:
            self.current_number_plate = edited_text
            self.entry_fees_display.clear()
            self.getVehicleData(self.current_number_plate)

    def update_exit_time(self, timing):
        self.exit_time = timing
        self.time_display.setText(f"Exit time {timing}")

    def getVehicleData(self, number_plate):
        try:
            response = self.api_service.getVehicleDetails(number_plate)
            self.parkingTicketIDVal = response.get("parkingTicketID", "")
            self.right_box_input.setFocus()

            try:
                self.right_box_input.textChanged.disconnect(self.update_entered_OTP)
            except TypeError:
                pass  

            self.right_box_input.textChanged.connect(self.update_entered_OTP)
        except Exception as e:
            print("Error fetching vehicle details:", str(e))
            self.show_popup(f"An error occurred: {str(e)}")

    def update_entered_OTP(self, text):
        """ Updates self.entered_OTP as the user types and calls otpExitTicket when OTP is 4 digits """
        self.entered_OTP = text

    def finalexit(self):
        """Handles the vehicle exit process with OTP verification"""
        if not self.parkingTicketIDVal or not self.entered_OTP:
            self.show_popup("Please ensure vehicle number and OTP are entered")
            return
            
        response = self.api_service.otpExitTicket(self.entered_OTP, self.parkingTicketIDVal)

        if response and "message" in response and "OTP verified" in response["message"]:
            # OTP is verified, call parkingCharges
            parkingdetails = self.api_service.parkingCharges(self.parkingTicketIDVal)
            print(parkingdetails)
            totalcharges = parkingdetails.get("totalParkingCharges", '0')
            self.entry_fees_display.setText(f"{totalcharges} Rs")

            # Add to recent exit list
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            item = QListWidgetItem(f"{self.current_number_plate} - {current_time}")
            self.recent_exit_list.addItem(item)

            # Call exitTicket only if OTP is verified
            exit_response = self.api_service.exitTicket(self.parkingTicketIDVal)

            if exit_response and "successMessage" in exit_response and "Vehicle exited safely" in exit_response["successMessage"]:
                self.show_popup(exit_response["successMessage"])
                self.right_box_input.clear()
                self.entry_fees_display.clear()
                self.parkingTicketIDVal = None
                self.entered_OTP = ""
                self.left_box_input.clear()
                self.time_display.setText("Exit time --:--")
                self.detected_image.clear()
                self.detected_text.clear()
        else:
            self.show_popup("Wrong OTP! Try again.") 

    def show_popup(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Vehicle Exit Notification")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingManagementSystem()
    window.show()
    sys.exit(app.exec_())