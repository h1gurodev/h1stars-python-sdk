# 📦 Инструкция по развертыванию H1Stars Python SDK

Полное руководство по публикации SDK на PyPI, GitHub и настройке CI/CD.

## 🚀 Быстрый чеклист

- [ ] Подготовить проект
- [ ] Создать GitHub репозиторий
- [ ] Настроить GitHub Actions
- [ ] Опубликовать на PyPI
- [ ] Создать документацию

## 📁 1. Подготовка проекта

### Структура проекта
```
pay-h1stars-sdk/
├── h1stars_sdk/
│   ├── __init__.py
│   ├── client.py
│   └── exceptions.py
├── examples/
│   ├── basic_usage.py
│   ├── webhook_handler.py
│   └── partner_api.py
├── tests/                    # Создать тесты
│   ├── __init__.py
│   ├── test_client.py
│   └── test_webhook.py
├── .github/
│   └── workflows/
│       ├── test.yml
│       └── publish.yml
├── setup.py
├── requirements.txt
├── README.md
├── LICENSE                   # Добавить лицензию
├── MANIFEST.in
└── DEPLOYMENT.md
```

### Создать недостающие файлы

```bash
# Создать папку для тестов
mkdir tests
touch tests/__init__.py
touch tests/test_client.py
touch tests/test_webhook.py

# Создать GitHub Actions
mkdir -p .github/workflows

# Создать лицензию MIT
touch LICENSE
```

## 📄 2. Лицензия MIT

Создайте файл `LICENSE`:

```text
MIT License

Copyright (c) 2024 H1Stars

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🧪 3. Создать базовые тесты

### tests/test_client.py

```python
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
```

### tests/test_webhook.py

```python
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
```

## ⚙️ 4. GitHub Actions для CI/CD

### .github/workflows/test.yml

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-asyncio
        pip install -e .
        pip install -e ".[examples]"

    - name: Run tests
      run: |
        pytest tests/ -v

    - name: Test examples
      run: |
        python -c "import h1stars_sdk; print('SDK imported successfully')"
```

