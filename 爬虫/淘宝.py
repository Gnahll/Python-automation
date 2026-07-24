import csv
import os
import random
import time
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
from bs4 import BeautifulSoup
from playwright.sync_api import Playwright, sync_playwright, TimeoutError as PlaywrightTimeout


def parse_page_items(page_html):
    soup = BeautifulSoup(page_html, "html.parser")
    items = soup.select("div[class*=\"search-content-col\"]")
    print(f"  当前页找到 {len(items)} 个外层容器")

    page_results = []

    for item in items:
        a_tag = item.find("a")
        if not a_tag:
            continue
        href = a_tag.get("href")
        if not href:
            continue

        card = item.find("div", class_=lambda c: c and "doubleCard--" in c)
        if not card:
            continue

        title_tag = card.find("div", class_=lambda c: c and "title--" in c)
        name = title_tag.text.strip() if title_tag else ""

        price = ""
        price_wrapper = card.find("div", class_=lambda c: c and "priceWrapper--" in c)
        if price_wrapper:
            price_int = price_wrapper.find("div", class_=lambda c: c and "priceInt--" in c)
            price_float = price_wrapper.find("div", class_=lambda c: c and "priceFloat--" in c)
            price = (price_int.text if price_int else "") + (price_float.text if price_float else "")

        sales_tag = card.find("span", class_=lambda c: c and "realSales--" in c)
        sales = sales_tag.text.strip() if sales_tag else ""

        shop_tag = card.find("a", class_=lambda c: c and "shopName--" in c)
        shop = shop_tag.text.strip() if shop_tag else ""

        if name:
            page_results.append([name, price, sales, shop, href])

    return page_results


def build_page_url(base_url, page_num):
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params["s"] = [str((page_num - 1) * 44)]
    new_query = urlencode(params, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def run(playwright):
    browser = playwright.chromium.launch(
        channel="msedge",
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
        ],
    )
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    )
    page = context.new_page()

    page.add_init_script("""
        Object.defineProperty(navigator, "webdriver", {
            get: () => undefined
        });
        Object.defineProperty(navigator, "plugins", {
            get: () => [1, 2, 3, 4, 5]
        });
        Object.defineProperty(navigator, "languages", {
            get: () => ["zh-CN", "zh", "en"]
        });
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
    """)

    keyword = "肌酸"
    base_url = f"https://s.taobao.com/search?q={keyword}"

    print("正在打开淘宝首页...")
    page.goto("https://www.taobao.com/", wait_until="domcontentloaded")
    page.wait_for_timeout(random.randint(3000, 5000))

    all_results = []
    max_pages = 10
    current_page = 1

    while current_page <= max_pages:
        target_url = build_page_url(base_url, current_page)
        print(f"\n===== 正在采集第 {current_page} 页 =====")
        print(f"  URL: {target_url}")

        page.goto(target_url, wait_until="domcontentloaded")
        try:
            page.wait_for_selector("div[class*=\"doubleCard--\"]", timeout=15000)
        except PlaywrightTimeout:
            print("  页面未加载到商品卡片，翻页结束")
            break

        page.wait_for_timeout(random.randint(2000, 4000))

        html = page.content()
        page_items = parse_page_items(html)

        if not page_items:
            print("  当前页无数据，翻页结束")
            break

        all_results.extend(page_items)
        print(f"  第 {current_page} 页采集到 {len(page_items)} 条数据，累计 {len(all_results)} 条")

        current_page += 1

        if current_page <= max_pages:
            delay = random.randint(3, 6)
            print(f"  等待 {delay} 秒后翻下一页...")
            time.sleep(delay)

    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "taobao_data.csv")
    with open(save_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["标题", "价格", "销量", "店铺", "链接"])
        writer.writerows(all_results)
    print(f"\n===== 采集完成 =====")
    print(f"共 {len(all_results)} 条数据，已保存到 -> {save_path}")

    page.pause()

    try:
        context.close()
    except Exception:
        pass
    try:
        browser.close()
    except Exception:
        pass


with sync_playwright() as playwright:
    run(playwright)
