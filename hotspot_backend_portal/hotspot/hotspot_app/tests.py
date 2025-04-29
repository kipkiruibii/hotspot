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

response = requests.post(url, headers=headers, data=json.dumps(payload))

print("Status Code:", response.status_code)
assert response.status_code == 200
print("Response:", response)
