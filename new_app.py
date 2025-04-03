from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
import json
import traceback
import sys
import os
from api.ApiService import ApiService, EnvConfig
from middleui import ParkingApp

class ParkKeyUI(QWidget):
    def __init__(self):
        super().__init__()
        # Basic window setup
        self.setWindowTitle("Parkkey - Key to Parking")
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        
        # Initialize API service
        env_config = EnvConfig()
        self.api_service = ApiService(env_config)

        # Main layout - exact match to screenshot
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left panel - White background with logo
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #F7F7F7; border-top-left-radius: 20px; border-bottom-left-radius: 20px;")
                        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignCenter)
        left_layout.setContentsMargins(50, 50, 50, 50)
                
        # Single image for the entire left panel
        image_label = QLabel()
        image_path = "assets/left_panel_image.jpg"
        if os.path.exists(image_path):
            self.original_pixmap = QPixmap(image_path)
            # We'll set the actual size in the resizeEvent initially
            image_label.setPixmap(self.original_pixmap.scaled(800, 1600, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            # Store reference to the label for resizing
            self.image_label = image_label
        else:
            # Placeholder if image is missing
            image_label.setText("Image Not Found")
            image_label.setFont(QFont("Arial", 18, QFont.Bold))
            image_label.setStyleSheet("color: #006c45;")
        image_label.setAlignment(Qt.AlignCenter)
                
        left_layout.addWidget(image_label, alignment=Qt.AlignCenter)
        
        # Right panel - Blue background with form
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            background-color: #0077b6;
            border-top-right-radius: 20px;
            border-bottom-right-radius: 20px;
        """)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)  # Remove margin for perfect centering
        right_layout.setAlignment(Qt.AlignCenter)  # Center alignment for the entire layout
        right_layout.setSpacing(0)  # Remove spacing for tight layout

        # Create a centered container for the login form
        login_container = QWidget()
        login_layout = QVBoxLayout(login_container)
        login_layout.setContentsMargins(30, 30, 30, 30)
        login_layout.setAlignment(Qt.AlignCenter)
        login_layout.setSpacing(10)  # Reduced spacing between elements

        # Login Dashboard header
        login_header = QLabel("Login Dashboard")
        login_header.setFont(QFont("Arial", 28, QFont.Bold))
        login_header.setAlignment(Qt.AlignLeft)  # Center the header
        login_header.setStyleSheet("color: white; margin-bottom: 20px;")  # Reduced margin

        # Mobile input field with icon
        mobile_container = QWidget()
        mobile_container.setFixedSize(600, 70)
        mobile_container.setStyleSheet("background-color: white; border-radius: 8px;")
        
        mobile_layout = QHBoxLayout(mobile_container)
        mobile_layout.setContentsMargins(15, 0, 15, 0)
        mobile_layout.setSpacing(20)
        
        # Mobile icon
       
        mobile_icon = QLabel()
        # Load your image (replace "otp_icon.png" with your actual image path)
        pixmap = QPixmap("assets/Solid.png")  # e.g., "assets/otp_icon.png"
        # Scale the image to fit while maintaining aspect ratio
        mobile_icon.setPixmap(pixmap.scaled(26, 26, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        mobile_icon.setFixedSize(26, 26)
        mobile_icon.setStyleSheet("background: transparent;")
        
        # Mobile input
        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("Mobile No")
        self.mobile_input.setFont(QFont("Arial", 12))
        self.mobile_input.setStyleSheet("""
            QLineEdit {
                border: none;
                color: #555555;
                background: transparent;
            }
        """)
        self.mobile_input.textChanged.connect(self.check_mobile_number)
        
        mobile_layout.addWidget(mobile_icon)
        mobile_layout.addWidget(self.mobile_input)

        # OTP input field with icon
        otp_container = QWidget()
        otp_container.setFixedSize(600, 70)
        otp_container.setStyleSheet("background-color: white; border-radius: 8px;")
        
        otp_layout = QHBoxLayout(otp_container)
        otp_layout.setContentsMargins(15, 0, 15, 0)
        otp_layout.setSpacing(20)
        
        # OTP icon
        otp_icon = QLabel()
        # Load your image (replace "otp_icon.png" with your actual image path)
        pixmap = QPixmap("assets/Solid.png")  # e.g., "assets/otp_icon.png"
        # Scale the image to fit while maintaining aspect ratio
        otp_icon.setPixmap(pixmap.scaled(26, 26, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        otp_icon.setFixedSize(26, 26)
        otp_icon.setStyleSheet("background: transparent;")
        
        # OTP input
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("OTP")
        self.otp_input.setFont(QFont("Arial", 12))
        self.otp_input.setStyleSheet("""
            QLineEdit {
                border: none;
                color: #555555;
                background: transparent;
            }
        """)
        
        otp_layout.addWidget(otp_icon)
        otp_layout.addWidget(self.otp_input)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setStyleSheet("color: white;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setFixedHeight(30)

        # Next button - centered
        button_container = QWidget()
        button_container.setFixedWidth(600)
        
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignCenter)
        
        self.login_button = QPushButton("Next")
        self.login_button.setFixedSize(180, 70)
        self.login_button.setFont(QFont("Arial", 16))
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #0c8964;
                color: white;
                border-radius: 8px;
                padding-right: 15px;
                text-align: center;
                padding-left: 15px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #096e4f;
            }
            QPushButton:pressed {
                background-color: #086a4d;
            }
            QPushButton:disabled {
                background-color: #90c0b0;
                color: #e0e0e0;
            }
            QPushButton:focus {  /* Add this to remove focus outline */
                outline: none;
                border: none;
            }                            
        """)
        self.login_button.setFocusPolicy(Qt.NoFocus)
        self.login_button.setText("Next")  # Include the arrow in the text itself
        self.login_button.clicked.connect(self.validate_credentials)
        
     
        arrow_label = QLabel(self.login_button)
        arrow_label.setText("›")
        arrow_label.setFont(QFont("Arial", 18, QFont.Bold))
        arrow_label.setStyleSheet("color: white; background: transparent;")
        arrow_label.setAttribute(Qt.WA_TransparentForMouseEvents)  # Make it ignore mouse events
        arrow_label.setFocusPolicy(Qt.NoFocus)  # Prevent it from getting focus
        arrow_label.setGeometry(140, 18, 30, 30) 

        
        button_layout.addWidget(self.login_button)

        # Horizontal line
        line_frame = QFrame()
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("background-color: white;")
        line_frame.setFixedHeight(2)
        line_frame.setFixedWidth(600)

        # Resend OTP link - aligned right
        resend_container = QWidget()
        resend_container.setFixedWidth(600)
        
        resend_layout = QHBoxLayout(resend_container)
        resend_layout.setContentsMargins(0, 0, 0, 0)
        
        self.resend_label = QLabel("resend otp")
        self.resend_label.setFont(QFont("Arial", 12))
        self.resend_label.setStyleSheet("color: white; text-decoration: none;")
        # Fix cursor property by using proper Qt way
        self.resend_label.setCursor(Qt.PointingHandCursor)
        self.resend_label.setAlignment(Qt.AlignRight)
        self.resend_label.mousePressEvent = self.resend_otp_clicked
        
        resend_layout.addStretch()
        resend_layout.addWidget(self.resend_label)

        # Add all elements to the login container with minimal spacing
        login_layout.addWidget(login_header)
        login_layout.addSpacing(10)
        login_layout.addWidget(mobile_container, alignment=Qt.AlignCenter)
        login_layout.addSpacing(30)  # Small gap between input fields
        login_layout.addWidget(otp_container, alignment=Qt.AlignCenter)
        login_layout.addWidget(self.status_label)
        login_layout.addSpacing(10)
        login_layout.addWidget(button_container, alignment=Qt.AlignCenter)
        login_layout.addSpacing(20)
        login_layout.addWidget(line_frame, alignment=Qt.AlignCenter)
        login_layout.addSpacing(20)
        login_layout.addWidget(resend_container, alignment=Qt.AlignCenter)

        # Add login container to right panel
        right_layout.addWidget(login_container, alignment=Qt.AlignCenter)

        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
        
        # Set the final layout
        container = QWidget()
        container.setLayout(main_layout)
        container.setStyleSheet("background-color: #F7F7F7; border-radius: 20px;")
        
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(30, 30, 30, 30)
        outer_layout.addWidget(container)
        self.setStyleSheet("background-color: #E6F2F7;")
        
        # Store reference to left panel for resizing
        self.left_panel = left_panel
        
        # Initialize UI states
        self.mobile_input.setFocus()

    def resizeEvent(self, event):
        """Handle window resize events to adjust the image size"""
        super().resizeEvent(event)
        
        # Only proceed if we have an image and left panel
        if hasattr(self, 'original_pixmap') and hasattr(self, 'left_panel'):
            # Calculate available space in left panel (accounting for margins)
            panel_width = self.left_panel.width() - 100
            panel_height = self.left_panel.height() - 100
            
            if panel_width > 0 and panel_height > 0:
                # Find the image label in the layout
                for i in range(self.left_panel.layout().count()):
                    widget = self.left_panel.layout().itemAt(i).widget()
                    if isinstance(widget, QLabel) and widget.pixmap() is not None:
                        # Resize the image to fit the panel while maintaining aspect ratio
                        scaled_pixmap = self.original_pixmap.scaled(
                            panel_width, 
                            panel_height,
                            Qt.KeepAspectRatio, 
                            Qt.SmoothTransformation
                        )
                        widget.setPixmap(scaled_pixmap)
                        break

    def check_mobile_number(self):
        """Check if mobile number is valid and send OTP automatically"""
        mobile_number = self.mobile_input.text().strip()
        if len(mobile_number) == 10 and mobile_number.isdigit():
            self.send_otp_auto(mobile_number)

    def send_otp_auto(self, mobile_number):
        """Send OTP automatically when valid mobile number is entered"""
        self.status_label.setText("Sending OTP...")
        self.status_label.setStyleSheet("color: white;")
        
        # API call with delay
        QTimer.singleShot(1000, lambda: self.complete_otp_sending(mobile_number))

    def complete_otp_sending(self, mobile_number):
        """Complete the OTP sending process"""
        try:
            url = "login-service/send-otp"
            payload = json.dumps({"mobileNo": mobile_number})
            response = self.api_service.sendOtp(url, payload)
            
            # Check response and update status
            if response:
                self.status_label.setText("OTP sent successfully!")
                self.status_label.setStyleSheet("color: white;")
                self.otp_input.setFocus()
            else:
                self.status_label.setText("Failed to send OTP. Please try again.")
                self.status_label.setStyleSheet("color: #ffcccc;")
        except Exception as e:
            self.status_label.setText("Error sending OTP.")
            self.status_label.setStyleSheet("color: #ffcccc;")
            print(f"Error sending OTP: {str(e)}")

    def resend_otp_clicked(self, event):
        """Handle resend OTP click"""
        mobile_number = self.mobile_input.text().strip()
        if len(mobile_number) == 10 and mobile_number.isdigit():
            self.send_otp_auto(mobile_number)
        else:
            self.status_label.setText("Please enter a valid mobile number first.")
            self.status_label.setStyleSheet("color: #ffcccc;")

    def validate_credentials(self):
        """Validate OTP and login the user"""
        mobile_number = self.mobile_input.text().strip()
        otp = self.otp_input.text().strip()

        if not mobile_number.isdigit() or len(mobile_number) != 10:
            self.status_label.setText("Please enter a valid 10-digit mobile number.")
            self.status_label.setStyleSheet("color: #ffcccc;")
            return

        if not otp.isdigit() or len(otp) != 4:
            self.status_label.setText("Please enter a valid 4-digit OTP.")
            self.status_label.setStyleSheet("color: #ffcccc;")
            return

        # Show login in progress
        original_text = self.login_button.text()
        self.login_button.setText("...")
        self.login_button.setEnabled(False)
        
        # API call with delay
        QTimer.singleShot(1000, lambda: self.complete_validation(mobile_number, otp, original_text))

    def complete_validation(self, mobile_number, otp, original_button_text):
        """Complete the validation process after API call"""
        try:
            # Reset button
            self.login_button.setText(original_button_text)
            self.login_button.setEnabled(True)
            
            url = "login-service/verify-otp/employee"
            payload = json.dumps({"mobileNo": mobile_number, "otp": otp})
            response = self.api_service.verifyOtp(url, payload)
            
            if response:
                try:
                    response_data = json.loads(response)
                    if response_data.get("status", {}).get("code") == 1001:
                        # Success
                        self.status_label.setText("Login successful!")
                        self.status_label.setStyleSheet("color: white;")
                        
                        # Open main window after delay
                        QTimer.singleShot(1000, self.open_main_window)
                    else:
                        # Show error from API
                        error_message = response_data.get("status", {}).get("message", "Invalid OTP")
                        self.status_label.setText(error_message)
                        self.status_label.setStyleSheet("color: #ffcccc;")
                except json.JSONDecodeError:
                    self.status_label.setText("Invalid response from server.")
                    self.status_label.setStyleSheet("color: #ffcccc;")
            else:
                self.status_label.setText("Wrong OTP. Please try again.")
                self.status_label.setStyleSheet("color: #ffcccc;")
                
        except Exception as e:
            self.status_label.setText("An error occurred. Please try again.")
            self.status_label.setStyleSheet("color: #ffcccc;")
            print(f"Login error: {str(e)}")
            print(traceback.format_exc())

    def open_main_window(self):
        """Open the main application window"""
        try:
            self.parking_window = ParkingApp()
            self.parking_window.show()
            self.close()
        except Exception as e:
            self.status_label.setText("Error loading main window.")
            self.status_label.setStyleSheet("color: #87CEFA;")
            print(f"Error opening main window: {str(e)}")
            print(traceback.format_exc())

def exception_hook(exc_type, exc_value, exc_traceback):
    """Global exception handler to prevent application termination"""
    print("An error occurred:", exc_value)
    traceback.print_exception(exc_type, exc_value, exc_traceback)

if __name__ == "__main__":
    # Set the global exception hook
    sys.excepthook = exception_hook
    
    app = QApplication([])
    window = ParkKeyUI()
    window.show()
    sys.exit(app.exec_())