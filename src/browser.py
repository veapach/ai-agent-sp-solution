import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class BrowserController:
    def __init__(self, user_data_dir: str = "./browser_data", headless: bool = False):
        self.user_data_dir = Path(user_data_dir)
        self.headless = headless
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def start(self) -> Page:
        self.user_data_dir.mkdir(parents=True, exist_ok=True)

        self._playwright = await async_playwright().start()
        self._context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
            viewport={"width": 1280, "height": 900},
            locale="ru-RU",
        )

        self._page = (
            self._context.pages[0]
            if self._context.pages
            else await self._context.new_page()
        )
        return self._page

    @property
    def page(self) -> Page:
        if not self._page:
            raise RuntimeError("Браузер не запущен. Вызовите start() сначала.")
        return self._page

    async def goto(self, url: str) -> str:
        await self.page.goto(url, wait_until="domcontentloaded")
        await self.page.wait_for_timeout(500)
        return f"Перешёл на {self.page.url}"

    async def click(self, selector: str) -> str:
        try:
            await self.page.click(selector, timeout=5000)
            await self.page.wait_for_timeout(500)
            return f"Кликнул на элемент: {selector}"
        except Exception as e:
            return f"Ошибка клика: {e}"

    async def fill(self, selector: str, text: str) -> str:
        try:
            await self.page.fill(selector, text, timeout=5000)
            return f"Ввёл текст в {selector}"
        except Exception as e:
            return f"Ошибка ввода: {e}"

    async def press(self, key: str) -> str:
        await self.page.keyboard.press(key)
        return f"Нажал клавишу: {key}"

    async def scroll(self, direction: str = "down", amount: int = 500) -> str:
        delta = amount if direction == "down" else -amount
        await self.page.mouse.wheel(0, delta)
        await self.page.wait_for_timeout(300)
        return f"Проскроллил {direction} на {amount}px"

    async def screenshot(self) -> bytes:
        return await self.page.screenshot()

    async def get_url(self) -> str:
        return self.page.url

    async def get_title(self) -> str:
        return await self.page.title()

    async def close(self):
        if self._context:
            await self._context.close()
        if self._playwright:
            await self._playwright.stop()
