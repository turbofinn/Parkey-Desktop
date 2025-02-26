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

    def getVehicleDetails(self, url):
        headers = {'Authorization': "Bearer "+ env_config.get_token()}
        print(headers)
        response = requests.get(BASE_URL + url, headers=headers)
        print(response.text)
        return response.text


env_config = EnvConfig()

def main():
    api = ApiService()
    # mobileNo = input("Input Mobile: ")
    mobileNo = "7985157933"
    
    url = "login-service/send-otp"
    payload = json.dumps({"mobileNo": mobileNo})
    print(api.sendOtp(url, payload))

    otp = input("Input OTP: ")

    url = "login-service/verify-otp/employee"
    payload = json.dumps({"mobileNo": mobileNo, "otp": otp})
    print(api.verifyOtp(url, payload))


    # vehicleNo = input("Input OTP: ")
    vehicleNo = "UP32TY5645"
    url = "customer-flow-handler/get-vehicle-details?vehicleNo="+vehicleNo
    print(api.getVehicleDetails(url))

if __name__ == "__main__":
    main()

#7985157933
#UP32TY5645