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
        headers = {'Authorization': "Bearer "+ "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJncmFudF90eXBlIjoiYXV0aG9yaXphdGlvbi10b2tlbiIsInVzZXJUeXBlIjoiRU1QTE9ZRUUiLCJpc3MiOiJQYXJra2V5Iiwic3ViIjoiMWQyMzNhNzktOTcyYS00ZDA5LTk2MTktZDc0MTE5OGMwNDQwIiwianRpIjoiZjIyYmZmOWQtM2QzZC00NTJhLWE4NjAtMDIzOTJmNWE0MDk3IiwiaWF0IjoxNzM4NDkxNzU2LCJleHAiOjIwNTM4NTE3NTZ9.pO8OMjGt0S54gjwm9wGdyoEfU6ggXmuoNoj_qpyHIyA"}
        print(headers)
        response = requests.get(BASE_URL + url, headers=headers)
        print(response.text)
        response_data = response.json()
        return response_data


    def getCreateCustomer(self,mobileNo,vehicleNo):
        url = "customer-flow-handler/create-customer"
        source = "EMPLOYEE_DESKTOP"
        headers = { "Content-Type": "application/json","Authorization": "Bearer "+ "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyVHlwZSI6IkVNUExPWUVFIiwiZ3JhbnRfdHlwZSI6ImF1dGhvcml6YXRpb24tdG9rZW4iLCJpc3MiOiJQYXJra2V5Iiwic3ViIjoiMWQyMzNhNzktOTcyYS00ZDA5LTk2MTktZDc0MTE5OGMwNDQwIiwianRpIjoiMDM1ZGY0YmQtOTA5YS00MzFlLWI3ZjktODAxN2M2OGFjNDkzIiwiaWF0IjoxNzM4NTk1MTIxLCJleHAiOjIwNTM5NTUxMjF9.SQTURGQugO0j1KJLrDAhbsIJ7jayHhupcdKCK01YRAs"}
       
        payload = json.dumps({"source": source,"mobileNo": mobileNo,"vehicleNo": vehicleNo, "employeeID": "3bd3824c-0dca-4b92-9e60-d42c990c7853"})
        print("payload is this " + payload)
        response = requests.post(BASE_URL + url, headers=headers, data=payload)
        print(response.text)
        response_data = response.json()
        return response_data

    

    # def getCreateCustomer(self, mobileNo, vehicleNo):
        # URL of the API endpoint
        url = "customer-flow-handler/create-customer"
        employeeID = ""
        # Headers - adding Authorization with Bearer token
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer "  # Correct Bearer token format
        }
        
        # Payload - unchanged
        payload = json.dumps({
            "source": "EMPLOYEE_DESKTOP",
            "mobileNo": mobileNo,
            "vehicleNo": vehicleNo,
            "employeeID": employeeID
        })

        # Debugging - Print headers and payload
        print("Headers:", headers)
        print("Payload:", payload)
        
        # Making the POST request to the API endpoint
        response = requests.post(BASE_URL + url, headers=headers, data=payload)

        # Debugging - Print response status and content
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)
        
        # Parse and return the response JSON, handling errors
        try:
            response_data = response.json()
        except ValueError:
            response_data = {"error": "Failed to parse JSON response"}
        
        return response_data


env_config = EnvConfig()

def main():
    api = ApiService()
    # mobileNo = input("Input Mobile: ")
    # mobileNo = "7985157933"
    
    # url = "login-service/send-otp"
    # payload = json.dumps({"mobileNo": mobileNo})
    # print(api.sendOtp(url, payload))

    # otp = input("Input OTP: ")

    # url = "login-service/verify-otp/employee"
    # payload = json.dumps({"mobileNo": mobileNo, "otp": otp})
    # print(api.verifyOtp(url, payload))


    # # vehicleNo = input("Input OTP: ")
    # vehicleNo = "UP32TY5645"
   
    print(api.getCreateCustomer("8585588585", "UP32TY5645"))

if __name__ == "__main__":
    main()

#7985157933
#UP32TY5645