from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QListWidgetItem
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


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


save_directory = r'imges'

if not os.path.exists(save_directory):
    os.makedirs(save_directory)


class ParkingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parking Management System")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #118B50;")
        self.initUI()
        self.cap = None  # Camera object
        self.timer = None  # Timer for updating frames
        self.sess = None
        self.input_tensor = None
        self.detection_boxes = None
        self.detection_scores = None
        self.detection_classes = None
        self.num_detections = None

    def initUI(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left section
        left_layout = QVBoxLayout()

        # Detected Number Plate
        detected_box = QVBoxLayout()
        self.detected_image_label = QLabel("Detected Number Plate")
        self.detected_image_label.setFixedSize(200,50)
        self.detected_image_label.setScaledContents(True)
        self.detected_image_label.setStyleSheet("color: black; font-size: 18px;")

        
        self.detected_image = QLabel()
          
        self.detected_image.setScaledContents(True)
        self.detected_image.setFixedSize(200, 100)

        detected_box.addWidget(self.detected_image_label, alignment=Qt.AlignCenter)
        detected_box.addWidget(self.detected_image, alignment=Qt.AlignCenter)

        detected_box_container = QWidget()
        detected_box_container.setLayout(detected_box)
        detected_box_container.setStyleSheet(
            "background-color: white; border: 2px solid black; border-radius: 10px; padding: 10px;"
        )
        left_layout.addWidget(detected_box_container)

        # Center section
        center_layout = QVBoxLayout()

        # Vehicle image (camera feed)
        self.vehicle_image = QLabel()
        self.vehicle_image.setScaledContents(True)
        self.vehicle_image.setFixedSize(300, 200)
        center_layout.addWidget(self.vehicle_image, alignment=Qt.AlignCenter)

        # Buttons
        button_layout = QHBoxLayout()
        self.automatic_button = QPushButton("Automatic")
        self.manual_button = QPushButton("Manual")
        self.entry_button = QPushButton("Entry")

        for button in [self.automatic_button, self.manual_button, self.entry_button]:
            button.setStyleSheet(
                "background-color: #FF5733; color: white; font-size: 16px; padding: 10px; border-radius: 10px;"
            )
            button.setFixedSize(120, 50)

        self.entry_button.clicked.connect(self.start_camera)  # Start camera on button click
        button_layout.addWidget(self.automatic_button)
        button_layout.addWidget(self.manual_button)
        button_layout.addWidget(self.entry_button)

        center_layout.addLayout(button_layout)

        # Right section (recent entry and exit lists)
        right_layout = QVBoxLayout()
        self.recent_entry_label = QLabel("Recent Entry")
        self.recent_entry_label.setStyleSheet("color: black; font-size: 18px;")
        self.recent_entry_list = QListWidget()
        self.recent_entry_list.setStyleSheet(
            "font-size: 16px; background-color: white; border: 2px solid black; border-radius: 10px; padding: 5px;"
        )
        self.recent_exit_label = QLabel("Recent Exit")
        self.recent_exit_label.setStyleSheet("color: black; font-size: 18px;")
        self.recent_exit_list = QListWidget()
        self.recent_exit_list.setStyleSheet(
            "font-size: 16px; background-color: white; border: 2px solid black; border-radius: 10px; padding: 5px;"
        )

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

    def keyPressEvent(self, event):
        """Close the camera on pressing 'Q'"""
        if event.key() == Qt.Key_Q:
            self.stop_camera()

    def start_camera(self):
        """Start the camera and begin detecting number plates."""
        self.cap = cv2.VideoCapture(0)  # Open default camera
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
        if self.cap:
            self.timer.stop()
            self.cap.release()
            cv2.destroyAllWindows()


    # def update_frame_with_detection(self):
    #     """Capture a frame, run number plate detection, and display the result."""
    #     ret, frame = self.cap.read()
    #     if not ret:
    #         print("Error: Failed to grab frame")
    #         self.timer.stop()
    #         self.cap.release()
    #         return

    #     # Preprocess the frame for the model
    #     input_frame = cv2.resize(frame, (300, 300))  # Resize frame to model's input size
    #     input_frame = np.expand_dims(input_frame, axis=0)  # Add batch dimension

    #     # Run inference
    #     outputs = self.sess.run(
    #         [self.num_detections, self.detection_boxes, self.detection_scores, self.detection_classes],
    #         feed_dict={self.input_tensor: input_frame}
    #     )

    #     # Process the predictions
    #     num_detected = int(outputs[0][0])
    #     detected_plates = set()  # Store detected valid plates to avoid duplicate prints

    #     for i in range(num_detected):
    #         score = outputs[2][0][i]
    #         if score > 0.5:  # Confidence threshold
    #             box = outputs[1][0][i]

             
    #             h, w, _ = frame.shape
    #             y1, x1, y2, x2 = int(box[0] * h), int(box[1] * w), int(box[2] * h), int(box[3] * w)

               
    #             roi = frame[y1:y2, x1:x2]

               
    #             try:
    #                 if roi.size > 0: 
    #                     result = reader.readtext(roi)
    #                     for detection in result:
    #                         text = detection[1].strip()  
    #                         pattern = "^[A-Z]{2}[ -]?[0-9]{2}[ -]?[A-Z]{1,2}[ -]?[0-9]{4}$"

    #                         if re.match(pattern, text):  
    #                             if text not in detected_plates:  
    #                                 print(f"Detected Valid Number Plate: {text}")
    #                                 detected_plates.add(text) 
    #                         else:
    #                             print(f"Ignored Invalid Plate: {text}")
    #             except Exception as e:
    #                 print(f"Error with OCR: {e}")

    #             # Draw the bounding box and label
    #             cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    #             cv2.putText(frame, "Number Plate", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    #     # Convert the frame to RGB format for PyQt
    #     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #     h, w, ch = rgb_frame.shape
    #     bytes_per_line = ch * w
    #     qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #     pixmap = QPixmap.fromImage(qt_image)

    #     # Update the QLabel in the GUI with the new frame
    #     self.vehicle_image.setPixmap(pixmap)



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
                            print("Valid vehicle number plate!",DetectedNumberPlate)
                            self.update_detected_image(filename)

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
            """ Update the detected image label with the new image """
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.detected_image.setPixmap(pixmap)
                
            else:
                self.detected_image.setText("Image not found")





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ParkingApp()
    window.show()
    sys.exit(app.exec_())
