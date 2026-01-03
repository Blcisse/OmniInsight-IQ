"""
Minimal aiosqlite-compatible shim for offline testing.

This module provides a small subset of the public API used by SQLAlchemy's
``sqlite+aiosqlite`` dialect so we can run tests without installing the real
``aiosqlite`` package from PyPI (network access is restricted in the sandbox).
It wraps Python's built-in ``sqlite3`` driver and exposes async methods by
delegating work to a thread via ``asyncio.to_thread``.
"""

from __future__ import annotations

import asyncio
import sqlite3
from typing import Any, Iterable, Optional


# Expose DBAPI-style attributes expected by SQLAlchemy
apilevel = sqlite3.apilevel
paramstyle = sqlite3.paramstyle
threadsafety = sqlite3.threadsafety
sqlite_version = sqlite3.sqlite_version
sqlite_version_info = sqlite3.sqlite_version_info

Error = sqlite3.Error
Warning = sqlite3.Warning
InterfaceError = sqlite3.InterfaceError
DatabaseError = sqlite3.DatabaseError
DataError = sqlite3.DataError
OperationalError = sqlite3.OperationalError
IntegrityError = sqlite3.IntegrityError
InternalError = sqlite3.InternalError
ProgrammingError = sqlite3.ProgrammingError
NotSupportedError = sqlite3.NotSupportedError


class Cursor:
    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    @property
    def description(self):
        return self._cursor.description

    async def fetchone(self):
        return await asyncio.to_thread(self._cursor.fetchone)

    async def fetchall(self):
        return await asyncio.to_thread(self._cursor.fetchall)

    async def fetchmany(self, size: Optional[int] = None):
        return await asyncio.to_thread(self._cursor.fetchmany, size or 1)

    async def close(self):
        return await asyncio.to_thread(self._cursor.close)

    def __aiter__(self):
        return self

    async def __anext__(self):
        row = await self.fetchone()
        if row is None:
            raise StopAsyncIteration
        return row


class Connection:
    def __init__(self, database: str, **kwargs: Any):
        # mirror aiosqlite defaults while allowing overrides passed through
        row_factory = kwargs.pop("row_factory", sqlite3.Row)
        check_same_thread = kwargs.pop("check_same_thread", False)
        self._conn = sqlite3.connect(database, check_same_thread=check_same_thread, **kwargs)
        self._conn.row_factory = row_factory

    async def cursor(self) -> Cursor:
        cur = await asyncio.to_thread(self._conn.cursor)
        return Cursor(cur)

    async def execute(self, sql: str, parameters: Optional[Iterable[Any]] = None) -> Cursor:
        cur = await self.cursor()
        await asyncio.to_thread(cur._cursor.execute, sql, parameters or [])
        return cur

    async def executemany(self, sql: str, seq_of_parameters: Iterable[Iterable[Any]]) -> Cursor:
        cur = await self.cursor()
        await asyncio.to_thread(cur._cursor.executemany, sql, seq_of_parameters)
        return cur

    async def executescript(self, script: str) -> Cursor:
        cur = await self.cursor()
        await asyncio.to_thread(cur._cursor.executescript, script)
        return cur

    async def commit(self):
        return await asyncio.to_thread(self._conn.commit)

    async def rollback(self):
        return await asyncio.to_thread(self._conn.rollback)

    async def close(self):
        return await asyncio.to_thread(self._conn.close)

    async def __aenter__(self) -> "Connection":
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.close()


async def connect(database: str, **kwargs: Any) -> Connection:
    """Async factory mirroring ``aiosqlite.connect`` signature."""
    return Connection(database, **kwargs)
