import os
import requests
import json

BASE_URL = "https://xkzd75f5kd.execute-api.ap-south-1.amazonaws.com/prod/"

class EnvConfig:
    def __init__(self):
        # Initialize environment variables
        self.access_token = os.getenv('Access-token')
        self.refresh_token = os.getenv('Refresh-token')
        self.employee_id = os.getenv('employeeID')

    def get_token(self):
        if not self.access_token:
            raise ValueError("Access token is not set.")
        return self.access_token

    def set_token(self, accessToken):
        self.access_token = accessToken
        os.environ['Access-token'] = accessToken

    def get_refresh_token(self):
        if not self.refresh_token:
            raise ValueError("Refresh token is not set.")
        return self.refresh_token

    def set_refresh_token(self, refreshToken):
        self.refresh_token = refreshToken
        os.environ['Refresh-token'] = refreshToken
    
    def get_employeeID(self):
        if not self.employee_id:
            raise ValueError("Employee ID is not set.")
        return self.employee_id

    def set_employeeID(self, employeeID):
        self.employee_id = employeeID
        os.environ['employeeID'] = employeeID


class ApiService:
    def __init__(self, env_config):
        self.env_config = env_config

    def sendOtp(self, url, payload):
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(BASE_URL + url, headers=headers, data=payload)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error sending OTP: {e}")
            return None

    def verifyOtp(self, url, payload):
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(BASE_URL + url, headers=headers, data=payload)
            response.raise_for_status()
            response_data = self._get_json_response(response)

            if response_data and response_data.get("status", {}).get("code") == 1001:
                token = response_data.get("token")
                refreshToken = response_data.get("refreshToken")
                employeeID = response_data.get("employee", {}).get("employeeID")

                self.env_config.set_token(token)
                self.env_config.set_refresh_token(refreshToken)
                self.env_config.set_employeeID(employeeID)

            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error verifying OTP: {e}")
            return None

    def getVehicleDetails(self, vehicleNo):
        url = f"customer-flow-handler/get-vehicle-details?vehicleNo={vehicleNo}"
        headers = {'Authorization': "Bearer " + self.env_config.get_token()}
        try:
            response = requests.get(BASE_URL + url, headers=headers)
            response.raise_for_status()
            return self._get_json_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error getting vehicle details: {e}")
            return None

    def createCustomer(self, source, mobileNo, vehicleNo):
        url = "customer-flow-handler/create-customer"
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + self.env_config.get_token()}
        payload = json.dumps({"source": source, "mobileNo": mobileNo, "vehicleNo": vehicleNo, "employeeID": self.env_config.get_employeeID()})
        try:
            response = requests.post(BASE_URL + url, headers=headers, data=payload)
            response.raise_for_status()
            return self._get_json_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error creating customer: {e}")
            return None
    
    def confirmTicket(self, parkingTicketID):
        url = "ticket-handler/confirm-ticket"
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + self.env_config.get_token()}
        payload = json.dumps({"parkingTicketID": parkingTicketID, "requestType": "CONFIRM_TICKET", "employeeID": self.env_config.get_employeeID()})
        try:
            response = requests.post(BASE_URL + url, headers=headers, data=payload)
            response.raise_for_status()
            return self._get_json_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error confirming ticket: {e}")
            return None
    
    def otpExitTicket(self, otp):
        url = "ticket-handler/otp-exit-ticket"
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + self.env_config.get_token()}
        payload = json.dumps({"parkingTicketID": parkingTicketID, "exitOTP": otp})
        try:
            response = requests.post(BASE_URL + url, headers=headers, data=payload)
            response.raise_for_status()
            return self._get_json_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error exiting vehicle: {e}")
            return None
    
    def exitTicket(self, parkingTicketID,employeeID):
        url = "ticket-handler/exit-ticket"
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + self.env_config.get_token()}
        payload = json.dumps({"parkingTicketID": parkingTicketID, "employeeID": employeeID})
        try:
            response = requests.post(BASE_URL + url, headers=headers, data=payload)
            response.raise_for_status()
            return self._get_json_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error exiting vehicle: {e}")
            return None
    
    def parkingCharges(self, parkingTicketID):
        url = "ticket-handler/exit-ticket"
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + self.env_config.get_token()}
        params = {
        'parkingTicketID': parkingTicketID  
        }
        try:
            response = requests.get(BASE_URL + url, headers=headers, params=params)
            response.raise_for_status()
            return self._get_json_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error exiting vehicle: {e}")
            return None
    
    def parkingSpaceDetails(self, parkingSpaceID):
        url = "user-management/parking-space/fetch-parking-space-info/"+ parkingSpaceID
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + self.env_config.get_token()}
        
        try:
            response = requests.get(BASE_URL + url, headers=headers)
            response.raise_for_status()
            return self._get_json_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error exiting vehicle: {e}")
            return None
    
    def employeeDetails(self, employeeID):
        url = "user-management/employee/fetch-employee-info/"+ employeeID
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + self.env_config.get_token()}
        
        try:
            response = requests.get(BASE_URL + url, headers=headers)
            response.raise_for_status()
            return self._get_json_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error exiting vehicle: {e}")
            return None
        
 
    def _get_json_response(self, response):
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Error decoding JSON response: {response.text}")
            return None


def main():
    env_config = EnvConfig()  # Initialize the environment configuration
    api = ApiService(env_config)  # Pass it to the API service

    try:
        mobileNo = input("Input Mobile: ")
        url = "login-service/send-otp"
        payload = json.dumps({"mobileNo": mobileNo})
        print(api.sendOtp(url, payload))

        otp = input("Input OTP: ")
        url = "login-service/verify-otp/employee"
        payload = json.dumps({"mobileNo": mobileNo, "otp": otp})
        print(api.verifyOtp(url, payload))

        vehicleNo = input("Input Vehicle: ")
        vehicle_details = api.getVehicleDetails(vehicleNo)
        if vehicle_details:
            print(vehicle_details)

        # Create a customer (if vehicle details are valid)
        customer_response = api.createCustomer("EMPLOYEE_APP", mobileNo, vehicleNo)
        if customer_response:
            print(customer_response)
            ticketID = customer_response.get("parkingTicketID")
            print("Ticket created with ID:", ticketID)

            input("Press Enter to confirm ticket...")
            confirmation = api.confirmTicket(ticketID)
            print(confirmation)

            exitOtp = input("Exit vehicle enter OTP: ")
            exit_response = api.exitVehicle(ticketID, exitOtp)
            print(exit_response)
        else:
            print("Failed to create customer.")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
