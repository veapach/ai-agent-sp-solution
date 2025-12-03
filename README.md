# AI Browser Agent

AI-агент для автоматизации браузера, управляемый через Claude API.

## Возможности

- Автономное выполнение задач в браузере
- Persistent sessions (сохраняет сессии между запусками)
- Security layer (подтверждение опасных действий)
- Умное извлечение контента страниц

## Установка

```bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Установить браузеры Playwright
playwright install chromium
```

## Настройка

1. Скопируйте `.env.example` в `.env`
2. Укажите ваш Anthropic API ключ

```bash
cp .env.example .env
```

## Запуск

```bash
python main.py
```

## Примеры задач

- "Открой google.com и найди информацию о погоде в Москве"
- "Прочитай последние 10 писем в яндекс почте и удали спам"
- "Найди 3 вакансии Python-разработчика на hh.ru"

## Архитектура

```
src/
├── browser.py      # Управление браузером через Playwright
├── page_analyzer.py # Извлечение контента страницы
├── agent.py        # AI-агент с Claude API
└── tools.py        # Определение инструментов
```
