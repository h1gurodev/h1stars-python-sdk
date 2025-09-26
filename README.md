# H1Stars Payment Gateway Python SDK

Официальный **асинхронный** Python SDK для интеграции с платежным шлюзом H1Stars.

⚡ **Полностью асинхронный** - максимальная производительность
🚀 **Простая интеграция** - всего 5 минут до первого платежа
🔒 **Безопасный** - проверка webhook подписей, защищенные соединения
📱 **Современный** - Python 3.8+, aiohttp, type hints

## 🚀 Быстрая установка

```bash
pip install h1stars-payment-sdk

# Для примеров с FastAPI
pip install h1stars-payment-sdk[examples]
```

## 📖 Использование

### Инициализация клиента

```python
import asyncio
from h1stars_sdk import H1StarsClient

# Используйте async context manager для автоматического управления сессией
async with H1StarsClient(api_key="your_api_key_here") as client:
    # Ваш код здесь
    pass
```

### Создание платежа

```python
async def create_payment_example():
    async with H1StarsClient(api_key="your_api_key_here") as client:
        try:
            payment = await client.create_payment(
                amount=100.50,
                description="Покупка звезд в игре",
                user_id="user123",
                callback_url="https://yoursite.com/webhook",
                return_url="https://yoursite.com/success"
            )

            print(f"Payment ID: {payment['payment_id']}")
            print(f"Payment URL: {payment['payment_url']}")

            # Отправьте пользователя на payment_url для оплаты

        except Exception as e:
            print(f"Ошибка создания платежа: {e}")

# Запуск
asyncio.run(create_payment_example())
```

### Параллельные платежи

```python
async def multiple_payments():
    async with H1StarsClient(api_key="your_api_key_here") as client:
        # Создаем несколько платежей параллельно
        tasks = [
            client.create_payment(
                amount=100.0 + i * 10,
                description=f"Платеж #{i+1}",
                user_id=f"user_{i+1}"
            )
            for i in range(5)
        ]

        payments = await asyncio.gather(*tasks)
        print(f"Создано {len(payments)} платежей за раз!")
```

### Проверка статуса платежа

```python
async def check_payment_status():
    async with H1StarsClient(api_key="your_api_key_here") as client:
        try:
            payment_status = await client.get_payment("pay_1234567890")
            print(f"Статус: {payment_status['status']}")

            if payment_status['status'] == 'completed':
                print("Платеж успешно оплачен!")

        except Exception as e:
            print(f"Ошибка получения статуса: {e}")
```

### FastAPI Webhook Handler

```python
from fastapi import FastAPI, Request, HTTPException
from h1stars_sdk import H1StarsClient
import json

app = FastAPI()

@app.post("/webhook")
async def handle_webhook(request: Request):
    # Получаем данные webhook
    payload = await request.body()
    payload_str = payload.decode('utf-8')
    signature = request.headers.get('X-Signature')

    # Проверяем подпись
    if H1StarsClient.verify_webhook_signature(payload_str, signature, "your_webhook_secret"):
        webhook_data = json.loads(payload_str)

        if webhook_data['event'] == 'payment.completed':
            payment_id = webhook_data['payment_id']
            print(f"Платеж {payment_id} успешно оплачен!")

            # Ваша асинхронная логика обработки
            await process_successful_payment(webhook_data)

        return {"status": "ok"}
    else:
        raise HTTPException(status_code=400, detail="Invalid signature")

async def process_successful_payment(webhook_data):
    # Ваша логика обработки платежа
    pass
```

### Работа с партнерским API

```python
async def partner_api_example():
    async with H1StarsClient(api_key="your_api_key_here") as client:
        # Параллельное получение данных
        balance_task = client.get_partner_balance()
        transactions_task = client.get_partner_transactions(limit=10)

        balance, transactions = await asyncio.gather(
            balance_task,
            transactions_task
        )

        print(f"Доступно для вывода: {balance['available_for_withdrawal']} RUB")
        print(f"Транзакций: {len(transactions.get('transactions', []))}")

        # Создание заявки на вывод
        if balance['available_for_withdrawal'] >= 1000:
            withdrawal = await client.create_withdrawal(
                amount=1000.00,
                payment_method="card",
                card_number="4111111111111111",
                cardholder_name="IVAN PETROV"
            )
            print(f"Заявка на вывод создана: {withdrawal.get('status')}")
```

## 🔧 Обработка ошибок

```python
from h1stars_sdk import (
    H1StarsAuthError,
    H1StarsValidationError,
    H1StarsNotFoundError,
    H1StarsRateLimitError,
    H1StarsServerError
)

try:
    payment = client.create_payment(
        amount=100.50,
        description="Test payment",
        user_id="user123"
    )
except H1StarsAuthError:
    print("Неверный API ключ")
except H1StarsValidationError:
    print("Некорректные параметры запроса")
except H1StarsRateLimitError:
    print("Превышен лимит запросов")
except H1StarsServerError:
    print("Ошибка сервера")
```

## 📋 Статусы платежей

- `pending` - Ожидает оплаты
- `completed` - Успешно оплачен
- `expired` - Истек срок оплаты (15 минут)
- `inactive` - Деактивирован

## 🔐 Безопасность

- Всегда проверяйте подписи webhook уведомлений
- Используйте HTTPS для всех callback URL
- Не передавайте API ключи в клиентском коде
- Храните webhook секреты в безопасном месте

## 📞 Поддержка

- Документация API: https://pay.h1stars.ru/docs
- Email: support@h1stars.ru
- Telegram: @h1stars_support

## 📄 Лицензия

MIT License