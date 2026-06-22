from behave import given, when, then
import config
import time

from features.helpers.restore import restore_database

IP = config.IP

@given('Открываем браузер')  # type: ignore
def open_browser(context):
    context.page.goto(f"http://{IP}")

@given('Восстанавливаем БД из бэкапа')  # type: ignore
def step_restore_db(context):
    restore_database()

@given('Ждём "{timeout}" сек.')  # type: ignore
def wait(context, timeout):
    seconds = int(timeout)
    time.sleep(seconds)

@given('В поле "{field}" вводим "{value}"')  # type: ignore
def enter_to_field(context, field, value):
    # Ищем элемент разными способами
    element = None
    
    # 1. Пробуем найти input
    element = context.page.locator(
        f"//label[contains(text(), '{field}')]/following::input[1]"
    ).first
    if element.count() > 0:
        element.wait_for(state="visible", timeout=5000)
        element.clear()
        element.fill(value)
        return
    
    # 2. Пробуем найти textarea
    element = context.page.locator(
        f"//label[contains(text(), '{field}')]/following::textarea[1]"
    ).first
    if element.count() > 0:
        element.wait_for(state="visible", timeout=5000)
        element.clear()
        element.fill(value)
        return
    
    # 3. Пробуем найти select
    element = context.page.locator(
        f"//label[contains(text(), '{field}')]/following::select[1]"
    ).first
    if element.count() > 0:
        element.wait_for(state="visible", timeout=5000)
        element.select_option(value)
        return
    
    # 4. Пробуем найти combobox (div с ролью combobox) - ЭТО ДЛЯ ФОРМЫ ДОПУСКА
    element = context.page.locator(
        f"//label[contains(text(), '{field}')]/following::div[@role='combobox'][1]"
    ).first
    if element.count() > 0:
        element.wait_for(state="visible", timeout=5000)
        # Кликаем по combobox, чтобы открыть выпадающий список
        element.click()
        # Ждём появления опций и выбираем нужную
        context.page.wait_for_selector(f"//li[contains(text(), '{value}')]", timeout=5000)
        context.page.locator(f"//li[contains(text(), '{value}')]").first.click()
        return
    
    # 5. Пробуем найти contenteditable div
    element = context.page.locator(
        f"//label[contains(text(), '{field}')]/following::div[@contenteditable='true'][1]"
    ).first
    if element.count() > 0:
        element.wait_for(state="visible", timeout=5000)
        element.evaluate('el => el.textContent = ""')
        element.type(value, delay=50)
        return
    
    # 6. Пробуем найти через родительский контейнер
    element = context.page.locator(
        f"//div[label[contains(text(), '{field}')]]//input | "
        f"//div[label[contains(text(), '{field}')]]//textarea | "
        f"//div[label[contains(text(), '{field}')]]//div[@role='combobox'] | "
        f"//div[label[contains(text(), '{field}')]]//select"
    ).first
    if element.count() > 0:
        # Проверяем тип элемента
        tag_name = element.evaluate('el => el.tagName.toLowerCase()')
        role = element.get_attribute('role')
        
        if tag_name == 'select':
            element.select_option(value)
        elif role == 'combobox':
            element.click()
            context.page.wait_for_selector(f"//li[contains(text(), '{value}')]", timeout=5000)
            context.page.locator(f"//li[contains(text(), '{value}')]").first.click()
        else:
            element.wait_for(state="visible", timeout=5000)
            element.clear()
            element.fill(value)
        return
    
    # Если ничего не найдено
    raise Exception(f'Не найдено поле "{field}"')

@given('Нажимаем на кнопку "{button}"')  # type: ignore
def click_button(context, button):
    context.page.click(f"//button[contains(text(), '{button}')]")

@given('Проверяем что текущий пользователь "{user}"')  # type: ignore
def check_current_user(context, user):
    context.page.wait_for_selector(f'//header//p[contains(text(), "{user}")]')

@given('Переходим на боковую вкладку "{tab}"')  # type: ignore
def switch_to_tab(context, tab):
    context.page.click(f'//ul/li//span[contains(text(),"{tab}")]')

@given('В ниспадающем меню "{field}" выбираем "{value}"')  # type: ignore
def select_from_dropdown(context, field, value):
    # Находим combobox (выпадающий список) по label
    combobox = context.page.locator(
        f"//label[contains(text(), '{field}')]/following::div[@role='combobox'][1]"
    ).first
    
    if combobox.count() == 0:
        # Пробуем найти через родительский контейнер
        combobox = context.page.locator(
            f"//div[label[contains(text(), '{field}')]]//div[@role='combobox']"
        ).first
    
    if combobox.count() == 0:
        raise Exception(f'Не найдено выпадающее меню "{field}"')
    
    combobox.wait_for(state="visible", timeout=5000)
    combobox.click()  # Открываем выпадающий список
    
    # Ждём появления опций и выбираем нужную
    option = context.page.locator(f"//li[contains(text(), '{value}')]").first
    option.wait_for(state="visible", timeout=5000)
    option.click()