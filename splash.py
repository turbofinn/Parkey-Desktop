from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QMessageBox, QListWidgetItem, QLineEdit, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
import sys
import cv2
import numpy as np
import tensorflow as tf
import pytesseract
import re
import time  
import os
from ApiService import ApiService 
import datetime
import json

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"




save_directory = r'imges'

if not os.path.exists(save_directory):
    os.makedirs(save_directory)


class ParkingAppSplash(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parking Management System")
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        self.setStyleSheet("background-color: #117554;")
        self.initUI()
        self.cap = None  # Camera object
        self.timer = None  # Timer for updating frames
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
        self.api_service = ApiService()

    def initUI(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left section layout
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(10, 20, 10, 10)  # Uniform margins

        # Spacer at the top for equal spacing
        left_layout.addStretch(1)

        # --- Detected Number Plate Section ---
        detected_box = QVBoxLayout()
        detected_label = QLabel("Detected Number\nPlate")
        detected_label.setStyleSheet("color: black; font-size: 26px; font-weight: bold;")
        detected_label.setAlignment(Qt.AlignCenter)

        self.detected_image = QLabel()
        self.detected_image.setFixedSize(320, 180)
        self.detected_image.setStyleSheet("background-color: white;")
        self.detected_image.setAlignment(Qt.AlignCenter)

        detected_box.addWidget(detected_label)
        detected_box.addWidget(self.detected_image)

        detected_container = QWidget()
        detected_container.setLayout(detected_box)
        detected_container.setFixedHeight(250)
        detected_container.setStyleSheet("border-radius: 10px; padding: 20px; background-color: white;")

        left_layout.addWidget(detected_container)

        # Spacer for equal spacing
        left_layout.addStretch(1)

        # --- Entry Fees Section ---
        entry_fees_box = QVBoxLayout()
        entry_fees_label = QLabel("Entry Charges")
        entry_fees_label.setStyleSheet("color: black; font-size: 22px; font-weight: bold;")
        entry_fees_label.setAlignment(Qt.AlignCenter)

        self.entry_fees_display = QLabel()
        self.entry_fees_display.setFixedSize(160, 100)
        self.entry_fees_display.setStyleSheet("background-color: white; font-size: 32px; font-weight: bold; color: black;")
        self.entry_fees_display.setAlignment(Qt.AlignCenter)

        entry_fees_box.addWidget(entry_fees_label)
        entry_fees_box.addWidget(self.entry_fees_display)

        entry_fees_container = QWidget()
        entry_fees_container.setLayout(entry_fees_box)
        entry_fees_container.setFixedHeight(160)
        entry_fees_container.setStyleSheet("border-radius: 10px; padding: 20px; background-color: white;")

        left_layout.addWidget(entry_fees_container)

        # Spacer for equal spacing
        left_layout.addStretch(1)

        # --- Entry Time Section ---
        entry_time_box = QVBoxLayout()
        entry_time_label = QLabel("Entry Time")
        entry_time_label.setStyleSheet("color: black; font-size: 24px; font-weight: bold;")
        entry_time_label.setAlignment(Qt.AlignCenter)

        self.entry_time_display = QLabel()
        self.entry_time_display.setFixedSize(280, 100)
        self.entry_time_display.setStyleSheet("background-color: white; font-weight: bold; font-size: 32px; padding: 10px;")
        self.entry_time_display.setAlignment(Qt.AlignCenter)

        entry_time_box.addWidget(entry_time_label)
        entry_time_box.addWidget(self.entry_time_display)

        entry_time_container = QWidget()
        entry_time_container.setLayout(entry_time_box)
        entry_time_container.setFixedHeight(160)
        entry_time_container.setStyleSheet("border-radius: 10px; padding: 20px; background-color: white;")

        left_layout.addWidget(entry_time_container)

        # Spacer at the bottom for equal spacing
        left_layout.addStretch(1)



        

        

        center_layout = QVBoxLayout()

        # Spacer ABOVE Camera (pushes it down)
        center_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Camera feed layout (unchanged)
        self.vehicle_image = QLabel()
        self.vehicle_image.setScaledContents(True)
        self.vehicle_image.setFixedSize(1000, 550)
        self.vehicle_image.setStyleSheet("""
            background-color: black;
            border: 8px solid white;
            border-radius: 10px;
        """
        )
        center_layout.addWidget(self.vehicle_image, alignment=Qt.AlignCenter)

        # Spacer BELOW Camera (pushes boxes down)
        center_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Box Container
        box_container = QVBoxLayout()

        # Box Layout (Two side-by-side boxes)
        box_layout = QHBoxLayout()

        # Left Box (Vehicle Verification)
        verify_box = QVBoxLayout()
        verify_label = QLabel("Verify Vehicle Details")
        verify_label.setStyleSheet("color: black; font-size: 18px; font-weight: bold;")
        verify_label.setAlignment(Qt.AlignCenter)

        self.left_box_input = QLineEdit()
        self.left_box_input.setFixedHeight(60)
        self.left_box_input.setAlignment(Qt.AlignCenter)
        self.left_box_input.setStyleSheet("""
                background-color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 24px;
                font-weight: bold;
                color: black;
        """
        )

        verify_box.addWidget(verify_label)
        verify_box.addWidget(self.left_box_input)

        verify_container = QWidget()
        verify_container.setLayout(verify_box)
        verify_container.setFixedHeight(150)
        verify_container.setStyleSheet("background-color: white; border-radius: 10px; padding: 5px;")

        box_layout.addWidget(verify_container)

        # Right Box (Mobile Number Entry)
        right_box_layout = QVBoxLayout()
        right_box_label = QLabel("Enter Mobile Number")
        right_box_label.setStyleSheet("color: black; font-size: 18px; font-weight: bold;")
        right_box_label.setAlignment(Qt.AlignCenter)

        self.right_box_input = QLineEdit()
        self.right_box_input.setFixedHeight(60)
        self.right_box_input.setAlignment(Qt.AlignCenter)
        self.right_box_input.setStyleSheet("""
                background-color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 24px;
                font-weight: bold;
                color: black;
            """
        )

        right_box_layout.addWidget(right_box_label)
        right_box_layout.addWidget(self.right_box_input)

        right_box_container = QWidget()
        right_box_container.setLayout(right_box_layout)
        right_box_container.setFixedHeight(150)
        right_box_container.setStyleSheet("background-color: white; border-radius: 10px; padding: 5px;")

        box_layout.addWidget(right_box_container)

        box_container.addLayout(box_layout)

        # Spacer BELOW Boxes (to maintain gaps from buttons)
        box_container.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Add the box container to the center layout
        center_layout.addLayout(box_container)

        # Button Layout (unchanged)
        button_layout = QHBoxLayout()

        self.automatic_button = QPushButton("Start")
        self.manual_button = QPushButton("Stop")
        self.entry_button = QPushButton("Entry")

        for button in [self.automatic_button, self.manual_button, self.entry_button]:
            button.setFixedSize(150, 60)
            button.setStyleSheet("""
                    background-color: #FF5733;
                    color: white;
                    font-size: 20px;
                    padding: 15px;
                    border-radius: 10px;
                """
        )

        button_layout.addWidget(self.automatic_button)
        button_layout.addWidget(self.manual_button)
        button_layout.addWidget(self.entry_button)

        center_layout.addLayout(button_layout)
        self.automatic_button.clicked.connect(self.start_camera)
        self.manual_button.clicked.connect(self.stop_camera)
        self.entry_button.clicked.connect(self.submit_entry)





        # Right section (Single white box with Recent Entry and Exit)
        right_layout = QVBoxLayout()

        # Container Widget for the right side
        right_container = QWidget() 
        right_container.setStyleSheet("background-color: white; border-radius: 10px;")
        right_container_layout = QVBoxLayout()
        right_container_layout.setContentsMargins(20, 20, 30, 30)  # Padding inside the white box
        right_container_layout.setSpacing(20)  # Spacing between sections
        right_container.setFixedWidth(450)
        # --- Recent Entry Section ---
        recent_entry_layout = QVBoxLayout()
        self.recent_entry_label = QLabel("Recent Entry")
        self.recent_entry_label.setStyleSheet("color: black; font-size: 22px; font-weight: bold;")
        self.recent_entry_label.setAlignment(Qt.AlignCenter)

        self.recent_entry_list = QListWidget()
        self.recent_entry_list.setStyleSheet(
            "font-size: 18px; background-color: transparent; padding: 5px;"
        )
        self.recent_entry_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add to recent entry layout
        recent_entry_layout.addWidget(self.recent_entry_label)
        recent_entry_layout.addWidget(self.recent_entry_list)

        # --- Recent Exit Section ---
        recent_exit_layout = QVBoxLayout()
        self.recent_exit_label = QLabel("Recent Exit")
        self.recent_exit_label.setStyleSheet("color: black; font-size: 22px; font-weight: bold;")
        self.recent_exit_label.setAlignment(Qt.AlignCenter)

        self.recent_exit_list = QListWidget()
        self.recent_exit_list.setStyleSheet(
            "font-size: 18px; background-color: transparent; padding: 5px;"
        )
        self.recent_exit_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add to recent exit layout
        recent_exit_layout.addWidget(self.recent_exit_label)
        recent_exit_layout.addWidget(self.recent_exit_list)

        # Add both sections to the container layout
        right_container_layout.addLayout(recent_entry_layout)
        right_container_layout.addLayout(recent_exit_layout)

        # Make the container fill the entire right side
        right_container.setLayout(right_container_layout)
        right_layout.addWidget(right_container)

        # Add the right layout to the main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(center_layout)
        main_layout.addLayout(right_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)





    def keyPressEvent(self, event):
        """Close the camera on pressing 'Q'"""
        if event.key() == Qt.Key_Q:
            self.stop_camera()

    def start_camera(self):
        """Start the camera and begin detecting number plates."""
        self.cap = cv2.VideoCapture(0)  # Open default camera
        self.entry_button.setEnabled(True)
        if not self.cap.isOpened():
            print("Error: Cannot access the camera")
            return

        # Load the TensorFlow model
        with tf.io.gfile.GFile('num_plate.pb', 'rb') as f:
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
        self.timer.start(30)  # Update every 30ms (~33 FPS)

    def stop_camera(self):
        """Stop the camera feed and close OpenCV windows."""
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        
        if hasattr(self, 'cap') and self.cap is not None and self.cap.isOpened():
            self.cap.release()
            self.cap = None  # Reset cap to prevent future issues
            print("Camera stopped.")
        else:
            print("Camera was not running.")

        if hasattr(self, 'sess'):
            self.sess.close()  # Close TensorFlow session to free resources
            print("TensorFlow session closed.")
        self.right_box_input.clear()
        self.entry_fees_display.clear()
        self.recent_entry_list.clear()
        self.left_box_input.clear()
        self.recent_exit_list.clear()
        self.entry_time_display.clear()
        self.detected_image.clear()
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
        input_frame = cv2.resize(frame, (300, 300))  # Resize frame to model's input size
        input_frame = np.expand_dims(input_frame, axis=0)  # Add batch dimension

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
                        custom_config = r'--oem 3 --psm 6'  # Tesseract configuration
                        text = pytesseract.image_to_string(roi_thresh, config=custom_config)

                        cleaned_text = re.sub(r'[^A-Za-z0-9]', '', text)
                        pattern = r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$'
                        
                        if re.match(pattern, cleaned_text):
                            
                            DetectedNumberPlate = cleaned_text.strip()  # Strip any extra whitespace or newline characters
                            filename = f"{save_directory}/plate_{time.time()}.jpg"
                            cv2.imwrite(filename, roi) 
                            self.update_detected_image(filename)
                            # print(DetectedNumberPlate)
                            self.update_vehicle_details(DetectedNumberPlate)
                            timing = datetime.datetime.now().strftime("%I:%M %p")
                            self.update_entry_time(timing)  
                            self.update_mobile_number(DetectedNumberPlate)

                        # print(f"OCR Raw Output: {text}")

                        # Temporarily commenting out the validation logic
                        # text = re.sub(r'[^A-Z0-9]', '', text.strip())  # Clean the OCR output
                        # pattern = r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$'  # Example: MH12AB1234
                        # if re.match(pattern, text):
                        #     print(f"Detected Valid Number Plate: {text}")
                        # else:
                        #     print(f"Ignored Invalid Plate: {text}")

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
        self.vehicle_image.setPixmap(pixmap)

    def update_detected_image(self, image_path):
        """Update the detected image display in the UI."""
        pixmap = QPixmap(image_path)
        self.detected_image.setPixmap(pixmap.scaled(self.detected_image.width(), self.detected_image.height(), Qt.KeepAspectRatio))
        self.detected_image.setAlignment(Qt.AlignCenter)


    def update_vehicle_details(self, number_plate):
        """Update the verify vehicle details input field with the detected number plate."""
        self.detected_number_plate = number_plate  # Store in global variable
        self.current_number_plate = number_plate
        self.left_box_input.setText(self.current_number_plate)

    def handle_number_plate_edit(self):
        """Handle changes to the number plate input field"""
        edited_text = self.left_box_input.text().strip()
        if edited_text != self.current_number_plate:
            self.current_number_plate = edited_text
            self.entry_fees_display.clear()

    def update_entry_time(self, timing):
        self.entry_time = timing
        self.entry_time_display.setText(self.entry_time)

    def update_mobile_number(self, number_plate):
        try:
            vehicle_no = str(number_plate)
            response_data = self.api_service.getVehicleDetails(vehicle_no)  # This returns a dictionary

            # Debugging - Print the API response
            print("API Response:", response_data)

            if response_data:
                if 'errorMessage' in response_data:
                    # Vehicle not found in the system
                    self.show_popup("Vehicle not present in the system.\nPlease enter the mobile number manually.")
                    self.right_box_input.clear()
                    self.entry_fees_display.clear()
                    self.recent_entry_list.clear()
                    self.entered_mobile_number = ""

                    # Set focus on the input field for manual entry
                    self.right_box_input.setFocus()

                    # Disconnect any previous connections to avoid duplicate triggers
                    try:
                        self.right_box_input.textChanged.disconnect()
                    except TypeError:
                        pass  # Ignore if there's no previous connection

                    # Connect text change event to store the manually entered number
                    self.right_box_input.textChanged.connect(self.store_mobile_number)
                else:
                    # Vehicle found - Populate mobile number and entry fees
                    mobile_number = response_data.get("mobileNo", "")
                    entry_fee = str(response_data.get('totalParkingCharges', '0'))
                    item = QListWidgetItem(f"John Doe\n+91 {mobile_number}")
                    
                    # Update UI fields
                    self.entered_mobile_number = mobile_number
                    self.right_box_input.setText(self.entered_mobile_number)
                    self.entry_fees_display.setText(f"{entry_fee} Rs")  # Adding currency symbol for clarity
                    self.recent_entry_list.addItem(item)

            else:
                # Handle cases where API returns an empty response
                self.show_popup("No data received from server. Please try again.")

        except Exception as e:
            print("Error fetching vehicle details:", str(e))
            self.show_popup(f"An error occurred: {str(e)}")




    def store_mobile_number(self):
        """Store the manually entered mobile number in a variable and call the API."""
        self.entered_mobile_number = self.right_box_input.text().strip()
    
    def submit_entry(self):
        self.entry_button.setEnabled(False)
        if self.entered_mobile_number and self.current_number_plate:
            response = self.api_service.getCreateCustomer(self.entered_mobile_number, self.current_number_plate)
            entry_fee_value = f"{response.get('initialCharge', 'N/A')} Rs/h"
            self.entry_fees_display.setText(entry_fee_value)
            item = QListWidgetItem(f"John Doe\n+91 {self.entered_mobile_number}") 
            self.recent_entry_list.addItem(item)
            parkingTicketVal = response.get('parkingTicketID')
            confirmation = self.api_service.confirmTicket(parkingTicketVal)
            print(confirmation)
            self.show_popup("Added vehicle successfully")
        else:
            print("Error: Mobile number or vehicle number is missing.")
            
    def show_popup(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Vehicle Not Found")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingAppSplash()
    window.show()
    sys.exit(app.exec_())

























































