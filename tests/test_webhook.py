import pytest
import json
from h1stars_sdk import H1StarsClient


class TestWebhookSignature:

    def test_verify_webhook_signature_valid(self):
        payload = '{"event": "payment.completed", "payment_id": "pay_123"}'
        secret = "my_secret"

        # Генерируем правильную подпись
        import hmac
        import hashlib

        expected_signature = 'sha256=' + hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Проверяем
        is_valid = H1StarsClient.verify_webhook_signature(
            payload, expected_signature, secret
        )

        assert is_valid

    def test_verify_webhook_signature_invalid(self):
        payload = '{"event": "payment.completed", "payment_id": "pay_123"}'
        secret = "my_secret"
        wrong_signature = "sha256=wrong_hash"

        is_valid = H1StarsClient.verify_webhook_signature(
            payload, wrong_signature, secret
        )

        assert not is_valid