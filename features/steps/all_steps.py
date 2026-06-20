from behave import given, when, then
import config
import time

from features.helpers.restore import restore_database

IP = config.IP

@Given('Открываем браузер') # type: ignore
def open_browser(context):
    context.page.goto(f"http://{IP}")

@Given('Восстанавливаем БД из бэкапа') # type: ignore
def step_restore_db(context):
    restore_database()

@Given('Ждём "{timeout}" сек.') # type: ignore
def wait(context, timeout):
    seconds = int(timeout)
    time.sleep(seconds)

@Given('В поле "{field}" вводим "{value}"') # type: ignore
def enter_to_field(context, field, value):
    # Playwright сам ждёт появления элемента и его готовности к вводу
    locator = f"//label[contains(text(), '{field}')]/following-sibling::div//input"
    
    # fill() автоматически очищает поле перед вводом
    context.page.fill(locator, value)

@Given('Нажимаем на кнопку "{button}"') # type: ignore
def click_button(context, button):
    locator = f"//button[contains(text(), '{button}')]"
    context.page.click(locator)

@Given('Проверяем что текущий пользователь "{user}"') # type: ignore
def check_current_user(context, user):
    locator = f'//header//p[contains(text(), "{user}")]'
    context.page.wait_for_selector(locator)