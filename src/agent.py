import anthropic
from rich.console import Console
from .browser import BrowserController
from .page_analyzer import PageAnalyzer
from .tools import TOOLS, is_dangerous_action


console = Console()


SYSTEM_PROMPT = """Ты — AI-агент, управляющий веб-браузером для выполнения задач пользователя.

ПРАВИЛА:
1. Используй analyze_page чтобы понять, что на странице
2. Выбирай селекторы из списка интерактивных элементов
3. Действуй пошагово, проверяя результат каждого действия
4. Если что-то не работает — попробуй другой подход
5. Если нужна информация от пользователя — используй ask_user
6. Когда задача выполнена — используй done с отчётом

ВАЖНО:
- Не придумывай селекторы — бери их со страницы
- Перед деструктивными действиями убедись, что это то, что нужно
- Будь внимателен к контексту и состоянию страницы"""


class Agent:
    def __init__(self, api_key: str, browser: BrowserController):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.browser = browser
        self.analyzer = PageAnalyzer()
        self.messages = []
        self.running = False
        self._user_response = None
        self._waiting_for_user = False

    async def run(self, task: str):
        self.running = True
        self.messages = [{"role": "user", "content": f"Задача: {task}"}]

        console.print(f"\n[bold green]🚀 Начинаю задачу:[/] {task}\n")

        while self.running:
            response = self._call_llm()

            if response.stop_reason == "end_turn":
                self._handle_text_response(response)
                break

            if response.stop_reason == "tool_use":
                await self._handle_tool_calls(response)

    def _call_llm(self):
        return self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=self.messages,
        )

    def _handle_text_response(self, response):
        for block in response.content:
            if hasattr(block, "text"):
                console.print(f"\n[bold blue]💭 Агент:[/] {block.text}")

    async def _handle_tool_calls(self, response):
        self.messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            tool_name = block.name
            tool_input = block.input

            console.print(f"[yellow]🔧 {tool_name}[/]: {tool_input}")

            is_dangerous, reason = is_dangerous_action(tool_name, tool_input)
            if is_dangerous:
                if not self._confirm_action(tool_name, tool_input, reason):
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": "Действие отменено пользователем",
                        }
                    )
                    continue

            result = await self._execute_tool(tool_name, tool_input)

            console.print(
                f"[dim]→ {result[:200]}...[/]"
                if len(result) > 200
                else f"[dim]→ {result}[/]"
            )

            tool_results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": result}
            )

        self.messages.append({"role": "user", "content": tool_results})

    def _confirm_action(self, tool_name: str, args: dict, reason: str) -> bool:
        console.print(f"\n[bold red]⚠️  ВНИМАНИЕ: {reason}[/]")
        console.print(f"Действие: {tool_name} с параметрами {args}")
        response = console.input("[bold]Выполнить? (y/n): [/]")
        return response.lower() in ("y", "yes", "да", "д")

    async def _execute_tool(self, name: str, args: dict) -> str:
        try:
            if name == "goto":
                return await self.browser.goto(args["url"])

            elif name == "click":
                return await self.browser.click(args["selector"])

            elif name == "fill":
                return await self.browser.fill(args["selector"], args["text"])

            elif name == "press":
                return await self.browser.press(args["key"])

            elif name == "scroll":
                return await self.browser.scroll(
                    args.get("direction", "down"), args.get("amount", 500)
                )

            elif name == "analyze_page":
                analysis = await self.analyzer.analyze(self.browser.page)
                return self.analyzer.format_for_llm(analysis)

            elif name == "ask_user":
                console.print(
                    f"\n[bold cyan]❓ Агент спрашивает:[/] {args['question']}"
                )
                answer = console.input("[bold]Ваш ответ: [/]")
                return f"Пользователь ответил: {answer}"

            elif name == "done":
                console.print(
                    f"\n[bold green]✅ Задача выполнена![/]\n{args['summary']}"
                )
                self.running = False
                return "Задача завершена"

            else:
                return f"Неизвестный инструмент: {name}"

        except Exception as e:
            return f"Ошибка выполнения {name}: {e}"
