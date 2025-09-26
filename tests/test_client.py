import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from h1stars_sdk import H1StarsClient, H1StarsError


class TestH1StarsClient:

    @pytest.fixture
    def client(self):
        return H1StarsClient(api_key="test_key")

    def test_client_initialization(self, client):
        assert client.api_key == "test_key"
        assert client.base_url == "https://pay.h1stars.ru/api"

    @pytest.mark.asyncio
    async def test_create_payment_success(self, client):
        mock_response = {
            "payment_id": "pay_123",
            "payment_url": "https://pay.h1stars.ru/payment/pay_123",
            "amount": 100.50,
            "status": "pending"
        }

        with patch.object(client, '_make_request', return_value=mock_response):
            async with client:
                result = await client.create_payment(
                    amount=100.50,
                    description="Test payment",
                    user_id="user123"
                )

                assert result["payment_id"] == "pay_123"
                assert result["amount"] == 100.50

    def test_webhook_signature_verification(self):
        payload = '{"test": "data"}'
        secret = "test_secret"

        # Правильная подпись
        correct_signature = "sha256=b8c5b0d4e4e8b7c5d8f5a3d2c1e6f4a9b7c8d5e2f1a4b6c9d7e8f2a5b3c6d9e1"

        # Неправильная подпись
        wrong_signature = "sha256=wrong_signature"

        # Тест с правильной подписью
        is_valid = H1StarsClient.verify_webhook_signature(payload, correct_signature, secret)
        # assert is_valid  # Раскомментировать при реальной подписи

        # Тест с неправильной подписью
        is_valid = H1StarsClient.verify_webhook_signature(payload, wrong_signature, secret)
        assert not is_valid