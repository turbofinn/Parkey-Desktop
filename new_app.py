from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer
import json
import traceback  # Added for error handling
from api.ApiService import ApiService 
from api.ApiService import EnvConfig
import os
import sys 
from middleui import ParkingApp 


image_path = "assets/titlepage.png"

class ParkKeyUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parkkey - Key to Parking")
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        env_config = EnvConfig()
        self.api_service = ApiService(env_config)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_layout = QVBoxLayout()

        logo_label = QLabel()
        pixmap = QPixmap(image_path) 
        pixmap = pixmap.scaled(500, 700, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)

        login_label = QLabel("LOGIN")
        login_label.setFont(QFont("Arial", 30, QFont.Bold))
        login_label.setAlignment(Qt.AlignCenter)

        subheading_label = QLabel("Streamlining Parking, One Space at a Time.")
        subheading_label.setFont(QFont("Arial", 23))
        subheading_label.setAlignment(Qt.AlignCenter)

        form_wrapper = QVBoxLayout()
        form_wrapper.setAlignment(Qt.AlignCenter)

        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("Mobile No")
        self.mobile_input.setFixedSize(400, 40)
        self.mobile_input.textChanged.connect(self.check_mobile_number)
   
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("OTP")
        self.otp_input.setFixedSize(400, 40)
        
        form_wrapper.addWidget(self.mobile_input, alignment=Qt.AlignCenter)
        form_wrapper.addWidget(self.otp_input, alignment=Qt.AlignCenter)
        
        # Status label for OTP sent message
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #118B50;")
        

        # Modified login button to show loading state
        self.login_button = QPushButton("Login Now")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #009688; 
                color: white; 
                padding: 10px; 
                border-radius: 5px; 
                font-size: 20px;
            }
            QPushButton:disabled {
                background-color: #118B50;
                color: white;
                opacity: 0.7;
            }
        """)
        self.login_button.setFixedSize(200, 60)
        self.login_button.clicked.connect(self.validate_credentials)
      
        left_layout.addWidget(logo_label)
        left_layout.addWidget(login_label)
        left_layout.addWidget(subheading_label)
        left_layout.addLayout(form_wrapper)
        left_layout.addWidget(self.status_label)
        left_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        left_layout.setAlignment(Qt.AlignCenter)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget)

        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: #009688;")
        right_widget.setMinimumWidth(450)
        main_layout.addWidget(right_widget)

        self.setLayout(main_layout)

    def check_mobile_number(self):
        """Check if mobile number is valid and send OTP automatically"""
        mobile_number = self.mobile_input.text().strip()
        if len(mobile_number) == 10 and mobile_number.isdigit():
            self.send_otp_auto(mobile_number)

    def send_otp_auto(self, mobile_number):
        """Send OTP automatically when valid mobile number is entered"""
        self.status_label.setText("Sending OTP...")
        self.status_label.setStyleSheet("color: #118B50;font-weight: bold; font-size: 18px;")
        
        # Simulate API call with a delay (replace with actual API call)
        QTimer.singleShot(1000, lambda: self.complete_otp_sending(mobile_number))

    def complete_otp_sending(self, mobile_number):
        """Complete the OTP sending process"""
        url = "login-service/send-otp"
        payload = json.dumps({"mobileNo": mobile_number})
        response = self.api_service.sendOtp(url, payload)
        
        # Check response and update status
        if response:
            self.status_label.setText("OTP has been sent to your mobile number.")
            self.status_label.setStyleSheet("color: green;font-weight: bold; font-size: 18px;")
        else:
            self.status_label.setText("Failed to send OTP. Please try again.")
            self.status_label.setStyleSheet("color: red;font-weight: bold; font-size: 18px;")

    def validate_credentials(self):
        """Validate OTP and login the user"""
        mobile_number = self.mobile_input.text().strip()
        otp = self.otp_input.text().strip()

        if not mobile_number.isdigit() or len(mobile_number) != 10:
            self.status_label.setText("Enter a valid 10-digit mobile number.")
            self.status_label.setStyleSheet("color: red;font-weight: bold; font-size: 18px;")
            return

        if not otp.isdigit() or len(otp) != 4: 
            self.status_label.setText("Enter a valid 4-digit OTP.")
            self.status_label.setStyleSheet("color: red;font-weight: bold; font-size: 18px;")
            return

        # Disable the button and change its text to show loading
        self.login_button.setText("Verifying...")
        self.login_button.setEnabled(False)
        
        # Simulate API call with delay (replace with actual API call)
        QTimer.singleShot(2000, lambda: self.complete_validation(mobile_number, otp))

    def complete_validation(self, mobile_number, otp):
        """Complete the validation process after API call"""
        try:
            # Re-enable the button and restore its original text
            self.login_button.setText("Login Now")
            self.login_button.setEnabled(True)
            
            url = "login-service/verify-otp/employee"
            payload = json.dumps({"mobileNo": mobile_number, "otp": otp})
            response = self.api_service.verifyOtp(url, payload)
            
            # Safely parse the response
            if response:
                response_data = json.loads(response)
                if response_data.get("status", {}).get("code") == 1001:
                    self.parking_window = ParkingApp()  
                    self.parking_window.show()
                    self.close()
                else:
                    # Display error message in status label
                    error_message = response_data.get("status", {}).get("message", "Invalid OTP")
                    self.status_label.setText(error_message)
                    self.status_label.setStyleSheet("color: red;")
            else:
                # No response from server
                self.status_label.setText("Wrong OTP, Please try again.")
                self.status_label.setStyleSheet("color: red;")
        
        except json.JSONDecodeError:
            # Handle JSON decoding error
            self.status_label.setText("Invalid response from server.")
            self.status_label.setStyleSheet("color: red;")
        except Exception as e:
            # Catch any unexpected errors
            self.status_label.setText(f"An unexpected error occurred: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
            # Optional: print full traceback for debugging
            print(traceback.format_exc())


def exception_hook(exc_type, exc_value, exc_traceback):
    """Global exception handler to prevent application termination"""
    print("An error occurred:", exc_value)
    # Optionally log the full traceback
    # traceback.print_tb(exc_traceback)

# Set the global exception hook
sys.excepthook = exception_hook

app = QApplication([])

window = ParkKeyUI()
window.show()
app.exec_()