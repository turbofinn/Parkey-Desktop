from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFrame, QScrollArea, QMessageBox,
                             QListWidget, QListWidgetItem, QSizePolicy, QSpacerItem)
from PyQt5.QtGui import QFont, QColor, QPixmap, QImage
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


class ParkingAppFourth (QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raipur Railways Parking - Exit")
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        self.setStyleSheet("background-color: #04968b;")
        
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
        self.current_number_plate = ""
        self.exit_time = ""
        self.exit_fees = ""
        self.entered_OTP = ""
        self.parkingTicketIDVal = None
        env_config = EnvConfig()
        self.api_service = ApiService(env_config)
        
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
        sidebar.setFixedWidth(200)  # Increased width
        sidebar.setStyleSheet("background-color: white; border-radius: 15px;")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_layout.setSpacing(20)

        # Sidebar icons configuration with emoji icons
        sidebar_icons = [
            {"icon": "👤", "color": "#3b7be9", "position": "top"},     # User icon
            {"icon": "🏠", "color": "#e0e0e0", "position": "middle"}, # Home icon
            {"icon": "📹", "color": "#3b7be9", "position": "middle"}, # Camera/video icon
            {"icon": "🎙️", "color": "#e0e0e0", "position": "middle"},# Microphone icon
            {"icon": "📊", "color": "#f26e56", "position": "middle"} # Chart/stats icon
        ]

        # Function to create icon buttons
        def create_icon_button(icon, background_color):
            btn = QPushButton(icon)
            btn.setFixedSize(60, 60)
            btn.setStyleSheet(f"""
                font-size: 30px;
                background-color: {background_color};
                border-radius: 30px;
                color: white;
            """)
            return btn

        # Add top icons
        top_icons = [icon for icon in sidebar_icons if icon["position"] == "top"]
        for icon_config in top_icons:
            icon_btn = create_icon_button(icon_config['icon'], icon_config['color'])
            sidebar_layout.addWidget(icon_btn, 0, Qt.AlignCenter)

        sidebar_layout.addStretch(1)

        # Add middle icons
        middle_icons = [icon for icon in sidebar_icons if icon["position"] == "middle"]
        for icon_config in middle_icons:
            icon_btn = create_icon_button(icon_config['icon'], icon_config['color'])
            sidebar_layout.addWidget(icon_btn, 0, Qt.AlignCenter)

        sidebar_layout.addStretch(5)

        # User profile button at bottom
        profile = QLabel("👤")
        profile.setStyleSheet("""
            font-size: 30px; 
            color: #555555; 
            background-color: #e0e0e0; 
            border-radius: 30px;
            border: 3px solid white;
        """)
        profile.setFixedSize(60, 60)
        profile.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(profile, 0, Qt.AlignCenter)

        # Add sidebar to main layout
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
        header_layout.setContentsMargins(40, 0, 20, 0)
        
        title_label = QLabel("Raipur Railways Parking - Exit")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        header_layout.addWidget(title_label)
        
        content_layout.addWidget(header_widget)
        
        # Date and time display
        date_time_widget = QWidget()
        date_time_layout = QHBoxLayout(date_time_widget)
        date_time_layout.setContentsMargins(42, 0, 0, 0)
        date_time_layout.setSpacing(5)
        
        date_label = QLabel(datetime.datetime.now().strftime("%d %b %Y"))
        date_label.setStyleSheet("color: #666; font-size: 14px;")
        date_time_layout.addWidget(date_label)
        
        dot_label = QLabel()
        dot_label.setFixedSize(10, 10)
        dot_label.setStyleSheet("background-color: red; border-radius: 5px;")
        date_time_layout.addWidget(dot_label)
        
        self.exit_time_display = QLabel("Exit time --:--")
        self.exit_time_display.setStyleSheet("color: #666; font-size: 14px;")
        date_time_layout.addWidget(self.exit_time_display)
        date_time_layout.addStretch()
        
        content_layout.addWidget(date_time_widget)
        
        # Live camera feed
        camera_frame = QFrame()
        camera_layout = QVBoxLayout(camera_frame)
        camera_layout.setContentsMargins(0, 0, 0, 0)
        
        # Vehicle image (camera feed)
        self.vehicle_image = QLabel()
        self.vehicle_image.setAlignment(Qt.AlignCenter)
        self.vehicle_image.setStyleSheet("""
            background-color: black;
            border: 8px solid white;
            border-radius: 10px;
        """)
        self.vehicle_image.setFixedSize(1000, 550)
        camera_layout.addWidget(self.vehicle_image, alignment=Qt.AlignCenter)
        self.vehicle_image.setScaledContents(True)
        
        content_layout.addWidget(camera_frame)
        
        # Number plate display
        plate_frame = QFrame()
        plate_frame.setFixedSize(990, 80)
        plate_frame.setStyleSheet("background-color: #04968b; border-radius: 6px;")
        plate_layout = QHBoxLayout(plate_frame)
        plate_layout.setContentsMargins(0, 0, 0, 0)

        # Detected image display
        self.detected_image = QLabel()
        self.detected_image.setFixedSize(200, 60)
        self.detected_image.setStyleSheet("background-color: white; border-radius: 4px;")
        self.detected_image.setAlignment(Qt.AlignCenter)

        plate_layout.addWidget(self.detected_image, alignment=Qt.AlignCenter)

        content_layout.addWidget(plate_frame, alignment=Qt.AlignCenter)
        
        # Input fields section
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #04968b; border-radius: 6px;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 10, 15, 10)
        input_frame.setFixedSize(990, 80)
        input_layout.setSpacing(40)

        # Number plate input
        plate_widget = QWidget()
        plate_layout = QVBoxLayout(plate_widget)
        plate_layout.setContentsMargins(0, 0, 0, 0)
        plate_layout.setSpacing(5)

        plate_label = QLabel("Number Plate:")
        plate_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        plate_layout.addWidget(plate_label)

        self.plate_input = QLineEdit()
        self.plate_input.setFixedSize(250, 36)
        self.plate_input.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px 8px; font-size: 16px;")
        plate_layout.addWidget(self.plate_input)

        input_layout.addWidget(plate_widget)

        # OTP input
        otp_widget = QWidget()
        otp_layout = QVBoxLayout(otp_widget)
        otp_layout.setContentsMargins(0, 0, 0, 0)
        otp_layout.setSpacing(5)

        otp_label = QLabel("Exit OTP:")
        otp_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        otp_layout.addWidget(otp_label)

        self.otp_input = QLineEdit()
        self.otp_input.setFixedSize(250, 36)
        self.otp_input.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px 8px; font-size: 16px;")
        otp_layout.addWidget(self.otp_input)

        input_layout.addWidget(otp_widget)

        # Exit charges display
        charges_widget = QWidget()
        charges_layout = QVBoxLayout(charges_widget)
        charges_layout.setContentsMargins(0, 0, 0, 0)
        charges_layout.setSpacing(5)

        charges_label = QLabel("Exit Charges:")
        charges_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        charges_layout.addWidget(charges_label)

        self.exit_fees_display = QLabel()
        self.exit_fees_display.setFixedSize(250, 36)
        self.exit_fees_display.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px 8px; font-size: 16px; font-weight: bold;")
        self.exit_fees_display.setAlignment(Qt.AlignCenter)
        charges_layout.addWidget(self.exit_fees_display)

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
            """

        self.start_button = QPushButton("Start Camera")
        self.start_button.setFixedSize(150, 45)
        self.start_button.setStyleSheet(get_button_style("#007bff"))
        button_layout.addWidget(self.start_button)

        self.exit_button = QPushButton("Process Exit")
        self.exit_button.setFixedSize(150, 45)
        self.exit_button.setStyleSheet(get_button_style("#dc3545"))
        button_layout.addWidget(self.exit_button)

        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.setFixedSize(150, 45)
        self.stop_button.setStyleSheet(get_button_style("#6c757d"))
        button_layout.addWidget(self.stop_button)

        content_layout.addWidget(button_widget)
        main_layout.addWidget(content_area, 1)

        # Right sidebar for recent exits
        vehicle_sidebar = QWidget()
        vehicle_sidebar.setFixedWidth(550)
        vehicle_sidebar.setStyleSheet("background-color: white; border-radius: 15px;")
        vehicle_layout = QVBoxLayout(vehicle_sidebar)
        vehicle_layout.setContentsMargins(10, 10, 10, 10)
        vehicle_layout.setSpacing(10)
        
        # Recent exits label
        recent_exit_label = QLabel("Recent Exits")
        recent_exit_label.setFont(QFont("Arial", 14, QFont.Bold))
        recent_exit_label.setAlignment(Qt.AlignCenter)
        recent_exit_label.setStyleSheet("color: #666; margin-bottom: 5px; padding: 3px;")
        vehicle_layout.addWidget(recent_exit_label)
        
        # Recent exits list
        self.recent_exit_list = QListWidget()
        self.recent_exit_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                font-size: 14px;
            }
            QListWidget::item {
                border-bottom: 1px solid #ddd;
                padding: 5px;
            }
        """)
        vehicle_layout.addWidget(self.recent_exit_list)

                
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
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
        self.exit_button.clicked.connect(self.finalexit)
        self.otp_input.textChanged.connect(self.update_entered_OTP)

    def keyPressEvent(self, event):
        """Close the camera on pressing 'Q'"""
        if event.key() == Qt.Key_Q:
            self.stop_camera()

    def start_camera(self):
        """Start the camera and begin detecting number plates."""
        self.cap = cv2.VideoCapture(0)  
        self.exit_button.setEnabled(True)
       
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
        self.show_popup("Camera started successfully")

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
        
        # Clear UI elements
        self.plate_input.clear()
        self.otp_input.clear()
        self.exit_fees_display.clear()
        self.exit_time_display.setText("Exit time --:--")
        self.detected_image.clear()
        self.show_popup("Camera stopped successfully")
        
        # Clear the vehicle image
        self.vehicle_image.clear()
        
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
                            self.update_exit_time(timing)  
                            self.getVehicleData(DetectedNumberPlate)
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

        # Update the QLabel in the GUI with the new frame
        self.vehicle_image.setPixmap(pixmap.scaled(self.vehicle_image.width(), self.vehicle_image.height(), Qt.KeepAspectRatio))

    def update_detected_image(self, image_path):
        """Update the detected image display in the UI."""
        pixmap = QPixmap(image_path)
        self.detected_image.setPixmap(pixmap.scaled(self.detected_image.width(), self.detected_image.height(), Qt.KeepAspectRatio))
        self.detected_image.setAlignment(Qt.AlignCenter)

    def update_vehicle_details(self, number_plate):
        """Update the vehicle details input field with the detected number plate."""
        self.detected_number_plate = number_plate  
        self.current_number_plate = number_plate
        self.plate_input.setText(self.current_number_plate)

    def update_exit_time(self, timing):
        self.exit_time = timing
        self.exit_time_display.setText(f"Exit time {timing}")

    def getVehicleData(self, number_plate):
        try:
            response = self.api_service.getVehicleDetails(number_plate)
            self.parkingTicketIDVal = response.get("parkingTicketID", "")
            self.otp_input.setFocus()
        except Exception as e:
            print("Error fetching vehicle details:", str(e))
            self.show_popup(f"An error occurred: {str(e)}")

    def update_entered_OTP(self, text):
        """Updates self.entered_OTP as the user types"""
        self.entered_OTP = text

    def finalexit(self):
        """Handles the vehicle exit process with OTP verification"""
        self.exit_button.setEnabled(False)
        
        if not self.current_number_plate or not self.entered_OTP:
            self.show_popup("Please detect a vehicle number and enter OTP")
            self.exit_button.setEnabled(True)
            return
            
        try:
            response = self.api_service.otpExitTicket(self.entered_OTP, self.parkingTicketIDVal)

            if response and "message" in response and "OTP verified" in response["message"]:
                # OTP is verified, call parkingCharges
                parkingdetails = self.api_service.parkingCharges(self.parkingTicketIDVal)
                print(parkingdetails)
                totalcharges = parkingdetails.get("totalParkingCharges", '0')
                self.exit_fees_display.setText(f"{totalcharges} Rs")

                item = QListWidgetItem(f"Vehicle {self.current_number_plate} exited")
                self.recent_exit_list.addItem(item)

                # Call exitTicket only if OTP is verified
                exit_response = self.api_service.exitTicket(self.parkingTicketIDVal)

                if exit_response and "successMessage" in exit_response and "Vehicle exited safely" in exit_response["successMessage"]:
                    self.show_popup(exit_response["successMessage"])
                    self.clear_fields_after_exit()
                else:
                    self.show_popup("Exit failed. Please try again.")
            else:
                self.show_popup("Wrong OTP! Try again.") 
                
        except Exception as e:
            print(f"Error processing exit: {str(e)}")
            self.show_popup(f"Error processing exit: {str(e)}")
            
        self.exit_button.setEnabled(True)
            
    def clear_fields_after_exit(self):
        """Clear all fields after successful exit"""
        self.plate_input.clear()
        self.otp_input.clear()
        self.exit_fees_display.clear()
        self.exit_time_display.setText("Exit time --:--")
        self.detected_image.clear()
        self.current_number_plate = ""
        self.parkingTicketIDVal = None
        self.entered_OTP = ""
            
    def show_popup(self, message):
        """
        Instead of showing a dialog, log the message in the message log list
        and optionally maintain a max number of messages. 
        Most recent messages will appear at the top.
        """
        # Add the message to the message log list (insert at position 0)
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        log_item = QListWidgetItem(f"{current_time}: {message}")
        
        # Optional: Set color based on message type (you can expand this)
        if "error" in message.lower():
            log_item.setForeground(QColor('red'))
        elif "success" in message.lower():
            log_item.setForeground(QColor('green'))
        
        # Insert at the top of the list
        self.message_log_list.insertItem(0, log_item)
        
        # Optional: Limit the number of messages (e.g., keep last 10)
        if self.message_log_list.count() > 10:
            self.message_log_list.takeItem(self.message_log_list.count() - 1)  # Remove the oldest item
        
        # Scroll to the top of the list (where new items appear)
        self.message_log_list.scrollToTop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingAppFourth ()
    window.show()
    sys.exit(app.exec_())