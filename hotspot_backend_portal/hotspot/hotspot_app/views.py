from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json
from .models import *
import requests
import uuid
from routeros_api import RouterOsApiPool


def homepage(request):
    return JsonResponse({"status": True})


def allow_hotspot_mac(mac_address: str, ip: str):
    hu = HotspotUsers(mac_address="step 2 success")
    hu.save()
    try:
        connection = RouterOsApiPool(
            host="10.10.0.1",  # MikroTik's WireGuard IP
            username="admin",
            password="BS9NHVYKV3",
            port=8728,
            use_ssl=False,
        )
        api = connection.get_api()

        hu = HotspotUsers(mac_address="step 3 success")
        hu.save()
        bypass = api.get_resource("/ip/hotspot/ip-binding")

        # Check if already allowed
        existing = bypass.get(mac_address=mac_address)
        if not existing:
            bypass.add(
                mac_address=mac_address,
                type="bypassed",  # Or use 'regular' to still require login
                comment="Auto-added after M-Pesa payment",
            )

        hu = HotspotUsers(mac_address="step 4 success")
        hu.save()
        # save active to db
        hu = HotspotUsers(mac_address=mac_address, active=True, ip=ip)
        hu.save()

        connection.disconnect()
    except Exception as e:
        hu = HotspotUsers(mac_address=f"failed {e}")
        hu.save()


@csrf_exempt
def paymentSTK(request):
    if request.method == "POST":
        try:
            hu = HotspotUsers(mac_address=f"Data: {data}")
            hu.save()

            # ✅ Capture JSON data from frontend
            data = json.loads(request.body.decode("utf-8"))

            hu = HotspotUsers(mac_address=f"Data: {data}")
            hu.save()

            # ✅ Extract parameters sent from frontend
            mac_address = data.get("mac_address", "unknown-mac")
            phone_number = data.get("phone_number", None)
            amount = data.get("amount", 0)
            plan_type = data.get("plan_type", "default")
            devices_count = data.get("devices_count", 1)
            ip_address = data.get("ip_address", "0.0.0.0")

            hu = HotspotUsers(mac_address=f"Data: {data}")
            hu.save()

            if not phone_number:
                return JsonResponse({"error": "Phone number is required"}, status=400)

            # ✅ Generate a unique external reference
            external_reference = f"INV-{uuid.uuid4().hex[:8].upper()}"

            # ✅ Prepare the request payload for PayHero API
            url = "https://backend.payhero.co.ke/api/v2/payments"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Basic TkxUNkZBM2hFUmo2akgzbzhVTXk6QmtmT3A4SHVQM01LUWhjdmo4Q291SE1WQjlWME95ZmZ0VjV4UDYwMA==",
            }

            payload = {
                "amount": amount,
                "phone_number": phone_number,
                "channel_id": 647,
                "provider": "m-pesa",
                "external_reference": external_reference,
                "customer_name": mac_address,
                "callback_url": "https://warpspeed.site/payHeroCallback/",
            }

            # ✅ Send the payment request to PayHero API
            response = requests.post(url, headers=headers, json=payload)
            res_data = response.json()

            hu = HotspotUsers(mac_address=f"RESPONSE: {res_data}")
            hu.save()

            # ✅ Extract response values
            checkout_ref = res_data.get("CheckoutRequestID", None)
            status = res_data.get("status", "unknown")
            # is_successful = res_data.get("success", False)

            # ✅ Save successful payment to the database
            ph = PaymentHistory(
                CheckoutRequestID=checkout_ref,
                ExternalReference=external_reference,
                macAddress=mac_address,
                Status=status,
                amount=amount,
                phoneNumber=phone_number,
                planType=plan_type,
                devicesCount=devices_count,
                ipAddress=ip_address,
            )
            ph.save()

            return JsonResponse(res_data, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            hu = HotspotUsers(mac_address=f"step 0 FAILED {e}")
            hu.save()

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def payHeroCallback(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        response_data = data.get("response", {})
        if response_data:
            amount = response_data.get("Amount", 0)
            checkout_request_id = response_data.get("CheckoutRequestID", "k")
            external_reference = response_data.get("ExternalReference", "k")
            merchant_request_id = response_data.get("MerchantRequestID", "k")
            mpesa_receipt_number = response_data.get("MpesaReceiptNumber", "k")
            phone = response_data.get("Phone", "k")
            result_code = response_data.get("ResultCode", -1)
            result_desc = response_data.get("ResultDesc", "k")
            status = response_data.get("Status", "k")
            ph = PaymentHistory.objects.filter(
                CheckoutRequestID=checkout_request_id
            ).first()
            if ph:
                ph.Status = status
                ph.MerchantRequestID = merchant_request_id
                ph.MpesaReceiptNumber = mpesa_receipt_number
                ph.ResultCode = result_code
                ph.ResultDesc = result_desc

                hu = HotspotUsers(
                    mac_address=f"step 0 success {status} { status == "Success"}"
                )
                hu.save()

                if status == "Success":
                    # grant access to the mac in microtik for the given time
                    # check number of devices
                    hu = HotspotUsers(mac_address="step 1 success")
                    hu.save()
                    allow_hotspot_mac(mac_address=ph.macAddress, ip=ph.ipAddress)
                ph.save()
            else:
                ts = PaymentHistory(
                    amount=amount,
                    CheckoutRequestID=checkout_request_id,
                    ExternalReference=external_reference,
                    MerchantRequestID=merchant_request_id,
                    MpesaReceiptNumber=mpesa_receipt_number,
                    phoneNumber=phone,
                    ResultCode=result_code,
                    ResultDesc=result_desc,
                    Status=status,
                )
                ts.save()

            # check status if successful handle authentication:
            # add the request to

            return JsonResponse({"Result": "Callback Success"})

    return JsonResponse({"Result": "Failed"})


def paymentConfirmation(request):
    pass


def serviceWalletBalance(request):
    pass


def serviceWalletTopUp(request):
    pass


def walletBalance(request):
    pass
