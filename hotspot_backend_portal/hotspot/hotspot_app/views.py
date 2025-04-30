from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json
from .models import *
import requests
import uuid
from routeros_api import RouterOsApiPool
import traceback
from django.utils import timezone
from datetime import timedelta
import pytz


def homepage(request):
    return JsonResponse({"status": True})


def allow_hotspot_mac(mac_address: str, ip: str, plantype: str):
    try:
        connection = RouterOsApiPool(
            host="10.0.0.1",  # MikroTik's WireGuard IP
            username="api-user",
            password="@Dracula2025",
            port=8728,
            use_ssl=False,
            plaintext_login=True,
        )
        api = connection.get_api()

        bypass = api.get_resource("/ip/hotspot/ip-binding")

        # Check if already allowed
        existing = bypass.get(mac_address=mac_address)
        if not existing:
            bypass.add(
                mac_address=mac_address,
                type="bypassed",  # Or use 'regular' to still require login
                comment="M-Pesa payment",
            )
        # Schedule removal after e.g. 1 hour (60 minutes)

        exp_t = timezone.now() + timedelta(minutes=5)

        if plantype.lower() == "hourly":
            exp_t = timezone.now() + timedelta(hours=1)

        elif plantype.lower() == "daily":
            exp_t = timezone.now() + timedelta(days=1)

        elif plantype.lower() == "weekly":
            exp_t = timezone.now() + timedelta(days=7)

        elif plantype.lower() == "monthly":
            exp_t = timezone.now() + timedelta(days=30)

        toronto_tz = pytz.timezone("America/Toronto")
        exp_t = exp_t.astimezone(toronto_tz)

        scripts = api.get_resource("/system/script")

        # Remove existing script with the same name, if any
        existing_scripts = scripts.get(name=f"script-remove-{mac_address}")
        for script in existing_scripts:
            script_id = script.get(".id") or script.get("id")  # try both just in case
            if script_id:
                scripts.remove(id=script_id)
        scripts.add(
            name=f"script-remove-{mac_address}",
            source=f'/ip/hotspot/ip-binding/remove [find mac-address="{mac_address}"]',
            comment=f"Auto-generated removal script for {mac_address}",
        )

        scheduler = api.get_resource("/system/scheduler")
        # Remove existing scheduler with the same name, if it exists
        existing_schedulers = scheduler.get(name=f"remove-{mac_address}")
        for sched in existing_schedulers:
            sched_id = sched.get(".id") or sched.get("id")
            if sched_id:
                scheduler.remove(id=sched_id)
        scheduler.add(
            name=f"remove-{mac_address}",
            start_time=exp_t.strftime("%H:%M:%S"),
            start_date=exp_t.strftime("%Y-%m-%d"),
            on_event=f"script-remove-{mac_address}",
            comment="Auto-remove user after expiry",
        )
        # set the bandwidth
        queue = api.get_resource("/queue/simple")
        # Remove existing queue with the same name, if it exists
        existing_queues = queue.get(name=f"queue-{mac_address}")
        for q in existing_queues:
            q_id = q.get(".id") or q.get("id")
            if q_id:
                queue.remove(id=q_id)

        queue.add(
            name=f"queue-{mac_address}",
            target=f"{ip}/32",
            max_limit="8M/2M",  # 10 Mbps download / 5 Mbps upload
            comment=f"Limit for {mac_address}",
        )

        # save active to db
        hu = HotspotUsers(
            mac_address=mac_address, active=True, ip=ip, expectedExpiry=exp_t
        )
        hu.save()

        connection.disconnect()
    except Exception as e:
        el = ErrorLogs(errorException=f"{e}", traceback=f"{traceback.format_exc()}")
        el.save()


def sendWhatsappLoginLink(Phone_number, message):
    url = "https://backend.payhero.co.ke/api/v2/whatspp/sendText"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic TkxUNkZBM2hFUmo2akgzbzhVTXk6QmtmT3A4SHVQM01LUWhjdmo4Q291SE1WQjlWME95ZmZ0VjV4UDYwMA==",
    }

    data = {"message": message, "phone_number": Phone_number, "session": "loginlinks"}

    response = requests.post(url, json=data, headers=headers)

    print(response.text)


@csrf_exempt
def paymentSTK(request):
    if request.method == "POST":
        try:
            # ✅ Capture JSON data from frontend
            data = json.loads(request.body.decode("utf-8"))

            # ✅ Extract parameters sent from frontend
            mac_address = data.get("mac_address", "unknown-mac")
            phone_number = data.get("phone_number", None)
            amount = data.get("amount", 0)
            plan_type = data.get("plan_type", "default")
            devices_count = data.get("devices_count", 1)
            ip_address = data.get("ip_address", "0.0.0.0")

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
            el = ErrorLogs(
                errorException="Invalid JSON data",
                traceback=f"{traceback.format_exc()}",
            )
            el.save()
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            el = ErrorLogs(errorException=f"{e}", traceback=f"{traceback.format_exc()}")
            el.save()

        return JsonResponse({"sucecss": "true"}, status=200)
    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def payHeroCallback(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))

        response_data = data.get("response", {})

        try:

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
                    ph.save()

                    if status.lower() == "success":
                        allow_hotspot_mac(
                            mac_address=ph.macAddress,
                            ip=ph.ipAddress,
                            plantype=ph.planType,
                        )
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
        except Exception as e:
            el = ErrorLogs(errorException=f"{e}", traceback=f"{traceback.format_exc()}")
            el.save()

    return JsonResponse({"Result": "Failed"})


def paymentConfirmation(request):
    pass


def serviceWalletBalance(request):
    pass


def serviceWalletTopUp(request):
    pass


def walletBalance(request):
    pass
