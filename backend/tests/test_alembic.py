"""Verify that alembic upgrade head creates all expected tables."""

import os
import subprocess
import sys

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


EXPECTED_TABLES = {
    "admins",
    "categorias",
    "envios_config",
    "imagenes",
    "pagos",
    "pedido_items",
    "pedidos",
    "productos",
}


@pytest.mark.asyncio
async def test_alembic_upgrade_creates_all_tables(tmp_path):
    """Running alembic upgrade head MUST create all 8 expected tables."""
    db_path = tmp_path / "test_nutristore.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"

    # Run alembic via subprocess (env.py uses asyncio.run which conflicts with pytest-asyncio)
    env = os.environ.copy()
    env["DATABASE_URL"] = db_url

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=".",
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, (
        f"alembic upgrade failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )

    # Verify all tables exist
    engine = create_async_engine(db_url)
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%' "
                "AND name != 'alembic_version'"
            )
        )
        rows = result.fetchall()
        actual_tables = {row[0] for row in rows}

    await engine.dispose()

    assert actual_tables == EXPECTED_TABLES, (
        f"Expected tables {EXPECTED_TABLES}, got {actual_tables}"
    )
