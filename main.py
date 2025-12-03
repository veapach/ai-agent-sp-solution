import os
import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from src.browser import BrowserController
from src.agent import Agent


console = Console()


async def main():
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        console.print("[red]Ошибка: Укажите ANTHROPIC_API_KEY в .env файле[/]")
        return

    user_data_dir = os.getenv("USER_DATA_DIR", "./browser_data")
    headless = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"

    console.print(
        Panel.fit(
            "[bold cyan]🤖 AI Browser Agent[/]\n"
            "Введите задачу для выполнения или 'exit' для выхода",
            border_style="cyan",
        )
    )

    browser = BrowserController(user_data_dir=user_data_dir, headless=headless)

    try:
        await browser.start()
        console.print("[green]✓ Браузер запущен[/]\n")

        agent = Agent(api_key=api_key, browser=browser)

        while True:
            try:
                task = console.input("[bold cyan]📝 Задача:[/] ").strip()

                if not task:
                    continue

                if task.lower() in ("exit", "quit", "выход"):
                    break

                await agent.run(task)
                console.print("\n" + "─" * 50 + "\n")

            except KeyboardInterrupt:
                console.print("\n[yellow]Прервано пользователем[/]")
                break

    finally:
        await browser.close()
        console.print("[dim]Браузер закрыт[/]")


if __name__ == "__main__":
    asyncio.run(main())
