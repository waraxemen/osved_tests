import subprocess
import logging
 

def run_command_live(command, timeout): # Вывод команды в реальном времени
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    if not process.stdout:
        return None

    for line in process.stdout:
        print(line, end='')

    try:
        returncode = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        raise

    return returncode


def run_tests(timeout=600):
    # Список фич-файлов для запуска
    features = [
        "features/проверка_создания_пользователя.feature",
    ]
    
    # Список браузеров для прогона
    browsers = ["chromium", "firefox"]

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.NOTSET)
    
    # Очищаем лог
    with open('test_log.txt', 'w', encoding='utf-8') as log_file:
        pass 
    
    handler = logging.FileHandler('test_log.txt', mode='w', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("Начало выполнения тестов")

    all_passed = True
    
    # Двойной цикл: сначала по браузерам, потом по фичам (или наоборот, как удобнее)
    # Здесь логика: Для каждого браузера запускаем все фичи
    for browser in browsers:
        logger.info(f"--- Запуск тестов в браузере: {browser.upper()} ---")
        print(f"\n>>> ЗАПУСК В {browser.upper()}")
        
        for feature in features:
            # Формируем команду с параметром -D browser=...
            command = f"behave {feature} -D browser={browser}"
            
            print(f"Запуск: {command}")
            try:
                returncode = run_command_live(command, timeout)
                
                if returncode is None:
                    msg = f"Таймаут команды: {command}"
                    logger.error(msg)
                    print(msg)
                    all_passed = False
                    break # Прерываем внутренний цикл (фичи), но можно и внешний
                
                if returncode != 0:
                    msg = f"Ошибка в {browser} ({feature}): код {returncode}"
                    logger.error(msg)
                    print(msg)
                    all_passed = False
                    break # Если один тест упал, прерываем текущий браузер
                    
            except Exception as e:
                msg = f"Исключение при выполнении {command}: {str(e)}"
                logger.error(msg)
                print(msg)
                all_passed = False
                break
        
        if not all_passed:
            break # Если упало в одном браузере, можно не запускать следующий

    if all_passed:
        logger.info("Все тесты во всех браузерах прошли успешно")
        print("\n ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО")
    else:
        logger.error("Тесты завершились с ошибками")
        print("\n ЕСТЬ ОШИБКИ")

    logger.handlers.clear()
    return all_passed



if __name__ == '__main__':
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='test_log.txt', level=logging.INFO, format=log_format, encoding='utf-8')
    run_tests()




# для запуска в терминале:
# python start_all_tests.py