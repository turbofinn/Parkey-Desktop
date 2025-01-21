from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import cv2
import tensorflow as tf
import numpy as np
import datetime
import os

# Load the model when the app starts
model = tf.saved_model.load('num_plate.pb')  

# Create a thread to run OpenCV video capture and detection
class VideoCaptureThread(QThread):
    new_frame_signal = pyqtSignal(np.ndarray)
    detection_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        cap = cv2.VideoCapture(0)  # Open the camera
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Preprocess the frame for model input
            input_image = cv2.resize(frame, (320, 320))  # Resize image to model input size
            input_image = input_image / 255.0  # Normalize image if required by model
            input_image = np.expand_dims(input_image, axis=0)  # Add batch dimension

            # Convert to tensor and run inference
            input_tensor = tf.convert_to_tensor(input_image, dtype=tf.float32)
            detections = model(input_tensor)

            # Process detections and visualize
            for detection in detections['detection_boxes']:
                y1, x1, y2, x2 = detection[0].numpy()  # Convert tensor to numpy
                x1, y1, x2, y2 = int(x1 * frame.shape[1]), int(y1 * frame.shape[0]), int(x2 * frame.shape[1]), int(y2 * frame.shape[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "Number Plate", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Emit the frame to update the UI
            self.new_frame_signal.emit(frame)

            # Save frame when 's' is pressed
            if cv2.waitKey(1) & 0xFF == ord('s'):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join("captures", f"frame_{timestamp}.jpg")
                cv2.imwrite(save_path, frame)
                print(f"Frame saved at {save_path}")

            # Exit when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

class ParkingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parking Management System")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #118B50;")
        self.initUI()

        self.capture_thread = VideoCaptureThread()
        self.capture_thread.new_frame_signal.connect(self.update_camera_feed)
        self.capture_thread.detection_signal.connect(self.update_detection_label)

    def initUI(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left section
        left_layout = QVBoxLayout()

        # Detected Number Plate
        detected_box = QVBoxLayout()
        self.detected_label = QLabel("Detected Number Plate")
        self.detected_label.setStyleSheet("color: black; font-size: 18px;")
        self.detected_image = QLabel()
        self.detected_image.setPixmap(QPixmap("carimage.png"))  # Replace with actual image path
        self.detected_image.setScaledContents(True)
        self.detected_image.setFixedSize(200, 50)
      
        
        detected_box.addWidget(self.detected_label, alignment=Qt.AlignCenter)
        detected_box.addWidget(self.detected_image, alignment=Qt.AlignCenter)
    

        detected_box_container = QWidget()
        detected_box_container.setLayout(detected_box)
        detected_box_container.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 10px; padding: 10px;")
        left_layout.addWidget(detected_box_container)

        # Entry Charges
        charges_box = QVBoxLayout()
        self.charges_label = QLabel("Entry Charges")
        self.charges_label.setStyleSheet("color: black; font-size: 18px;")
        self.charges_value = QLabel("20 Rs/h")
        self.charges_value.setStyleSheet("color: black; font-size: 20px;")
        charges_box.addWidget(self.charges_label, alignment=Qt.AlignCenter)
        charges_box.addWidget(self.charges_value, alignment=Qt.AlignCenter)

        charges_box_container = QWidget()
        charges_box_container.setLayout(charges_box)
        charges_box_container.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 10px; padding: 10px;")
        left_layout.addWidget(charges_box_container)

        # Entry Time
        time_box = QVBoxLayout()
        self.entry_time_label = QLabel("Entry Time")
        self.entry_time_label.setStyleSheet("color: black; font-size: 18px;")
        self.entry_time_value = QLabel("9:00 AM")
        self.entry_time_value.setStyleSheet("color: black; font-size: 20px;")
        time_box.addWidget(self.entry_time_label, alignment=Qt.AlignCenter)
        time_box.addWidget(self.entry_time_value, alignment=Qt.AlignCenter)

        time_box_container = QWidget()
        time_box_container.setLayout(time_box)
        time_box_container.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 10px; padding: 10px;")
        left_layout.addWidget(time_box_container)

        # Center section
        center_layout = QVBoxLayout()

        # Vehicle image
        self.vehicle_image = QLabel()
        self.vehicle_image.setPixmap(QPixmap("carimage.png"))  # Replace with actual image path
        self.vehicle_image.setScaledContents(True)
        self.vehicle_image.setFixedSize(300, 200)

        # Verify Vehicle Details and Enter Mobile Number side by side
        vehicle_and_mobile_layout = QHBoxLayout()

        # Verify Vehicle Details
        vehicle_box = QVBoxLayout()
        self.vehicle_details_label = QLabel("Verify Vehicle Details")
        self.vehicle_details_label.setStyleSheet("color: black; font-size: 18px;")
        self.vehicle_details_value = QLabel("BG224NZ")
        self.vehicle_details_value.setStyleSheet("color: black; font-size: 20px;")
        vehicle_box.addWidget(self.vehicle_details_label, alignment=Qt.AlignCenter)
        vehicle_box.addWidget(self.vehicle_details_value, alignment=Qt.AlignCenter)

        vehicle_box_container = QWidget()
        vehicle_box_container.setLayout(vehicle_box)
        vehicle_box_container.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 10px; padding: 10px;")

        # Enter Mobile Number
        mobile_box = QVBoxLayout()
        self.mobile_label = QLabel("Enter Mobile Number")
        self.mobile_label.setStyleSheet("color: black; font-size: 18px;")
        self.mobile_value = QLabel("+91 8960888016")
        self.mobile_value.setStyleSheet("color: black; font-size: 20px;")
        mobile_box.addWidget(self.mobile_label, alignment=Qt.AlignCenter)
        mobile_box.addWidget(self.mobile_value, alignment=Qt.AlignCenter)

        mobile_box_container = QWidget()
        mobile_box_container.setLayout(mobile_box)
        mobile_box_container.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 10px; padding: 10px;")

        vehicle_and_mobile_layout.addWidget(vehicle_box_container)
        vehicle_and_mobile_layout.addWidget(mobile_box_container)

        center_layout.addWidget(self.vehicle_image, alignment=Qt.AlignCenter)
        center_layout.addLayout(vehicle_and_mobile_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.automatic_button = QPushButton("Automatic")
        self.manual_button = QPushButton("Manual")
        self.entry_button = QPushButton("Entry")

        for button in [self.automatic_button, self.manual_button, self.entry_button]:
            button.setStyleSheet("background-color: #FF5733; color: white; font-size: 16px; padding: 10px; border-radius: 10px;")
            button.setFixedSize(120, 50)
        
        self.entry_button.clicked.connect(self.detect_number_plate)
        button_layout.addWidget(self.automatic_button)
        button_layout.addWidget(self.manual_button)
        button_layout.addWidget(self.entry_button)

        center_layout.addLayout(button_layout)

        # Right section
        right_layout = QVBoxLayout()
        self.recent_entry_label = QLabel("Recent Entry")
        self.recent_entry_label.setStyleSheet("color: black; font-size: 18px;")
        self.recent_entry_list = QListWidget()
        self.recent_entry_list.setStyleSheet("font-size: 16px; background-color: white; border: 2px solid black; border-radius: 10px; padding: 5px;")

        self.recent_exit_label = QLabel("Recent Exit")
        self.recent_exit_label.setStyleSheet("color: black; font-size: 18px;")
        self.recent_exit_list = QListWidget()
        self.recent_exit_list.setStyleSheet("font-size: 16px; background-color: white; border: 2px solid black; border-radius: 10px; padding: 5px;")

        # Add dummy data
        for name in ["Julia Howard", "Eleanor Cooper", "Bessie Fox", "Gloria Mccoy"]:
            item = QListWidgetItem(f"{name}\n+91 98765 43210")
            self.recent_entry_list.addItem(item)
            self.recent_exit_list.addItem(item)

        right_layout.addWidget(self.recent_entry_label)
        right_layout.addWidget(self.recent_entry_list)
        right_layout.addWidget(self.recent_exit_label)
        right_layout.addWidget(self.recent_exit_list)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(center_layout)
        main_layout.addLayout(right_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    def start_capture(self):
        self.capture_thread.start()

    def update_camera_feed(self, frame):
        # Convert OpenCV frame to QPixmap
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb_image.shape
        bytes_per_line = 3 * w
        q_image = QPixmap.fromImage(rgb_image, bytes_per_line, h)
        self.camera_feed.setPixmap(q_image)

    def update_detection_label(self, plate_number):
        self.detected_label.setText(f"Detected Number Plate: {plate_number}")
        # Display the detected number plate image if needed
        self.detected_image.setPixmap(QPixmap("carimage.png"))  # Replace with actual number plate image


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingApp()
    window.show()
    sys.exit(app.exec_())
