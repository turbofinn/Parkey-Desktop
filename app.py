

# from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QStackedLayout, QMessageBox
# from PyQt5.QtGui import QFont, QPixmap
# from PyQt5.QtCore import Qt

# class ParkKeyUI(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Parkkey - Key to Parking")
#         self.setGeometry(100, 100, 900, 500)

#         # Main layout
#         main_layout = QHBoxLayout()
#         main_layout.setContentsMargins(0, 0, 0, 0)  # Remove outer margins
#         main_layout.setSpacing(0)
#         # Left side layout (Login Form)
#         left_layout = QVBoxLayout()

#         logo_label = QLabel()
#         pixmap = QPixmap("titlepage.png")  # Replace with the actual path to your image
#         pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
#         logo_label.setPixmap(pixmap)
#         logo_label.setAlignment(Qt.AlignCenter)

#         # Login Label
#         login_label = QLabel("LOGIN")
#         login_label.setFont(QFont("Arial", 20, QFont.Bold))
#         login_label.setAlignment(Qt.AlignCenter)

#         # Subheading
#         subheading_label = QLabel("Streamlining Parking, One Space at a Time.")
#         subheading_label.setFont(QFont("Arial", 10))
#         subheading_label.setAlignment(Qt.AlignCenter)

#         # Create Form Layout and Adjust Inputs
#         form_layout = QFormLayout()

#         # Mobile Number Input
#         mobile_input = QLineEdit()
#         mobile_input.setPlaceholderText("Mobile No")
#         mobile_input.setFixedSize(400, 40)  # Fixed size for the textbox
#         mobile_input.setStyleSheet(
#             "QLineEdit {"
#             "   background-color: #f0f0f0;"  # Light grey background
#             "   border-radius: 10px;"         # Curved borders
#             "   padding: 5px;"                # Padding inside the textbox
#             "   border: 1px solid #ccc;"      # Border color
#             "   margin: 0 auto;"
#             "   width: 100%;"
#             "} "
#         )

#         # OTP Input
#         otp_input = QLineEdit()
#         otp_input.setPlaceholderText("Otp")
#         otp_input.setFixedSize(400, 40)  # Fixed size for the textbox
#         otp_input.setStyleSheet(
#             "QLineEdit {"
#             "   background-color: #f0f0f0;"  # Light grey background
#             "   border-radius: 10px;"         # Curved borders
#             "   padding: 5px;"                # Padding inside the textbox
#             "   border: 1px solid #ccc;"      # Border color
#             "   margin: 0 auto;"
#             "   width: 100%;"
#             "} "
#         )

#         # Adjust alignment by using empty spacers to center the widgets
#         form_layout.addRow(mobile_input)
#         form_layout.addRow(otp_input)

#         # Center the layout horizontally
#         form_layout.setAlignment(Qt.AlignCenter)  # Ensure that widgets are aligned in the center

#         # Login Button
#         login_button = QPushButton("Login Now")
#         login_button.setStyleSheet("background-color: #118B50; color: white; padding: 10px; border-radius: 5px;")
#         login_button.setFont(QFont("Arial", 8))
#         login_button.setFixedSize(150, 40)
#         login_button.setCursor(Qt.PointingHandCursor)
        

#         # Adjust Layout Spacing: Reduce gap between logo and login label
#         left_layout.addWidget(logo_label)
#         left_layout.addSpacing(10)  # Reduced spacing here between logo and login label
#         left_layout.addWidget(login_label)
#         left_layout.addSpacing(10)  # Reduced spacing here between login label and form inputs
#         left_layout.addWidget(subheading_label)
#         left_layout.addSpacing(20)  # Normal spacing here
#         left_layout.addLayout(form_layout)
#         left_layout.addWidget(login_button, alignment=Qt.AlignCenter)
#         left_layout.setAlignment(Qt.AlignCenter)

#         # Create the left-side widget and add to main layout
#         left_widget = QWidget()
#         left_widget.setLayout(left_layout)
#         main_layout.addWidget(left_widget)

#  # Right Side Layout
#         right_widget = QWidget()
#         right_widget.setStyleSheet("background-color: #118B50;")  # Green background
#         right_widget.setMinimumWidth(450)  # Maintain the original width

#         # Overlay Background Image
#         overlay_label = QLabel(right_widget)
#         overlay_pixmap = QPixmap("bgimgtemp.png")  # Replace with the background image path
#         overlay_pixmap = overlay_pixmap.scaled(450, 500, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)  # Full width and height
#         overlay_label.setPixmap(overlay_pixmap)
#         overlay_label.setAlignment(Qt.AlignCenter)
#         overlay_label.move(0, 0)  # Position it at the top-left corner

#         car_image_label = QLabel(right_widget)
#         car_pixmap = QPixmap("carimage.png")  # Replace with the path to your car image

