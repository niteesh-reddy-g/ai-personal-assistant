from __future__ import annotations

import re
from typing import Any

from assistant.agents.base_agent import BaseAgent
from assistant.tools.browser_tool import BrowserTool


class ShoppingAgent(BaseAgent):
    name = "shopping_agent"
    description = "Search marketplaces for product deals and return structured results"
    capabilities = ["product_search", "price_compare"]

    def __init__(self, browser_tool: BrowserTool) -> None:
        self.browser_tool = browser_tool

    @staticmethod
    def _extract_price_number(price_text: str) -> float:
        m = re.search(r"([\d,.]+)", price_text)
        if not m:
            return float("inf")
        return float(m.group(1).replace(",", ""))

    async def run(self, task: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        query = task["query"]
        platforms = task["platforms"]
        products = await self.browser_tool.search_products(query, platforms)
        sorted_products = sorted(products, key=lambda p: self._extract_price_number(p.get("price", "")))
        return {"agent": self.name, "query": query, "best": sorted_products[0] if sorted_products else None, "products": sorted_products}
