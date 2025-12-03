TOOLS = [
    {
        "name": "goto",
        "description": "Перейти по URL адресу",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL для перехода"}
            },
            "required": ["url"],
        },
    },
    {
        "name": "click",
        "description": "Кликнуть на элемент по CSS-селектору",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS-селектор элемента"}
            },
            "required": ["selector"],
        },
    },
    {
        "name": "fill",
        "description": "Ввести текст в поле ввода",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS-селектор поля"},
                "text": {"type": "string", "description": "Текст для ввода"},
            },
            "required": ["selector", "text"],
        },
    },
    {
        "name": "press",
        "description": "Нажать клавишу (Enter, Tab, Escape и т.д.)",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Название клавиши"}
            },
            "required": ["key"],
        },
    },
    {
        "name": "scroll",
        "description": "Прокрутить страницу",
        "input_schema": {
            "type": "object",
            "properties": {
                "direction": {
                    "type": "string",
                    "enum": ["up", "down"],
                    "description": "Направление",
                },
                "amount": {
                    "type": "integer",
                    "description": "Количество пикселей",
                    "default": 500,
                },
            },
            "required": ["direction"],
        },
    },
    {
        "name": "analyze_page",
        "description": "Получить содержимое текущей страницы (текст и интерактивные элементы)",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "ask_user",
        "description": "Задать вопрос пользователю, если нужна дополнительная информация",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Вопрос пользователю"}
            },
            "required": ["question"],
        },
    },
    {
        "name": "done",
        "description": "Завершить задачу и сообщить результат",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Итоговый отчёт о выполненной работе",
                }
            },
            "required": ["summary"],
        },
    },
]

DANGEROUS_ACTIONS = {
    "click": [
        "удалить",
        "delete",
        "remove",
        "оплатить",
        "pay",
        "купить",
        "buy",
        "подтвердить",
        "confirm",
        "отправить",
        "send",
        "submit",
    ]
}


def is_dangerous_action(tool_name: str, args: dict) -> tuple[bool, str]:
    """Проверяет, является ли действие потенциально опасным."""
    if tool_name not in DANGEROUS_ACTIONS:
        return False, ""

    keywords = DANGEROUS_ACTIONS[tool_name]
    text_to_check = str(args).lower()

    for keyword in keywords:
        if keyword in text_to_check:
            return True, f"Действие содержит '{keyword}'"

    return False, ""
