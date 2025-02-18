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
        headers = {'Authorization': "Bearer "+ "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJncmFudF90eXBlIjoiYXV0aG9yaXphdGlvbi10b2tlbiIsInVzZXJUeXBlIjoiRU1QTE9ZRUUiLCJpc3MiOiJQYXJra2V5Iiwic3ViIjoiMWQyMzNhNzktOTcyYS00ZDA5LTk2MTktZDc0MTE5OGMwNDQwIiwianRpIjoiYTBmYzQ1MDYtMGIzNC00MzkwLTkxOTYtNTg4Njg4ZGVmNDhlIiwiaWF0IjoxNzM4OTEzMjAzLCJleHAiOjIwNTQyNzMyMDN9.gJZDoGrAqMt7oCZ-7urIR3DDu4jZQPt1tvVvmo5Hat0"}
        response = requests.get(BASE_URL + url, headers=headers)
        response_data = response.json()
        return response_data

    def getCreateCustomer(self, mobileNo, vehicleNo):
        # URL of the API endpoint
        url = "customer-flow-handler/create-customer"
        source = "EMPLOYEE_DESKTOP"
        empID = "5ec10c00-7eff-48c9-ada3-bce66129246d"
        headers = { "Content-Type": "application/json","Authorization": "Bearer "+ "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJncmFudF90eXBlIjoiYXV0aG9yaXphdGlvbi10b2tlbiIsInVzZXJUeXBlIjoiRU1QTE9ZRUUiLCJpc3MiOiJQYXJra2V5Iiwic3ViIjoiMWQyMzNhNzktOTcyYS00ZDA5LTk2MTktZDc0MTE5OGMwNDQwIiwianRpIjoiYTBmYzQ1MDYtMGIzNC00MzkwLTkxOTYtNTg4Njg4ZGVmNDhlIiwiaWF0IjoxNzM4OTEzMjAzLCJleHAiOjIwNTQyNzMyMDN9.gJZDoGrAqMt7oCZ-7urIR3DDu4jZQPt1tvVvmo5Hat0"}  
        payload = json.dumps({"source": source,"mobileNo": mobileNo,"vehicleNo": vehicleNo, "employeeID": empID})
        
        response = requests.post(BASE_URL + url, headers=headers, data=payload)
       
        response_data = response.json()
        return response_data


    def confirmTicket(self, parkingTicketID):
        url = "ticket-handler/confirm-ticket"
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyVHlwZSI6IkVNUExPWUVFIiwiZ3JhbnRfdHlwZSI6ImF1dGhvcml6YXRpb24tdG9rZW4iLCJpc3MiOiJQYXJra2V5Iiwic3ViIjoiMWQyMzNhNzktOTcyYS00ZDA5LTk2MTktZDc0MTE5OGMwNDQwIiwianRpIjoiZjgzNTc4NmUtNWY3Ny00YzRiLThkNDMtMmNjZjI5OWU4YzcyIiwiaWF0IjoxNzM5Nzk4MjUxLCJleHAiOjIwNTUxNTgyNTF9.Uxjvvd1xdlmAv7ili7V4gPtDpg01KYePcY37P7njoV4"}
        payload = json.dumps({"parkingTicketID": parkingTicketID, "requestType": "CONFIRM_TICKET", "employeeID": "5ec10c00-7eff-48c9-ada3-bce66129246d"})
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
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyVHlwZSI6IkVNUExPWUVFIiwiZ3JhbnRfdHlwZSI6ImF1dGhvcml6YXRpb24tdG9rZW4iLCJpc3MiOiJQYXJra2V5Iiwic3ViIjoiMWQyMzNhNzktOTcyYS00ZDA5LTk2MTktZDc0MTE5OGMwNDQwIiwianRpIjoiZjgzNTc4NmUtNWY3Ny00YzRiLThkNDMtMmNjZjI5OWU4YzcyIiwiaWF0IjoxNzM5Nzk4MjUxLCJleHAiOjIwNTUxNTgyNTF9.Uxjvvd1xdlmAv7ili7V4gPtDpg01KYePcY37P7njoV4"}
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
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyVHlwZSI6IkVNUExPWUVFIiwiZ3JhbnRfdHlwZSI6ImF1dGhvcml6YXRpb24tdG9rZW4iLCJpc3MiOiJQYXJra2V5Iiwic3ViIjoiMWQyMzNhNzktOTcyYS00ZDA5LTk2MTktZDc0MTE5OGMwNDQwIiwianRpIjoiZjgzNTc4NmUtNWY3Ny00YzRiLThkNDMtMmNjZjI5OWU4YzcyIiwiaWF0IjoxNzM5Nzk4MjUxLCJleHAiOjIwNTUxNTgyNTF9.Uxjvvd1xdlmAv7ili7V4gPtDpg01KYePcY37P7njoV4"}
        payload = json.dumps({"parkingTicketID": parkingTicketID, "employeeID": "5ec10c00-7eff-48c9-ada3-bce66129246d"})
        try:
            response = requests.post(BASE_URL + url, headers=headers, data=payload)
            response.raise_for_status()
            return self._get_json_response(response)
        except requests.exceptions.RequestException as e:
            print(f"Error exiting vehicle: {e}")
            return None
    
    def parkingCharges(self, parkingTicketID):
        url = "ticket-handler/get-parking-charges"
        headers = {'Content-Type': 'application/json', 'Authorization': "Bearer " + "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyVHlwZSI6IkVNUExPWUVFIiwiZ3JhbnRfdHlwZSI6ImF1dGhvcml6YXRpb24tdG9rZW4iLCJpc3MiOiJQYXJra2V5Iiwic3ViIjoiMWQyMzNhNzktOTcyYS00ZDA5LTk2MTktZDc0MTE5OGMwNDQwIiwianRpIjoiZjgzNTc4NmUtNWY3Ny00YzRiLThkNDMtMmNjZjI5OWU4YzcyIiwiaWF0IjoxNzM5Nzk4MjUxLCJleHAiOjIwNTUxNTgyNTF9.Uxjvvd1xdlmAv7ili7V4gPtDpg01KYePcY37P7njoV4"}
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