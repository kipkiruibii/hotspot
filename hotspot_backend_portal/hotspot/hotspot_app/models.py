from django.db import models
import uuid
from datetime import datetime
from django.utils import timezone


class PaymentHistory(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    phoneNumber = models.CharField(max_length=20, null=False)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    loginLink = models.TextField()
    macAddress = models.TextField(default="")
    ipAddress = models.TextField(default="")
    planType = models.TextField(default="")
    amount = models.IntegerField()
    devicesCount = models.IntegerField(default=1)
    expiry = models.DateTimeField(default=timezone.now)
    dateSubscribed = models.DateTimeField(default=timezone.now)
    CheckoutRequestID = models.TextField()
    ExternalReference = models.TextField(default="")
    MerchantRequestID = models.TextField()
    MpesaReceiptNumber = models.TextField(default="")
    ResultCode = models.FloatField(default=0)
    ResultDesc = models.TextField(null=True)
    Status = models.TextField(null=False)

    def __str__(self):
        return f"{self.phoneNumber} AMT: {self.amount}"


class HotspotUsers(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    mac_address = models.TextField()
    active = models.BooleanField(default=False)
    ip = models.TextField()
    user = models.TextField()
    plan = models.TextField(default="")
    dateSubscribed = models.DateTimeField(default=timezone.now)
    expectedExpiry = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.ip}, Active: {self.active} :Mac Address: {self.mac_address}"
