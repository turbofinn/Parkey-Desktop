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
        headers = {'Authorization': "Bearer "+ "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyVHlwZSI6IkVNUExPWUVFIiwiZ3JhbnRfdHlwZSI6ImF1dGhvcml6YXRpb24tdG9rZW4iLCJpc3MiOiJQYXJra2V5Iiwic3ViIjoiMWQyMzNhNzktOTcyYS00ZDA5LTk2MTktZDc0MTE5OGMwNDQwIiwianRpIjoiYTNmM2NlMTctOTBmOC00MGQ0LThjNmYtMThmNmQ2YTYxNjE1IiwiaWF0IjoxNzM4NzY1MDU4LCJleHAiOjIwNTQxMjUwNTh9.-FRQKl9nWfTMLlkh6mrJ3QVY5R60kZ_CzWThW-gU4mM"}
        print(headers)
        response = requests.get(BASE_URL + url, headers=headers)
        print(response.text)
        response_data = response.json()
        return response_data

    def getCreateCustomer(self, mobileNo, vehicleNo):
        # URL of the API endpoint
        url = "customer-flow-handler/create-customer"
        source = "EMPLOYEE_DESKTOP"
        empID = "5ec10c00-7eff-48c9-ada3-bce66129246d"
        headers = { "Content-Type": "application/json","Authorization": "Bearer "+ "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJncmFudF90eXBlIjoiYXV0aG9yaXphdGlvbi10b2tlbiIsInVzZXJUeXBlIjoiRU1QTE9ZRUUiLCJpc3MiOiJQYXJra2V5Iiwic3ViIjoiMWQyMzNhNzktOTcyYS00ZDA5LTk2MTktZDc0MTE5OGMwNDQwIiwianRpIjoiZjA3M2Y2OTQtYTFiMi00ZWQ0LTlkZjAtYWY1YTBlM2FlNzgwIiwiaWF0IjoxNzM4ODI4Nzk4LCJleHAiOjIwNTQxODg3OTh9.C9soV7f1VnjS9c1nFXusNoVT-rbDTu4HDB9KcllAC08"}  
        payload = json.dumps({"source": source,"mobileNo": mobileNo,"vehicleNo": vehicleNo, "employeeID": empID})
        print("payload is this " + payload)
        response = requests.post(BASE_URL + url, headers=headers, data=payload)
        print(response.text)
        response_data = response.json()
        return response_data



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