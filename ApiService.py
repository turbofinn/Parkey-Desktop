import os
import requests
import json

BASE_URL = "https://xkzd75f5kd.execute-api.ap-south-1.amazonaws.com/prod/"

class EnvConfig:
    def __init__(self):
        pass

    def get_token(self):
        return os.getenv('Access-token')

    def set_token(self, accessToken):
        os.environ['Access-token'] = accessToken

    def get_refresh_token(self):
        return os.getenv('Refresh-token')

    def set_refresh_token(self, refreshToken):
        os.environ['Refresh-token'] = refreshToken


class ApiService:
    def sendOtp(self, url, payload):
        headers = {'Content-Type': 'application/json'}
        response = requests.post(BASE_URL + url, headers=headers, data=payload)
        print(response.text)
        return response.text

    def verifyOtp(self, url, payload):
        headers = {'Content-Type': 'application/json'}
        response = requests.post(BASE_URL + url, headers=headers, data=payload)
        print(response.text)
        response_data = response.json()
        
        if response_data.get("status", {}).get("code") == 1001:
            token = response_data.get("token")
            refreshToken = response_data.get("refreshToken")
            
            env_config.set_token(token)
            env_config.set_refresh_token(refreshToken)
        
        return response.text

    def getVehicleDetails(self, vehicleNo):
        url = "customer-flow-handler/get-vehicle-details?vehicleNo="+vehicleNo
        headers = {'Authorization': "Bearer "+ self.env_config.get_token()}
        response = requests.get(BASE_URL + url, headers=headers)
        response_data = response.json()
        return response_data

    def getCreateCustomer(self, mobileNo, vehicleNo):
        # URL of the API endpoint
        url = "customer-flow-handler/create-customer"
        source = "EMPLOYEE_DESKTOP"
        empID = self.env_config.get_token()
        headers = { "Content-Type": "application/json","Authorization": "Bearer "+ self.env_config.get_token()}  
        payload = json.dumps({"source": source,"mobileNo": mobileNo,"vehicleNo": vehicleNo, "employeeID": empID})
        
        response = requests.post(BASE_URL + url, headers=headers, data=payload)
       
        response_data = response.json()
        return response_data


    def confirmTicket(self, parkingTicketID):
        url = "ticket-handler/confirm-ticket"
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + self.env_config.get_token()}
        empID = self.env_config.get_token()
        payload = json.dumps({"parkingTicketID": parkingTicketID, "requestType": "CONFIRM_TICKET", "employeeID": self.env_config.get_token()})
        try:
            response = requests.post(BASE_URL + url, headers=headers, data=payload)
            response.raise_for_status()
            return self._get_json_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error confirming ticket: {e}")
            return None
        
    #  ALL EXIT Api
    

    def otpExitTicket(self, otp, parkingTicketID):
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
    
    def exitTicket(self, parkingTicketID):
        url = "ticket-handler/exit-ticket"
        empID = self.env_config.get_token()
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + self.env_config.get_token()}
        payload = json.dumps({"parkingTicketID": parkingTicketID, "employeeID": empID})
        try:
            response = requests.post(BASE_URL + url, headers=headers, data=payload)
            response.raise_for_status()
            return self._get_json_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error exiting vehicle: {e}")
            return None
    
    def parkingCharges(self, parkingTicketID):
        url = "ticket-handler/get-parking-charges"
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
    
    def employeeDetails(self):
        url = "user-management/employee/fetch-employee-info/"+ self.env_config.get_token()
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
        
    


env_config = EnvConfig()

def main():
    api = ApiService()
    # mobileNo = input("Input Mobile: ")
    mobileNo = "9004263507"
    
    url = "login-service/send-otp"
    payload = json.dumps({"mobileNo": mobileNo})
    # print(api.sendOtp(url, payload))

    otp = input("Input OTP: ")

    url = "login-service/verify-otp/employee"
    payload = json.dumps({"mobileNo": mobileNo, "otp": otp})
    # print(api.verifyOtp(url, payload))


    # # vehicleNo = input("Input OTP: ")
    vehicleNo = "UP32TY5645"
   
    # print(api.getCreateCustomer("8585588585", "UP32TY5645"))

if __name__ == "__main__":
    main()

#7985157933
#UP32TY5645