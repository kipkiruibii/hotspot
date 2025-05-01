from django.db import models
import uuid
from django.utils import timezone
import pytz


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

    class Meta:
        ordering = ["-dateSubscribed"]

    def __str__(self):
        nairobi_tz = pytz.timezone("Africa/Nairobi")
        local_dt = self.dateSubscribed.astimezone(nairobi_tz)
        formatted_date = local_dt.strftime("%d/%b/%Y %H:%M")
        return f"{self.phoneNumber}_____AMT: {self.amount}_____DATE: {formatted_date} ___{self.Status}"


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

    class Meta:
        ordering = ["-dateSubscribed"]

    def __str__(self):
        nairobi_tz = pytz.timezone("Africa/Nairobi")
        local_dt = self.dateSubscribed.astimezone(nairobi_tz)
        formatted_date = local_dt.strftime("%d/%b/%Y %H:%M")
        return f"{self.ip}_____Active: {self.active}_____Mac Address: {self.mac_address}_____Date: {formatted_date}"


class ErrorLogs(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    errorException = models.TextField()
    traceback = models.TextField()
    dateRecorded = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-dateRecorded"]

    def __str__(self):
        nairobi_tz = pytz.timezone("Africa/Nairobi")
        local_dt = self.dateRecorded.astimezone(nairobi_tz)
        formatted_date = local_dt.strftime("%d/%b/%Y %H:%M")
        return f"{self.errorException},_____on: {formatted_date}"
