"""
Пример базового использования H1Stars SDK (асинхронный)
"""

import asyncio
from h1stars_sdk import H1StarsClient, H1StarsError


async def main():
    """Основная асинхронная функция"""

    # Используем async context manager для автоматического управления сессией
    async with H1StarsClient(api_key="your_api_key_here") as client:
        try:
            # Создание платежа
            print("Создание платежа...")
            payment = await client.create_payment(
                amount=100.50,
                description="Покупка звезд в игре",
                user_id="user123",
                callback_url="https://yoursite.com/webhook",
                return_url="https://yoursite.com/success"
            )

            print("✅ Платеж создан успешно!")
            print(f"Payment ID: {payment['payment_id']}")
            print(f"Payment URL: {payment['payment_url']}")
            print(f"Amount: {payment['amount']} RUB")
            print(f"Status: {payment['status']}")
            print(f"Expires at: {payment['expires_at']}")

            # Пользователь должен перейти на payment_url для оплаты
            print(f"\n🔗 Отправьте пользователя на: {payment['payment_url']}")

            # Проверка статуса платежа
            print(f"\nПроверка статуса платежа {payment['payment_id']}...")
            payment_status = await client.get_payment(payment['payment_id'])

            print(f"Status: {payment_status['status']}")
            print(f"Created at: {payment_status['created_at']}")

            if payment_status['status'] == 'completed':
                print("💰 Платеж успешно оплачен!")

        except H1StarsError as e:
            print(f"❌ Ошибка H1Stars: {e}")

        except Exception as e:
            print(f"❌ Общая ошибка: {e}")


async def multiple_payments_example():
    """Пример создания нескольких платежей параллельно"""

    async with H1StarsClient(api_key="your_api_key_here") as client:
        try:
            # Создаем несколько платежей параллельно
            tasks = [
                client.create_payment(
                    amount=100.0 + i * 10,
                    description=f"Платеж #{i+1}",
                    user_id=f"user_{i+1}"
                )
                for i in range(3)
            ]

            payments = await asyncio.gather(*tasks)

            print("✅ Все платежи созданы:")
            for payment in payments:
                print(f"- {payment['payment_id']}: {payment['amount']} RUB")

        except Exception as e:
            print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    # Запуск основного примера
    asyncio.run(main())

    # Пример параллельных запросов
    print("\n" + "="*50)
    print("Пример параллельных платежей:")
    asyncio.run(multiple_payments_example())