"""
Пример обработки webhook уведомлений от H1Stars (FastAPI + async)
"""

import asyncio
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from h1stars_sdk import H1StarsClient
import uvicorn

app = FastAPI(title="H1Stars Webhook Handler")

# Ваш секретный ключ для проверки webhook подписей
WEBHOOK_SECRET = "your_webhook_secret_here"


@app.post("/webhook")
async def handle_webhook(request: Request):
    """Асинхронный обработчик webhook уведомлений от H1Stars"""

    try:
        # Получаем данные запроса
        payload = await request.body()
        payload_str = payload.decode('utf-8')
        signature = request.headers.get('X-Signature', '')

        # Проверяем подпись webhook
        if not H1StarsClient.verify_webhook_signature(payload_str, signature, WEBHOOK_SECRET):
            print("❌ Неверная подпись webhook!")
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Парсим данные webhook
        webhook_data = json.loads(payload_str)

        print(f"📨 Получен webhook: {webhook_data['event']}")
        print(f"Payment ID: {webhook_data['payment_id']}")

        # Обрабатываем различные типы событий асинхронно
        if webhook_data['event'] == 'payment.completed':
            await handle_payment_completed(webhook_data)

        elif webhook_data['event'] == 'payment.expired':
            await handle_payment_expired(webhook_data)

        else:
            print(f"⚠️  Неизвестный тип события: {webhook_data['event']}")

        return JSONResponse({"status": "ok"})

    except json.JSONDecodeError:
        print("❌ Некорректный JSON в webhook")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    except Exception as e:
        print(f"❌ Ошибка обработки webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


async def handle_payment_completed(webhook_data):
    """Асинхронная обработка успешной оплаты"""

    payment_id = webhook_data['payment_id']
    amount = webhook_data['amount']
    user_id = webhook_data['user_id']

    print(f"💰 Платеж {payment_id} успешно оплачен!")
    print(f"Сумма: {amount} RUB")
    print(f"Пользователь: {user_id}")

    # Здесь ваша асинхронная логика:
    # - Асинхронно обновить статус заказа в базе данных
    # - Выдать пользователю товар/услугу
    # - Отправить уведомление пользователю
    # - Записать в лог

    # Пример с асинхронной базой данных:
    # async with get_db_session() as db:
    #     order = await db.get(Order, payment_id=payment_id)
    #     order.status = 'paid'
    #     await db.commit()
    #
    #     user = await db.get(User, id=user_id)
    #     user.balance += amount
    #     await db.commit()

    # Пример асинхронного уведомления
    # await send_notification(user_id, f"Платеж на {amount} RUB успешно обработан")


async def handle_payment_expired(webhook_data):
    """Асинхронная обработка истекшего платежа"""

    payment_id = webhook_data['payment_id']
    user_id = webhook_data['user_id']

    print(f"⏰ Платеж {payment_id} истек")
    print(f"Пользователь: {user_id}")

    # Здесь ваша асинхронная логика:
    # - Асинхронно отметить заказ как неоплаченный
    # - Отправить пользователю уведомление о необходимости повторной оплаты

    # await send_notification(user_id, "Время оплаты истекло. Создайте новый платеж.")


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "service": "H1Stars Webhook Handler"}


async def background_payment_checker():
    """Фоновая задача для проверки статусов платежей"""

    async with H1StarsClient(api_key="your_api_key_here") as client:
        while True:
            try:
                # Проверяем баланс каждые 60 секунд
                balance = await client.get_partner_balance()
                print(f"📊 Текущий баланс: {balance['available_for_withdrawal']} RUB")

                await asyncio.sleep(60)

            except Exception as e:
                print(f"❌ Ошибка фоновой проверки: {e}")
                await asyncio.sleep(10)


@app.on_event("startup")
async def startup_event():
    """Запуск фоновых задач при старте приложения"""
    print("🚀 Запуск webhook сервера...")
    print("📡 Webhook URL: http://localhost:8000/webhook")

    # Запускаем фоновую задачу
    asyncio.create_task(background_payment_checker())


if __name__ == "__main__":
    uvicorn.run(
        "webhook_handler:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )