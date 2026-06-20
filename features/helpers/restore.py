import os
import sys
import platform
import paramiko

# --- Настройка путей и импортов ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import DUMP, DB_IP, DB_PORT, DB_NAME

# --- Константы ---
SSH_USER = "postgres"
SSH_PASS = "postgres"
DB_USER = "postgres"
DB_PASS = "postgres"
REMOTE_BACKUP_DIR = "/tmp"

def execute_command(ssh: paramiko.SSHClient, command: str, description: str) -> bool:
    """Выполняет команду на удалённом хосте и проверяет результат."""
    print(f"\n>>> {description}")
    stdin, stdout, stderr = ssh.exec_command(command)
    
    exit_status = stdout.channel.recv_exit_status()
    stdout_result = stdout.read().decode().strip()
    stderr_result = stderr.read().decode().strip()

    if exit_status != 0 or stderr_result:
        print(f"[ОШИБКА] Команда завершилась с кодом {exit_status}")
        if stderr_result:
            print(f"stderr: {stderr_result}")
        return False
    
    if stdout_result:
        print(stdout_result)
    return True

def restore_database():
    """Основная логика восстановления БД через SSH."""
    # 1. Проверка локального файла
    local_backup_path = DUMP
    if platform.system() == "Windows":
        local_backup_path = local_backup_path.replace("/", "\\")

    if not os.path.exists(local_backup_path):
        print(f"[КРИТИЧЕСКАЯ ОШИБКА] Файл бэкапа не найден: {local_backup_path}")
        return False

    print(f"Локальный бэкап: {local_backup_path}")
    print(f"Целевая БД: {DB_NAME} на {DB_IP}:{DB_PORT}")

    # 2. SSH-соединение
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(DB_IP, port=22, username=SSH_USER, password=SSH_PASS)
        print("SSH-соединение установлено.")
    except Exception as e:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА] Не удалось подключиться по SSH: {e}")
        return False

    try:
        # 3. Копирование бэкапа
        remote_backup_path = f"{REMOTE_BACKUP_DIR}/{os.path.basename(local_backup_path)}"
        sftp = ssh.open_sftp()
        sftp.put(local_backup_path, remote_backup_path)
        sftp.close()
        print(f"Бэкап скопирован на сервер: {remote_backup_path}")

        # 4. Подготовка команд (используем переменные из config)
        psql_base = f"PGPASSWORD={DB_PASS} psql -h {DB_IP} -p {DB_PORT} -U {DB_USER}"
        
        cmds = [
            (f"{psql_base} -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{DB_NAME}' AND pid <> pg_backend_pid();\"", 
             "Завершение активных подключений"),
            (f"{psql_base} -c \"DROP DATABASE IF EXISTS {DB_NAME};\"", 
             "Удаление базы данных"),
            (f"{psql_base} -c \"CREATE DATABASE {DB_NAME};\"", 
             "Создание базы данных"),
            (f"PGPASSWORD={DB_PASS} pg_restore -h {DB_IP} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} --no-owner --no-privileges {remote_backup_path}", 
             "Восстановление из бэкапа")
        ]

        # 5. Последовательное выполнение
        for cmd, desc in cmds:
            success = execute_command(ssh, cmd, desc)
            if not success:
                print(f"\n[ПРЕРВАНО] Ошибка на этапе: {desc}. Восстановление остановлено.")
                return False

        print("\n✅ База данных успешно восстановлена.")
        return True

    except Exception as e:
        print(f"[КРИТИЧЕСКАЯ ОШИБКА] Во время выполнения операций: {e}")
        return False
    finally:
        ssh.close()
        print("SSH-соединение закрыто.")

if __name__ == "__main__":
    restore_database()