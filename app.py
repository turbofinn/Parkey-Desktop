# from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox
# from PyQt5.QtGui import QFont, QPixmap
# from PyQt5.QtCore import Qt
# from ApiService import ApiService

# class ParkKeyUI(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Parkkey - Key to Parking")
#         self.setGeometry(100, 100, 900, 500)

#         # Main layout
#         main_layout = QHBoxLayout()
#         main_layout.setContentsMargins(0, 0, 0, 0)
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
#         self.mobile_input = QLineEdit()
#         self.mobile_input.setPlaceholderText("Mobile No")
#         self.mobile_input.setFixedSize(400, 40)
#         self.mobile_input.setStyleSheet(
#             "QLineEdit {"
#             "   background-color: #f0f0f0;"
#             "   border-radius: 10px;"
#             "   padding: 5px;"
#             "   border: 1px solid #ccc;"
#             "   margin: 0 auto;"
#             "   width: 100%;"
#             "} "
#         )

#         # OTP Input
#         self.otp_input = QLineEdit()
#         self.otp_input.setPlaceholderText("Otp")
#         self.otp_input.setFixedSize(400, 40)
#         self.otp_input.setStyleSheet(
#             "QLineEdit {"
#             "   background-color: #f0f0f0;"
#             "   border-radius: 10px;"
#             "   padding: 5px;"
#             "   border: 1px solid #ccc;"
#             "   margin: 0 auto;"
#             "   width: 100%;"
#             "} "
#         )

#         # Add inputs to the form layout
#         form_layout.addRow(self.mobile_input)
#         form_layout.addRow(self.otp_input)

#         # Login Button
#         login_button = QPushButton("Login Now")
#         login_button.setStyleSheet("background-color: #118B50; color: white; padding: 10px; border-radius: 5px;")
#         login_button.setFont(QFont("Arial", 8))
#         login_button.setFixedSize(150, 40)
#         login_button.setCursor(Qt.PointingHandCursor)

#         # Connect the button to the validation function
#         login_button.clicked.connect(self.validate_credentials)

#         left_layout.addWidget(logo_label)
#         left_layout.addWidget(login_label)
#         left_layout.addWidget(subheading_label)
#         left_layout.addLayout(form_layout)
#         left_layout.addWidget(login_button, alignment=Qt.AlignCenter)
#         left_layout.setAlignment(Qt.AlignCenter)

#         # Left-side widget
#         left_widget = QWidget()
#         left_widget.setLayout(left_layout)
#         main_layout.addWidget(left_widget)

#         # Right Side Layout
#         right_widget = QWidget()
#         right_widget.setStyleSheet("background-color: #118B50;")
#         right_widget.setMinimumWidth(450)

#         # Overlay Background Image
#         overlay_label = QLabel(right_widget)
#         overlay_pixmap = QPixmap("bgimgtemp.png")
#         overlay_pixmap = overlay_pixmap.scaled(450, 500, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
#         overlay_label.setPixmap(overlay_pixmap)
#         overlay_label.setAlignment(Qt.AlignCenter)

#         main_layout.addWidget(right_widget)
#         self.setLayout(main_layout)

#     def validate_credentials(self):
        

#         entered_mobile = self.mobile_input.text()
#         entered_otp = self.otp_input.text()



# # Run the Application
# app = QApplication([])
# window = ParkKeyUI()
# window.show()
# app.exec_()





























from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import json
from ApiService import ApiService  
from duo import ParkingApp

class ParkKeyUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parkkey - Key to Parking")
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)

        self.api_service = ApiService()  # Initialize API service

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left side layout (Login Form)
        left_layout = QVBoxLayout()

        logo_label = QLabel()
        pixmap = QPixmap("titlepage.png")  # Replace with actual path
        pixmap = pixmap.scaled(500, 700, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        # Login Label
        login_label = QLabel("LOGIN")
        login_label.setFont(QFont("Arial", 30, QFont.Bold))
        login_label.setAlignment(Qt.AlignCenter)

        # Subheading
        subheading_label = QLabel("Streamlining Parking, One Space at a Time.")
        subheading_label.setFont(QFont("Arial", 23))
        subheading_label.setAlignment(Qt.AlignCenter)

        # Form Layout
        form_wrapper = QVBoxLayout()
        form_wrapper.setAlignment(Qt.AlignCenter)

        # Mobile Number Input
        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("Mobile No")
        self.mobile_input.setFixedSize(400, 40)
        

        # OTP Input
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("Otp")
        self.otp_input.setFixedSize(400, 40)
        

        # Add inputs to the form layout
        form_wrapper.addWidget(self.mobile_input, alignment=Qt.AlignCenter)
        form_wrapper.addWidget(self.otp_input, alignment=Qt.AlignCenter)
        

        # Buttons
        send_otp_button = QPushButton("Send OTP")
        send_otp_button.setStyleSheet("background-color: #118B50; color: white; padding: 10px; border-radius: 5px; font-size:20px")
        send_otp_button.setFixedSize(200, 60)
        send_otp_button.clicked.connect(self.send_otp)

        login_button = QPushButton("Login Now")
        login_button.setStyleSheet("background-color: #118B50; color: white; padding: 10px; border-radius: 5px; font-size:20px")
        login_button.setFixedSize(200, 60)
        login_button.clicked.connect(self.validate_credentials)

        # Add widgets to layout
        left_layout.addWidget(logo_label)
        left_layout.addWidget(login_label)
        left_layout.addWidget(subheading_label)
        left_layout.addLayout(form_wrapper)
        left_layout.addWidget(send_otp_button, alignment=Qt.AlignCenter)
        left_layout.addWidget(login_button, alignment=Qt.AlignCenter)
        left_layout.setAlignment(Qt.AlignCenter)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget)

        # Right side
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: #118B50;")
        right_widget.setMinimumWidth(450)
        main_layout.addWidget(right_widget)

        self.setLayout(main_layout)

    def send_otp(self):
        """Send OTP using the API"""
        mobile_number = self.mobile_input.text().strip()
        if not mobile_number.isdigit() or len(mobile_number) != 10:
            QMessageBox.warning(self, "Error", "Enter a valid 10-digit mobile number.")
            return

        url = "login-service/send-otp"
        payload = json.dumps({"mobileNo": mobile_number})
        response = self.api_service.sendOtp(url, payload)

        QMessageBox.information(self, "OTP Sent", "OTP has been sent to your mobile number.")

    def validate_credentials(self):
        """Validate OTP and login the user"""
        mobile_number = self.mobile_input.text().strip()
        otp = self.otp_input.text().strip()

        if not mobile_number.isdigit() or len(mobile_number) != 10:
            QMessageBox.warning(self, "Error", "Enter a valid 10-digit mobile number.")
            return

        if not otp.isdigit() or len(otp) != 4:  # Updated to check for 4-digit OTP
            QMessageBox.warning(self, "Error", "Enter a valid 4-digit OTP.")
            return

        url = "login-service/verify-otp/employee"
        payload = json.dumps({"mobileNo": mobile_number, "otp": otp})
        response = self.api_service.verifyOtp(url, payload)

        response_data = json.loads(response)
        if response_data.get("status", {}).get("code") == 1001:
            QMessageBox.information(self, "Login Successful", "You have logged in successfully!")
            self.parking_window = ParkingApp()  
            self.parking_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid OTP. Please try again.")


# Run the Application
app = QApplication([])
window = ParkKeyUI()
window.show()
app.exec_()