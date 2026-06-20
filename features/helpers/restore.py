import os
import subprocess
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import DUMP, DB_IP, DB_PORT, DB_NAME, PG_BIN

def restore_database():
    local_backup = os.path.normpath(DUMP)
    if not os.path.exists(local_backup):
        raise FileNotFoundError(f"Бэкап не найден: {local_backup}")

    psql = os.path.join(PG_BIN, "psql.exe")
    pg_restore = os.path.join(PG_BIN, "pg_restore.exe")

    env = os.environ.copy()
    env["PGPASSWORD"] = "postgres"

    # 1. Отключаем сессии
    subprocess.run(
        f'"{psql}" -h {DB_IP} -p {DB_PORT} -U postgres -c '
        f'"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname=\'{DB_NAME}\' AND pid <> pg_backend_pid();"',
        env=env, shell=True, check=True,  capture_output=True
    )

    # 2. Удаляем БД
    subprocess.run(
        f'"{psql}" -h {DB_IP} -p {DB_PORT} -U postgres -c '
        f'"DROP DATABASE IF EXISTS {DB_NAME};"',
        env=env, shell=True, check=True
    )

    # 3. Создаём БД
    subprocess.run(
        f'"{psql}" -h {DB_IP} -p {DB_PORT} -U postgres -c '
        f'"CREATE DATABASE {DB_NAME};"',
        env=env, shell=True, check=True
    )

    # 4. Восстанавливаем из бэкапа
    subprocess.run(
        f'"{pg_restore}" -h {DB_IP} -p {DB_PORT} -U postgres -d {DB_NAME} '
        f'--no-owner --no-privileges "{local_backup}"',
        env=env, shell=True, check=True
    )

    print("База восстановлена")

if __name__ == "__main__":
    restore_database()