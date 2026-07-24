from playwright.sync_api import Playwright, sync_playwright


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(channel="msedge", headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.baidu.com/")
    page.get_by_role("textbox", name="中国男篮对阵黎巴嫩裁判确定").click()
    page.get_by_role("button", name="百度一下").click()
    page.pause()

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)