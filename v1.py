import tkinter as tk
import cv2
import numpy as np
import tensorflow as tf
import pytesseract
import re
from PIL import Image, ImageTk
from datetime import datetime
import threading

# Define the regex pattern for number plate detection (adjust if necessary)
pattern = r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$'

# Path to Tesseract on macOS
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# Load TensorFlow model for number plate detection
with tf.io.gfile.GFile('num_plate.pb', 'rb') as f:
    graph_def = tf.compat.v1.GraphDef()
    graph_def.ParseFromString(f.read())

# OpenCV capture setup
cap = cv2.VideoCapture(0)

# Global variable for the detected number plate
DetectedNumberPlate = ''

# Define the classes for detection (background, number plate)
classes = ["background", "number plate"]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

# Create the main window for Tkinter
root = tk.Tk()
root.title("Number Plate Recognition")
root.geometry("1200x1600")  # Set an appropriate window size

# Create a frame for text labels and buttons
top_frame = tk.Frame(root)
top_frame.pack(pady=10, padx=10, fill=tk.X)

# Create a frame to hold the camera feed and cropped images horizontally
camera_frame = tk.Frame(root)
camera_frame.pack(padx=10, pady=10)

# Create a frame for the live camera feed
camera_feed_frame = tk.Frame(camera_frame, width=600, height=600)
camera_feed_frame.pack_propagate(False)  # Prevent resizing
camera_feed_frame.pack(side=tk.LEFT, padx=10)

# Create a label to display the live camera feed
camera_label = tk.Label(camera_feed_frame)
camera_label.pack()

# Create a frame for the OCR result (number plate text)
ocr_frame = tk.Frame(root)
ocr_frame.pack(pady=10, padx=10)

# Create a text widget to display the OCR result
ocr_text = tk.Text(ocr_frame, height=5, width=40, font=("Arial", 16))
ocr_text.pack()

# Function to capture video and process number plate detection
def video_stream():
    global DetectedNumberPlate  # Declare the variable as global
    with tf.compat.v1.Session() as sess:
        sess.graph.as_default()
        tf.import_graph_def(graph_def, name='')

        while True:
            _, img = cap.read()
            rows, cols = img.shape[0], img.shape[1]

            # Preprocess image for TensorFlow input
            inp = cv2.resize(img, (220, 220))
            inp = inp[:, :, [2, 1, 0]]  # Convert to BGR format

            # Run the detection model
            out = sess.run([sess.graph.get_tensor_by_name('num_detections:0'),
                            sess.graph.get_tensor_by_name('detection_scores:0'),
                            sess.graph.get_tensor_by_name('detection_boxes:0'),
                            sess.graph.get_tensor_by_name('detection_classes:0')],
                           feed_dict={'image_tensor:0': inp.reshape(1, inp.shape[0], inp.shape[1], 3)})

            num_detections = int(out[0][0])

            for i in range(num_detections):
                classId = int(out[3][0][i])
                score = float(out[1][0][i])
                bbox = [float(v) for v in out[2][0][i]]
                label = classes[classId]

                # If the detection confidence is greater than 40%
                if score > 0.4:
                    x, y, right, bottom = bbox[1] * cols, bbox[0] * rows, bbox[3] * cols, bbox[2] * rows
                    color = colors[classId]

                    # Draw a rectangle around the detected number plate
                    cv2.rectangle(img, (int(x), int(y)), (int(right), int(bottom)), color, thickness=1)
                    cv2.rectangle(img, (int(x), int(y)), (int(right), int(y + 30)), color, -1)

                    # Crop the detected number plate from the image
                    crop = img[int(y):int(bottom), int(x):int(right)]
                    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                    Cropped = cv2.resize(gray, (300, 100))

                    # Perform OCR on the cropped number plate image
                    text = pytesseract.image_to_string(Cropped, config='--psm 11')
                    print(text)
                    cleaned_text = re.sub(r'[^A-Za-z0-9]', '', text)
                    print(cleaned_text)

                    # Match the detected text with the license plate pattern
                    if re.match(pattern, cleaned_text):
                        DetectedNumberPlate = cleaned_text.strip()  # Strip any extra whitespace or newline characters
                        print("Valid vehicle number plate!")

                    # Display the cleaned text in the text area
                    ocr_text.delete(1.0, tk.END)  # Clear previous OCR text
                    ocr_text.insert(tk.END, f"Detected License Plate: {DetectedNumberPlate}\n")

            # Convert the image to RGB format for Tkinter
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(img_pil)

            # Update the camera label with the new image
            camera_label.img_tk = img_tk
            camera_label.config(image=img_tk)

            # Update the display every 10 ms
            camera_label.after(1, update_video)

def update_video():
    pass  # Placeholder function for periodic updates in Tkinter

# Start the video stream in a separate thread
def start_video_stream():
    thread = threading.Thread(target=video_stream, daemon=True)
    thread.start()

# Update the time every second
def update_time():
    current_time = datetime.now().strftime("%H:%M:%S")
    time_label.config(text=f"Current Time: {current_time}")
    root.after(1000, update_time)

# Create and display the "Current Time" label
time_label = tk.Label(top_frame, text="Current Time: ", font=("Arial", 16), relief="solid", bd=2, padx=10, pady=5, bg="lightblue", anchor='center', width=30)
time_label.pack(side=tk.LEFT, padx=5, pady=5)

# Create and display the "Welcome" label
welcome_label = tk.Label(top_frame, text="Welcome", font=("Arial", 16), relief="solid", bd=2, padx=10, pady=5, bg="lightgreen", anchor='center', width=30)
welcome_label.pack(side=tk.LEFT, padx=5, pady=5)

# Create and display the "Date" label
date_label = tk.Label(top_frame, text="Date: ", font=("Arial", 16), relief="solid", bd=2, padx=10, pady=5, bg="lightyellow", anchor='center', width=30)
date_label.pack(side=tk.LEFT, padx=5, pady=5)

# Create and display the "Action" label
action_label = tk.Label(top_frame, text="Action: Ready", font=("Arial", 16), relief="solid", bd=2, padx=10, pady=5, bg="lightcoral", anchor='center', width=30)
action_label.pack(side=tk.LEFT, padx=5, pady=5)

# Update the date when the program starts
def update_date():
    current_date = datetime.now().strftime("%Y-%m-%d")
    date_label.config(text=f"Date: {current_date}")

# Create and display the "Start" button (at the bottom, centered)
button_frame = tk.Frame(root)
button_frame.pack(pady=20, fill=tk.X)

start_button = tk.Button(button_frame, text="Start", command=start_video_stream, width=50, height=3)
start_button.pack(side=tk.LEFT, padx=20)

close_button = tk.Button(button_frame, text="Close", command=root.quit, width=50, height=3)
close_button.pack(side=tk.LEFT, padx=20)

update_time()  # Start updating the time
update_date()  # Update the date on the start

# Start the Tkinter event loop
root.mainloop()

# Release resources and close OpenCV windows when exiting
cap.release()
cv2.destroyAllWindows()
