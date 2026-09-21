#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] ENV=${ENV:-development}"
echo "[entrypoint] DB=${DATABASE_DB_HOST:-db}:${DATABASE_DB_PORT:-5432}/${DATABASE_DB_NAME:-?}"
echo "[entrypoint] REDIS=${REDIS_HOST:-redis}:${REDIS_PORT:-6379}"

for i in $(seq 1 30); do
    if python -c "
import asyncio, asyncpg, os
async def main():
    conn = await asyncpg.connect(
        user=os.environ['DATABASE_DB_USER'],
        password=os.environ['DATABASE_DB_PASSWORD'],
        host=os.getenv('DATABASE_DB_HOST', 'db'),
        port=int(os.getenv('DATABASE_DB_PORT', '5432')),
        database=os.environ['DATABASE_DB_NAME'],
    )
    await conn.close()
asyncio.run(main())
" 2>/dev/null; then
        echo "[entrypoint] database ready"
        break
    fi
    echo "[entrypoint] waiting for db ($i/30)..."
    sleep 2
done

if [[ -f "alembic.ini" ]]; then
    echo "[entrypoint] running migrations..."
    alembic upgrade head
fi

exec "$@"