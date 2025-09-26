"""
Пример использования партнерского API H1Stars (асинхронный)
"""

import asyncio
from h1stars_sdk import H1StarsClient, H1StarsError
from datetime import datetime, timedelta


async def main():
    """Основная асинхронная функция для работы с партнерским API"""

    async with H1StarsClient(api_key="your_api_key_here") as client:
        try:
            # Получение баланса партнера
            print("💰 Получение баланса партнера...")
            balance = await client.get_partner_balance()

            print(f"Общий баланс: {balance['balance']} {balance['currency']}")
            print(f"В процессе вывода: {balance['pending_withdrawals']} {balance['currency']}")
            print(f"Доступно для вывода: {balance['available_for_withdrawal']} {balance['currency']}")
            print(f"Последнее обновление: {balance['last_updated']}")

            # Создание заявки на вывод средств
            if balance['available_for_withdrawal'] >= 1000:
                print("\n💳 Создание заявки на вывод...")

                withdrawal = await client.create_withdrawal(
                    amount=1000.00,
                    payment_method="card",
                    card_number="4111111111111111",
                    cardholder_name="IVAN PETROV"
                )

                print("✅ Заявка на вывод создана!")
                print(f"Сумма: {withdrawal.get('amount', 'N/A')}")
                print(f"Статус: {withdrawal.get('status', 'N/A')}")

            else:
                print(f"⚠️  Недостаточно средств для вывода (минимум 1000 RUB)")

            # История транзакций за последние 30 дней
            print("\n📊 История транзакций за последние 30 дней...")

            date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            date_to = datetime.now().strftime('%Y-%m-%d')

            transactions = await client.get_partner_transactions(
                limit=10,
                offset=0,
                date_from=date_from,
                date_to=date_to
            )

            if 'transactions' in transactions and transactions['transactions']:
                print(f"Найдено транзакций: {len(transactions['transactions'])}")

                for transaction in transactions['transactions'][:5]:  # Показываем первые 5
                    print(f"- {transaction.get('date', 'N/A')}: {transaction.get('amount', 'N/A')} RUB "
                          f"({transaction.get('type', 'N/A')}) - {transaction.get('description', 'N/A')}")

            else:
                print("Транзакции не найдены")

            # Статистика за разные периоды
            print("\n📈 Статистика...")

            # За текущий месяц
            current_month = datetime.now().strftime('%Y-%m-01')
            month_transactions = await client.get_partner_transactions(
                date_from=current_month,
                limit=1000
            )

            if 'transactions' in month_transactions:
                month_total = sum(
                    float(t.get('amount', 0))
                    for t in month_transactions['transactions']
                    if t.get('type') == 'payment'
                )
                print(f"Доход за текущий месяц: {month_total:.2f} RUB")

        except H1StarsError as e:
            print(f"❌ Ошибка H1Stars API: {e}")

        except Exception as e:
            print(f"❌ Общая ошибка: {e}")


async def parallel_requests_example():
    """Пример параллельного выполнения запросов к партнерскому API"""

    async with H1StarsClient(api_key="your_api_key_here") as client:
        try:
            print("🚀 Выполняем несколько запросов параллельно...")

            # Запускаем несколько запросов одновременно
            balance_task = client.get_partner_balance()

            # Транзакции за разные периоды
            current_month = datetime.now().strftime('%Y-%m-01')
            last_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            current_month_task = client.get_partner_transactions(
                date_from=current_month,
                limit=100
            )

            last_month_task = client.get_partner_transactions(
                date_from=last_month,
                date_to=current_month,
                limit=100
            )

            # Ждем завершения всех задач
            balance, current_transactions, last_transactions = await asyncio.gather(
                balance_task,
                current_month_task,
                last_month_task,
                return_exceptions=True
            )

            # Обрабатываем результаты
            if isinstance(balance, dict):
                print(f"💰 Баланс: {balance['available_for_withdrawal']} RUB")

            if isinstance(current_transactions, dict):
                current_count = len(current_transactions.get('transactions', []))
                print(f"📊 Транзакций за текущий период: {current_count}")

            if isinstance(last_transactions, dict):
                last_count = len(last_transactions.get('transactions', []))
                print(f"📊 Транзакций за прошлый период: {last_count}")

        except Exception as e:
            print(f"❌ Ошибка параллельных запросов: {e}")


async def monitoring_example():
    """Пример мониторинга баланса и транзакций"""

    async with H1StarsClient(api_key="your_api_key_here") as client:
        print("🔍 Запуск мониторинга (нажмите Ctrl+C для остановки)...")

        try:
            while True:
                balance = await client.get_partner_balance()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Баланс: {balance['available_for_withdrawal']} RUB")

                # Ждем 30 секунд перед следующей проверкой
                await asyncio.sleep(30)

        except KeyboardInterrupt:
            print("\n⏹️  Мониторинг остановлен")

        except Exception as e:
            print(f"❌ Ошибка мониторинга: {e}")


if __name__ == "__main__":
    # Основной пример
    print("=== Основной пример ===")
    asyncio.run(main())

    # Параллельные запросы
    print("\n=== Параллельные запросы ===")
    asyncio.run(parallel_requests_example())

    # Мониторинг (раскомментируйте для использования)
    # print("\n=== Мониторинг ===")
    # asyncio.run(monitoring_example())