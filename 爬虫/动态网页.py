import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# 目标：百度首页（含动态热搜榜）
url = 'https://www.baidu.com'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0'}

# --- 方法1：传统 Requests（静态） ---
print("【Requests结果】")
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'lxml')
# 尝试查找热搜榜的标签（通过F12观察到的类名）
hot_news = soup.select('div#s-hotsearch-wrapper')
print(f"找到热搜区域数量：{len(hot_news)}")  # 大概率输出 0，因为还没加载
for news in hot_news:
    links=news.find_all('li', class_='hotsearch-item')
    for link in links:
        a_tag = link.find('a', class_='title-content')
        span = a_tag.find('span',class_='title-content-title')
        if span:
            print(span.text)
# --- 方法2：Playwright（动态） ---
print("\n【Playwright结果】")
with sync_playwright() as p:
    # 启动隐形浏览器（headless=False 可显示窗口便于调试）
    browser = p.chromium.launch(channel="msedge", headless=False) # True表示后台运行
    page = browser.new_page()

    # 访问页面
    page.goto(url)

    # 【核心】等待热搜区域加载出来（F12里看到的id）
    # 最多等5秒，直到这个元素出现
    page.wait_for_selector('div#s-hotsearch-wrapper', timeout=5000)

    # 获取渲染完成后的完整HTML
    rendered_html = page.content()
    browser.close()

# 用BeautifulSoup解析渲染后的HTML
soup_dynamic = BeautifulSoup(rendered_html, 'lxml')
hot_news_dynamic = soup_dynamic.select('div#s-hotsearch-wrapper')
for news in hot_news_dynamic:
    links=news.find_all('li', class_='hotsearch-item')
    for link in links:
        a_tag = link.find('a', class_='title-content')
        span = a_tag.find('span',class_='title-content-title')
        if span:
            print(span.text)
print(f"找到热搜区域数量：{len(hot_news_dynamic)}")  # 输出 1，成功！