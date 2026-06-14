from playwright.sync_api import sync_playwright

def before_all(context):
    context.playwright = sync_playwright().start()
    
    # Читаем параметр из командной строки. По умолчанию chromium.
    browser_name = context.config.userdata.get('browser', 'chromium')
    
    if browser_name == 'firefox':
        context.browser = context.playwright.firefox.launch(headless=False)
    elif browser_name == 'webkit':
        context.browser = context.playwright.webkit.launch(headless=False)
    else:
        context.browser = context.playwright.chromium.launch(headless=False)
        
    context.page = context.browser.new_page()

def after_all(context):
    context.browser.close()
    context.playwright.stop()