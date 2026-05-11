#!/usr/bin/env python3
"""Standalone CLI script to create the initial admin user.

Reads ADMIN_EMAIL and ADMIN_PASSWORD from environment / .env.
Idempotent — does nothing if an admin already exists.
"""
import asyncio
import sys
import os

# Ensure the backend package is importable when run as a script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import settings
from app.database import async_session
from app.usuarios.service import seed_admin


async def main():
    async with async_session() as session:
        await seed_admin(session)
    print(f"Admin {settings.ADMIN_EMAIL} seeded successfully.")


if __name__ == "__main__":
    asyncio.run(main())
