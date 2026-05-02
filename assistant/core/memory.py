from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

import aiosqlite


class MemoryStore(ABC):
    @abstractmethod
    async def save(self, key: str, value: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load(self, key: str) -> Any:
        raise NotImplementedError


class SQLiteMemoryStore(MemoryStore):
    def __init__(self, path: str) -> None:
        self.path = path

    async def _ensure(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS memory (k TEXT PRIMARY KEY, v TEXT NOT NULL)"
            )
            await db.commit()

    async def save(self, key: str, value: Any) -> None:
        await self._ensure()
        payload = json.dumps(value)
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT INTO memory(k, v) VALUES(?, ?) ON CONFLICT(k) DO UPDATE SET v=excluded.v",
                (key, payload),
            )
            await db.commit()

    async def load(self, key: str) -> Any:
        await self._ensure()
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute("SELECT v FROM memory WHERE k = ?", (key,))
            row = await cursor.fetchone()
        return None if row is None else json.loads(row[0])