#         # Increase the height of the car image and set a larger width (you can adjust these values as needed)
#         car_pixmap = car_pixmap.scaled(350, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Height is now 500

#         # Set the image to the label
#         car_image_label.setPixmap(car_pixmap)

#         # Apply a larger curve to the borders (increased to 50px for more curvature)
#         car_image_label.setStyleSheet("border-radius: 50px;")  # Larger curve

#         # Set the alignment of the image to center it
#         car_image_label.setAlignment(Qt.AlignCenter)

#         # Position the car image over the background (adjust these values as needed)
#         car_image_label.move(75, 50)  # Adjust the position if necessary

#         text_label = QLabel("From crowded lots to open spaces,\nwe make parking faster, easier, and smarter.", right_widget)
#         text_label.setFont(QFont("Arial", 12))  # Set the font and size
#         text_label.setStyleSheet("color: white; text-align: center;")  # White text and centered
#         text_label.setAlignment(Qt.AlignCenter)

#         # Position the text label below the car image
#         text_label.move(75, 650)


#         # Add the right widget to the main layout
#         main_layout.addWidget(right_widget)

#         # Set the main layout for the window
#         self.setLayout(main_layout)
#         self.setWindowTitle("Parkkey UI")
#         self.resize(900, 500)


    

# # Run the Application
# app = QApplication([])
# window = ParkKeyUI()
# window.show()
# app.exec_()




















































from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

class ParkKeyUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parkkey - Key to Parking")
        self.setGeometry(100, 100, 900, 500)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left side layout (Login Form)
        left_layout = QVBoxLayout()

        logo_label = QLabel()
        pixmap = QPixmap("titlepage.png")  # Replace with the actual path to your image
        pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        # Login Label
        login_label = QLabel("LOGIN")
        login_label.setFont(QFont("Arial", 20, QFont.Bold))
        login_label.setAlignment(Qt.AlignCenter)

        # Subheading
        subheading_label = QLabel("Streamlining Parking, One Space at a Time.")
        subheading_label.setFont(QFont("Arial", 10))
        subheading_label.setAlignment(Qt.AlignCenter)

        # Create Form Layout and Adjust Inputs
        form_layout = QFormLayout()

        # Mobile Number Input
        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("Mobile No")
        self.mobile_input.setFixedSize(400, 40)
        self.mobile_input.setStyleSheet(
            "QLineEdit {"
            "   background-color: #f0f0f0;"
            "   border-radius: 10px;"
            "   padding: 5px;"
            "   border: 1px solid #ccc;"
            "   margin: 0 auto;"
            "   width: 100%;"
            "} "
        )

        # OTP Input
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("Otp")
        self.otp_input.setFixedSize(400, 40)
        self.otp_input.setStyleSheet(
            "QLineEdit {"
            "   background-color: #f0f0f0;"
            "   border-radius: 10px;"
            "   padding: 5px;"
            "   border: 1px solid #ccc;"
            "   margin: 0 auto;"
            "   width: 100%;"
            "} "
        )

        # Add inputs to the form layout
        form_layout.addRow(self.mobile_input)
        form_layout.addRow(self.otp_input)

        # Login Button
        login_button = QPushButton("Login Now")
        login_button.setStyleSheet("background-color: #118B50; color: white; padding: 10px; border-radius: 5px;")
        login_button.setFont(QFont("Arial", 8))
        login_button.setFixedSize(150, 40)
        login_button.setCursor(Qt.PointingHandCursor)

        # Connect the button to the validation function
        login_button.clicked.connect(self.validate_credentials)

        left_layout.addWidget(logo_label)
        left_layout.addWidget(login_label)
        left_layout.addWidget(subheading_label)
        left_layout.addLayout(form_layout)
        left_layout.addWidget(login_button, alignment=Qt.AlignCenter)
        left_layout.setAlignment(Qt.AlignCenter)

        # Left-side widget
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget)

        # Right Side Layout
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: #118B50;")
        right_widget.setMinimumWidth(450)

        # Overlay Background Image
        overlay_label = QLabel(right_widget)
        overlay_pixmap = QPixmap("bgimgtemp.png")
        overlay_pixmap = overlay_pixmap.scaled(450, 500, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        overlay_label.setPixmap(overlay_pixmap)
        overlay_label.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(right_widget)
        self.setLayout(main_layout)

    def validate_credentials(self):
        # Hardcoded credentials
        valid_mobile = "9004263507"
        valid_otp = "1234"

        entered_mobile = self.mobile_input.text()
        entered_otp = self.otp_input.text()

        if entered_mobile == valid_mobile and entered_otp == valid_otp:
            QMessageBox.information(self, "Success", "Login Successful!")
        else:
            QMessageBox.critical(self, "Error", "Invalid Mobile Number or OTP!")


# Run the Application
app = QApplication([])
window = ParkKeyUI()
window.show()
app.exec_()
