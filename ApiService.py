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
    
    def get_employeeID(self):
        return os.getenv('employeeID')

    def set_employeeID(self, employeeID):
        os.environ['employeeID'] = employeeID


class ApiService:
    def sendOtp(self, url, payload):
        headers = {'Content-Type': 'application/json'}
        response = requests.post(BASE_URL + url, headers=headers, data=payload)
        return response.text

    def verifyOtp(self, url, payload):
        headers = {'Content-Type': 'application/json'}
        response = requests.post(BASE_URL + url, headers=headers, data=payload)
        response_data = self._get_json_response(response)
        
        if response_data and response_data.get("status", {}).get("code") == 1001:
            token = response_data.get("token")
            refreshToken = response_data.get("refreshToken")
            employeeID = response_data.get("employee").get("employeeID")
            
            env_config.set_token(token)
            env_config.set_refresh_token(refreshToken)
            env_config.set_employeeID(employeeID)
        
        return response.text

    def getVehicleDetails(self, vehicleNo):
        print("getVehicleDetails api called")
        url = "customer-flow-handler/get-vehicle-details?vehicleNo=" + vehicleNo
        headers = {'Authorization': "Bearer " + env_config.get_token()}
        response = requests.get(BASE_URL + url, headers=headers)
        return self._get_json_response(response)

    def createCustomer(self, source, mobileNo, vehicleNo):
        print("createCustomer api called")
        url = "customer-flow-handler/create-customer"
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + env_config.get_token()}
        payload = json.dumps({"source": source, "mobileNo": mobileNo, "vehicleNo": vehicleNo,"employeeID":env_config.get_employeeID()})
        print(payload)
        response = requests.post(BASE_URL + url, headers=headers, data=payload)
        return self._get_json_response(response)
    
    def confirmTicket(self, parkingTicketID):
        print("confirmTicket api called")
        url = "ticket-handler/confirm-ticket"
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + env_config.get_token()}
        payload = json.dumps({"parkingTicketID": parkingTicketID, "requestType": "CONFIRM_TICKET", "employeeID":env_config.get_employeeID()})
        print(payload)
        response = requests.post(BASE_URL + url, headers=headers, data=payload)
        return self._get_json_response(response)
    
    def exitVehicle(self, parkingTicketID,otp):
        print("exitVehicle api called")
        url = "ticket-handler/otp-exit-ticket"
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + env_config.get_token()}
        payload = json.dumps({"parkingTicketID": parkingTicketID, "exitOTP": otp})
        response = requests.post(BASE_URL + url, headers=headers, data=payload)
        return self._get_json_response(response)

    def _get_json_response(self, response):
        print(response.text)
        try:
            response_data = response.json()
            return response_data
        except requests.exceptions.JSONDecodeError:
            print(f"Error decoding JSON response: {response.text}")
            print(f"HTTP Status Code: {response.status_code}")
            return None


env_config = EnvConfig()

def main():
    api = ApiService()
    mobileNo = input("Input Mobile: ")
    
    url = "login-service/send-otp"
    payload = json.dumps({"mobileNo": mobileNo})
    print(api.sendOtp(url, payload))

    otp = input("Input OTP: ")

    url = "login-service/verify-otp/employee"
    payload = json.dumps({"mobileNo": mobileNo, "otp": otp})
    print(api.verifyOtp(url, payload))

    vehicleNo = input("Input Vehicle: ")
    print(api.getVehicleDetails(vehicleNo))

    # print(api.createCustomer("EMPLOYEE_APP", mobileNo, vehicleNo))

    ticketID = api.createCustomer("EMPLOYEE_APP", mobileNo, vehicleNo)
    print(ticketID)

    input("Confirm Ticket")

    print(api.confirmTicket(ticketID.get("parkingTicketID")))

    exitOtp = input("Exit vehicle enter otp ")
    print(api.exitVehicle(ticketID.get("parkingTicketID"),exitOtp))


if __name__ == "__main__":
    main()


# 8960880615
# UP32TY1234