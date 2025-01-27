import requests

url = "https://xkzd75f5kd.execute-api.ap-south-1.amazonaws.com/prod/customer-flow-handler/get-customer-vehicle-details?userID=7d2406b4-0e74-4d92-a27f-8bc11a81e1e9"

payload = {}
headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJncmFudF90eXBlIjoiYXV0aG9yaXphdGlvbi10b2tlbiIsInVzZXJUeXBlIjoiQ1VTVE9NRVIiLCJpc3MiOiJQYXJra2V5Iiwic3ViIjoiODM4MjAyNWQtOGU5OC00OTJlLWIyMTYtMmJlZGNkOTQwN2Y3IiwianRpIjoiNDcxNzIyMTItMzQzNC00MmE1LThiZDktODk5MmI4NTJhNTdkIiwiaWF0IjoxNzE1NDA5MzEwLCJleHAiOjIwMzA3NjkzMTB9.6c75Mjo-9JYbQPl4zStMT3FNLH2i2ssrwZCVB6quWr8'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

