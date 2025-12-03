import re
from dataclasses import dataclass
from playwright.async_api import Page


@dataclass
class InteractiveElement:
    index: int
    tag: str
    selector: str
    text: str
    attributes: dict


class PageAnalyzer:
    """Извлекает и сжимает контент страницы для отправки в LLM."""

    MAX_TEXT_LENGTH = 15000

    async def analyze(self, page: Page) -> dict:
        url = page.url
        title = await page.title()

        elements = await self._extract_interactive_elements(page)
        text_content = await self._extract_text_content(page)

        return {
            "url": url,
            "title": title,
            "text_content": text_content[: self.MAX_TEXT_LENGTH],
            "interactive_elements": elements,
        }

    async def _extract_interactive_elements(self, page: Page) -> list[dict]:
        js_code = """
        () => {
            const elements = [];
            const selectors = 'a, button, input, select, textarea, [role="button"], [onclick], [tabindex="0"]';
            
            document.querySelectorAll(selectors).forEach((el, idx) => {
                const rect = el.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) return;
                if (window.getComputedStyle(el).visibility === 'hidden') return;
                
                const text = (el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || '').trim().slice(0, 100);
                
                let selector = '';
                if (el.id) {
                    selector = '#' + el.id;
                } else if (el.name) {
                    selector = `${el.tagName.toLowerCase()}[name="${el.name}"]`;
                } else if (el.className && typeof el.className === 'string') {
                    const classes = el.className.split(' ').filter(c => c && !c.includes(':') && c.length < 30).slice(0, 2);
                    if (classes.length) {
                        selector = el.tagName.toLowerCase() + '.' + classes.join('.');
                    }
                }
                
                if (!selector) {
                    const tag = el.tagName.toLowerCase();
                    if (text) {
                        selector = `${tag}:has-text("${text.slice(0, 30)}")`;
                    } else {
                        selector = `${tag}:nth-of-type(${idx + 1})`;
                    }
                }
                
                elements.push({
                    index: elements.length,
                    tag: el.tagName.toLowerCase(),
                    selector: selector,
                    text: text,
                    type: el.type || null,
                    href: el.href || null,
                });
            });
            
            return elements.slice(0, 100);
        }
        """

        try:
            return await page.evaluate(js_code)
        except Exception:
            return []

    async def _extract_text_content(self, page: Page) -> str:
        js_code = """
        () => {
            const elementsToRemove = ['script', 'style', 'noscript', 'iframe', 'svg'];
            const clone = document.body.cloneNode(true);
            
            elementsToRemove.forEach(tag => {
                clone.querySelectorAll(tag).forEach(el => el.remove());
            });
            
            return clone.innerText;
        }
        """

        try:
            text = await page.evaluate(js_code)
            text = re.sub(r"\n{3,}", "\n\n", text)
            text = re.sub(r" {2,}", " ", text)
            return text.strip()
        except Exception:
            return ""

    def format_for_llm(self, analysis: dict) -> str:
        lines = [
            f"URL: {analysis['url']}",
            f"Заголовок: {analysis['title']}",
            "",
            "=== Интерактивные элементы ===",
        ]

        for el in analysis["interactive_elements"]:
            el_info = f"[{el['index']}] <{el['tag']}>"
            if el.get("text"):
                el_info += f" \"{el['text'][:50]}\""
            if el.get("href"):
                el_info += f" -> {el['href'][:60]}"
            if el.get("type"):
                el_info += f" (type={el['type']})"
            lines.append(el_info)

        lines.extend(
            [
                "",
                "=== Текст страницы ===",
                analysis["text_content"][:8000],
            ]
        )

        return "\n".join(lines)
