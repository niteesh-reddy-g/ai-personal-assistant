from __future__ import annotations

from typing import Any

from playwright.async_api import async_playwright


class BrowserTool:
    async def search_products(self, query: str, platforms: list[dict[str, str]]) -> list[dict[str, Any]]:
        products: list[dict[str, Any]] = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            for platform in platforms:
                url = platform["search_url"].format(query=query.replace(" ", "+"))
                await page.goto(url, wait_until="domcontentloaded")
                cards = page.locator(platform["card_selector"])
                count = min(await cards.count(), platform.get("max_items", 5))
                for i in range(count):
                    card = cards.nth(i)
                    title = await card.locator(platform["title_selector"]).first.inner_text()
                    price = await card.locator(platform["price_selector"]).first.inner_text()
                    link = await card.locator(platform["link_selector"]).first.get_attribute("href")
                    if link and link.startswith("/"):
                        link = platform.get("base_url", "") + link
                    products.append({"title": title.strip(), "price": price.strip(), "platform": platform["name"], "link": link or ""})
            await browser.close()
        return products