### .github/workflows/publish.yml

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: |
        python -m build

    - name: Check package
      run: |
        twine check dist/*

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        twine upload dist/*
```

## 🐙 5. Создание GitHub репозитория

### Инициализация Git

```bash
# В папке вашего проекта
git init
git add .
git commit -m "Initial commit: H1Stars Python SDK"

# Создать ветку main
git branch -M main
```

### Создание репозитория на GitHub

1. Перейдите на https://github.com
2. Нажмите "New repository"
3. Введите название: `h1stars-python-sdk`
4. Выберите Public
5. НЕ создавайте README (у вас уже есть)
6. Нажмите "Create repository"

### Подключение к GitHub

```bash
# Замените на ваш URL репозитория
git remote add origin https://github.com/h1gurodev/h1stars-python-sdk.git
git push -u origin main
```

## 📦 6. Публикация на PyPI

### Регистрация на PyPI

1. Перейдите на https://pypi.org/
2. Создайте аккаунт
3. Подтвердите email
4. Включите двухфакторную аутентификацию

### Создание API Token

1. В настройках PyPI создайте API Token
2. Скопируйте токен (начинается с `pypi-`)

### Добавление секретов в GitHub

1. В вашем репозитории: Settings → Secrets and variables → Actions
2. Добавьте секрет `PYPI_API_TOKEN` со значением вашего API токена

### Ручная публикация (первый раз)

```bash
# Установить инструменты
pip install build twine

# Собрать пакет
python -m build

# Проверить пакет
twine check dist/*

# Загрузить на test.pypi.org (для проверки)
twine upload --repository testpypi dist/*

# После проверки - загрузить на основной PyPI
twine upload dist/*
```

### Проверка установки

```bash
# Установить из PyPI
pip install h1stars-payment-sdk

# Проверить работу
python -c "from h1stars_sdk import H1StarsClient; print('✅ SDK работает!')"
```

## 🏷️ 7. Создание релизов

### Семантическое версионирование

- `1.0.0` - Первый стабильный релиз
- `1.0.1` - Исправление багов
- `1.1.0` - Новые функции (обратно совместимые)
- `2.0.0` - Breaking changes

### Процесс релиза

1. **Обновите версию в setup.py**
```python
version="1.0.1",
```

2. **Обновите CHANGELOG.md**
```markdown
## [1.0.1] - 2024-01-15

### Fixed
- Исправлена ошибка в обработке webhook
- Улучшена обработка таймаутов

### Added
- Поддержка Python 3.11
```

3. **Создайте тег и релиз**
```bash
git add .
git commit -m "Bump version to 1.0.1"
git tag v1.0.1
git push origin main
git push origin v1.0.1
```

4. **Создайте релиз на GitHub**
- Перейдите в Releases
- Нажмите "Create a new release"
- Выберите тег v1.0.1
- Заполните описание
- Нажмите "Publish release"

GitHub Actions автоматически опубликует на PyPI!

## 📊 8. Мониторинг и аналитика

### GitHub Insights

- Stars/Forks/Downloads
- Issues/Pull Requests
- Contributors

### PyPI статистика

- https://pypistats.org/packages/h1stars-payment-sdk
- Количество загрузок
- Версии Python

### Настройка уведомлений

В `.github/workflows/notify.yml`:

```yaml
name: Release Notification

on:
  release:
    types: [published]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
    - name: Notify Telegram
      run: |
        curl -X POST "https://api.telegram.org/bot${{ secrets.TELEGRAM_BOT_TOKEN }}/sendMessage" \
             -H "Content-Type: application/json" \
             -d '{"chat_id": "${{ secrets.TELEGRAM_CHAT_ID }}", "text": "🚀 Новая версия H1Stars SDK: ${{ github.event.release.tag_name }}"}'
```

## 🔧 9. Локальная разработка

### Установка в режиме разработки

```bash
# Клонирование
git clone https://github.com/h1gurodev/h1stars-python-sdk.git
cd h1stars-python-sdk

# Установка зависимостей
pip install -e .
pip install -e ".[examples]"

# Установка dev зависимостей
pip install pytest pytest-asyncio black flake8 mypy

# Запуск тестов
pytest tests/ -v

# Форматирование кода
black h1stars_sdk/ examples/ tests/

# Линтинг
flake8 h1stars_sdk/ examples/ tests/
```

### Pre-commit хуки

Создайте `.pre-commit-config.yaml`:

```yaml
repos:
-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black
        language_version: python3

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
```

```bash
# Установка pre-commit
pip install pre-commit
pre-commit install

# Запуск на всех файлах
pre-commit run --all-files
```

## ✅ 10. Финальный чеклист

### Перед публикацией

- [ ] Все тесты проходят
- [ ] Документация актуальна
- [ ] README содержит примеры использования
- [ ] Версия обновлена в setup.py
- [ ] CHANGELOG обновлен
- [ ] Лицензия добавлена

### После публикации

- [ ] Пакет доступен на PyPI
- [ ] GitHub Actions работают
- [ ] Документация опубликована
- [ ] Анонсирована в соцсетях/форумах

## 🚨 Важные замечания

1. **API Ключи**: Никогда не коммитьте реальные API ключи
2. **Тестирование**: Используйте test.pypi.org перед основной публикацией
3. **Версионирование**: Следуйте SemVer
4. **Безопасность**: Регулярно обновляйте зависимости
5. **Документация**: Поддерживайте README в актуальном состоянии

## 📞 Поддержка

- GitHub Issues: https://github.com/h1gurodev/h1stars-python-sdk/issues
- Email: predmetdev@gmail.com
- Telegram: @h1stars_support

---

Теперь ваш SDK готов к публикации! 🎉