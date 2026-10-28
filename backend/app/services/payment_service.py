"""Payment-session creation and webhook verification.

The service deliberately separates *starting* a checkout from *settling* it.
Only a verified provider webhook can move a live booking out of PENDING.  The
explicit local sandbox exists for demos/tests and labels its result as such.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlencode

import requests


class PaymentService:
    def is_sandbox(self) -> bool:
        return os.getenv("PAYMENT_SANDBOX", "true").strip().lower() == "true"

    def start_checkout(
        self,
        bookings: Iterable[Any],
        payment_method: str,
        return_url: Optional[str],
    ) -> Dict[str, Any]:
        booking_list = list(bookings)
        amount = round(sum(float(booking.price) for booking in booking_list), 2)
        method = payment_method.upper()
        transaction_id = f"TXN-{method}-{uuid.uuid4().hex[:10].upper()}"
        booking_ids = [booking.id for booking in booking_list]

        if method == "STRIPE" and os.getenv("STRIPE_SECRET_KEY"):
            session = self._create_stripe_session(booking_list, transaction_id, return_url)
            if session:
                return {
                    "mode": "live",
                    "provider": "STRIPE",
                    "transaction_id": transaction_id,
                    "checkout_url": session["url"],
                    "provider_session_id": session["id"],
                    "amount": amount,
                    "booking_ids": booking_ids,
                }
        if method == "VNPAY" and os.getenv("VNPAY_TMN_CODE") and os.getenv("VNPAY_HASH_SECRET"):
            return self._create_vnpay_url(amount, transaction_id, booking_ids, return_url)
        if method == "MOMO" and os.getenv("MOMO_PARTNER_CODE") and os.getenv("MOMO_SECRET_KEY"):
            result = self._create_momo_payment(amount, transaction_id, booking_ids, return_url)
            if result:
                return result

        if self.is_sandbox():
            return {
                "mode": "sandbox",
                "provider": method,
                "transaction_id": transaction_id,
                "amount": amount,
                "booking_ids": booking_ids,
                "voucher_code": f"VOUCHER-{uuid.uuid4().hex[:10].upper()}",
            }
        raise ValueError(f"{method} is not configured. Add its server-side credentials or enable PAYMENT_SANDBOX for development.")

    def _create_stripe_session(self, bookings: List[Any], transaction_id: str, return_url: Optional[str]) -> Optional[Dict[str, str]]:
        success_url = return_url or os.getenv("STRIPE_SUCCESS_URL", "http://localhost:3000/payment/success")
        cancel_url = os.getenv("STRIPE_CANCEL_URL", success_url)
        data: Dict[str, str] = {
            "mode": "payment",
            "success_url": f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": cancel_url,
            "metadata[transaction_id]": transaction_id,
            "metadata[booking_ids]": ",".join(str(booking.id) for booking in bookings),
        }
        for index, booking in enumerate(bookings):
            prefix = f"line_items[{index}]"
            data[f"{prefix}[price_data][currency]"] = "vnd"
            data[f"{prefix}[price_data][product_data][name]"] = booking.service_name[:120]
            data[f"{prefix}[price_data][unit_amount]"] = str(max(1, int(round(float(booking.price)))))
            data[f"{prefix}[quantity]"] = "1"
        try:
            response = requests.post(
                "https://api.stripe.com/v1/checkout/sessions",
                auth=(os.environ["STRIPE_SECRET_KEY"], ""),
                data=data,
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json()
            return {"id": payload["id"], "url": payload["url"]}
        except Exception:
            return None

    def _create_vnpay_url(self, amount: float, transaction_id: str, booking_ids: List[int], return_url: Optional[str]) -> Dict[str, Any]:
        params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": os.environ["VNPAY_TMN_CODE"],
            "vnp_Amount": str(int(round(amount * 100))),
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": transaction_id,
            "vnp_OrderInfo": f"Travel bookings {','.join(map(str, booking_ids))}",
            "vnp_OrderType": "other",
            "vnp_Locale": "vn",
            "vnp_ReturnUrl": return_url or os.getenv("VNPAY_RETURN_URL", "http://localhost:3000/payment/vnpay-return"),
            "vnp_IpAddr": "127.0.0.1",
            "vnp_CreateDate": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        }
        signing_data = urlencode(sorted(params.items()))
        signature = hmac.new(
            os.environ["VNPAY_HASH_SECRET"].encode(), signing_data.encode(), hashlib.sha512
        ).hexdigest()
        gateway = os.getenv("VNPAY_PAYMENT_URL", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
        return {
            "mode": "live",
            "provider": "VNPAY",
            "transaction_id": transaction_id,
            "checkout_url": f"{gateway}?{signing_data}&vnp_SecureHash={signature}",
            "amount": amount,
            "booking_ids": booking_ids,
        }

    def _create_momo_payment(self, amount: float, transaction_id: str, booking_ids: List[int], return_url: Optional[str]) -> Optional[Dict[str, Any]]:
        partner = os.environ["MOMO_PARTNER_CODE"]
        access_key = os.getenv("MOMO_ACCESS_KEY", "")
        request_id = str(uuid.uuid4())
        endpoint = os.getenv("MOMO_ENDPOINT", "https://test-payment.momo.vn/v2/gateway/api/create")
        redirect_url = return_url or os.getenv("MOMO_RETURN_URL", "http://localhost:3000/payment/momo-return")
        notify_url = os.getenv("MOMO_NOTIFY_URL", redirect_url)
        raw_signature = (
            f"accessKey={access_key}&amount={int(amount)}&extraData=&ipnUrl={notify_url}&orderId={transaction_id}"
            f"&orderInfo=Travel bookings&partnerCode={partner}&redirectUrl={redirect_url}&requestId={request_id}&requestType=captureWallet"
        )
        signature = hmac.new(os.environ["MOMO_SECRET_KEY"].encode(), raw_signature.encode(), hashlib.sha256).hexdigest()
        payload = {
            "partnerCode": partner, "partnerName": "AI Travel Agent", "storeId": "travel-agent",
            "requestId": request_id, "amount": str(int(amount)), "orderId": transaction_id,
            "orderInfo": "Travel bookings", "redirectUrl": redirect_url, "ipnUrl": notify_url,
            "lang": "vi", "requestType": "captureWallet", "autoCapture": True, "extraData": "", "signature": signature,
        }
        try:
            response = requests.post(endpoint, json=payload, timeout=15)
            response.raise_for_status()
            result = response.json()
            if result.get("payUrl"):
                return {"mode": "live", "provider": "MOMO", "transaction_id": transaction_id, "checkout_url": result["payUrl"], "amount": amount, "booking_ids": booking_ids}
        except Exception:
            return None
        return None

    def verify_stripe_signature(self, body: bytes, signature: str) -> bool:
        secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        if not secret or not signature:
            return False
        values = dict(part.split("=", 1) for part in signature.split(",") if "=" in part)
        timestamp = values.get("t")
        received = values.get("v1")
        if not timestamp or not received:
            return False
        expected = hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, received)


payment_service = PaymentService()
