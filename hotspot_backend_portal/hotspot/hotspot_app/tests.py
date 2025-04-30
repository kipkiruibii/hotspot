from django.test import TestCase

# Create your tests here.
import requests
import json

url = "https://warpspeed.site/payHeroCallback/"  
payload = {
    "response": {
        "Amount": 100,
        "CheckoutRequestID": "ws_CO_12345",
        "ExternalReference": "order_98765",
        "MerchantRequestID": "mr_45678",
        "MpesaReceiptNumber": "ABC123XYZ",
        "Phone": "254712345678",
        "ResultCode": 0,
        "ResultDesc": "The service request is processed successfully.",
        "Status": "Completed"
    }
}

headers = {
    "Content-Type": "application/json"
}

# response = requests.post(url, headers=headers, data=json.dumps(payload))

# print("Status Code:", response.status_code)
# assert response.status_code == 200
# print("Response:", response)


import requests
import json

# Endpoint URL
url = "https://warpspeed.site/initiate_pay"

# Dummy data simulating frontend input
payload = {
    "phone_number": "0740714002",
    "mac_address": "00:11:22:33:44:55",
    "amount": 10.0,
    "plan_type": "daily",
    "devices_count": 1,
    "ip_address": "192.168.88.5"
}

# Set headers
headers = {
    "Content-Type": "application/json"
}

# # Send POST request
# response = requests.post(url, data=json.dumps(payload), headers=headers)

# # Output response
# print("Status Code:", response.status_code)
# try:
#     print("Response JSON:", response.json())
# except Exception:
#     print("Raw Response:", response.text)

import requests

url = 'https://backend.payhero.co.ke/api/v2/whatspp/sendText'

headers = {
    'Content-Type': 'application/json',
    "Authorization": "Basic TkxUNkZBM2hFUmo2akgzbzhVTXk6QmtmT3A4SHVQM01LUWhjdmo4Q291SE1WQjlWME95ZmZ0VjV4UDYwMA==",
}

data = {
    "message": "My First Text",
    "phone_number": "0740714002",
    "session": "loginlinks"
}

response = requests.post(url, json=data, headers=headers)

print(response.text)
