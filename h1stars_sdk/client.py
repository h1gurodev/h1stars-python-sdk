"""
H1Stars Payment Gateway Client
"""

import hmac
import hashlib
import aiohttp
import asyncio
from typing import Dict, Optional, List
from datetime import datetime

from .exceptions import (
    H1StarsAPIError,
    H1StarsAuthError,
    H1StarsValidationError,
    H1StarsNotFoundError,
    H1StarsRateLimitError,
    H1StarsServerError
)


class H1StarsClient:
    """H1Stars Payment Gateway Async Client"""

    def __init__(self, api_key: str, base_url: str = "https://pay.h1stars.ru/api"):
        """
        Initialize H1Stars client

        Args:
            api_key: Your API key from H1Stars dashboard
            base_url: API base URL (default: https://pay.h1stars.ru/api)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'H1Stars-Python-SDK/1.0.0'
        }
        self._session = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def _create_session(self):
        """Create aiohttp session"""
        if self._session is None:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self._session = aiohttp.ClientSession(
                headers=self.headers,
                connector=connector,
                timeout=timeout
            )

    async def close(self):
        """Close aiohttp session"""
        if self._session:
            await self._session.close()
            self._session = None

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make HTTP request to API"""
        if self._session is None:
            await self._create_session()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            async with self._session.request(method, url, json=data, params=params) as response:
                response_data = await response.json()

                if response.status == 400:
                    raise H1StarsValidationError("Invalid request parameters", response.status, response_data)
                elif response.status == 401:
                    raise H1StarsAuthError("Invalid or missing API key", response.status, response_data)
                elif response.status == 403:
                    raise H1StarsAuthError("Access denied", response.status, response_data)
                elif response.status == 404:
                    raise H1StarsNotFoundError("Resource not found", response.status, response_data)
                elif response.status == 429:
                    raise H1StarsRateLimitError("Rate limit exceeded", response.status, response_data)
                elif response.status >= 500:
                    raise H1StarsServerError("Internal server error", response.status, response_data)
                elif not response.ok:
                    raise H1StarsAPIError(f"HTTP {response.status}", response.status, response_data)

                return response_data

        except aiohttp.ClientError as e:
            raise H1StarsAPIError(f"Request failed: {str(e)}")
        except Exception as e:
            raise H1StarsAPIError(f"Unexpected error: {str(e)}")

    async def create_payment(
        self,
        amount: float,
        description: str,
        user_id: str,
        callback_url: Optional[str] = None,
        return_url: Optional[str] = None
    ) -> Dict:
        """
        Create a new payment

        Args:
            amount: Payment amount in rubles
            description: Payment description
            user_id: User identifier
            callback_url: Webhook URL for payment notifications
            return_url: URL to redirect user after payment

        Returns:
            Dict with payment information including payment_id and payment_url
        """
        data = {
            'amount': amount,
            'description': description,
            'user_id': user_id
        }

        if callback_url:
            data['callback_url'] = callback_url
        if return_url:
            data['return_url'] = return_url

        return await self._make_request('POST', '/create-payment', data)

    async def get_payment(self, payment_id: str) -> Dict:
        """
        Get payment information by ID

        Args:
            payment_id: Payment ID

        Returns:
            Dict with payment information
        """
        return await self._make_request('GET', f'/payment/{payment_id}')

    async def get_partner_balance(self) -> Dict:
        """
        Get partner account balance

        Returns:
            Dict with balance information
        """
        return await self._make_request('GET', '/partner/balance')

    async def create_withdrawal(
        self,
        amount: float,
        payment_method: str,
        card_number: Optional[str] = None,
        cardholder_name: Optional[str] = None
    ) -> Dict:
        """
        Create withdrawal request

        Args:
            amount: Amount to withdraw
            payment_method: Payment method (e.g., 'card')
            card_number: Card number (for card withdrawals)
            cardholder_name: Cardholder name (for card withdrawals)

        Returns:
            Dict with withdrawal information
        """
        data = {
            'amount': amount,
            'payment_method': payment_method
        }

        if card_number:
            data['card_number'] = card_number
        if cardholder_name:
            data['cardholder_name'] = cardholder_name

        return await self._make_request('POST', '/partner/withdraw', data)

    async def get_partner_transactions(
        self,
        limit: int = 50,
        offset: int = 0,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict:
        """
        Get partner transaction history

        Args:
            limit: Number of records to return (default: 50)
            offset: Offset for pagination (default: 0)
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)

        Returns:
            Dict with transaction history
        """
        params = {
            'limit': limit,
            'offset': offset
        }

        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to

        return await self._make_request('GET', '/partner/transactions', params=params)

    @staticmethod
    def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
        """
        Verify webhook signature

        Args:
            payload: Raw webhook payload (JSON string)
            signature: Signature from X-Signature header
            secret: Your webhook secret

        Returns:
            bool: True if signature is valid
        """
        expected = 'sha256=' + hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected)