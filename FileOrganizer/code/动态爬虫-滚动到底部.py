"""
无限滚动爬虫 + 数据存储（CSV + JSON）
目标网站：ScrapingCourse.com 的无限滚动页面
"""

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import json
import os

# ---------- 配置 ----------
URL = "https://www.douban.com/explore/"
OUTPUT_CSV = "products.csv"
OUTPUT_JSON = "products.json"
MAX_SCROLLS = 10  # 最多滚动次数，防止死循环
SCROLL_PAUSE = 2  # 每次滚动后等待时间（秒）

# ---------- 启动浏览器 ----------
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
driver.get(URL)
time.sleep(2)  # 首次加载等待

all_products = []  # 存储所有产品信息（字典列表）
seen_ids = set()  # 用于去重（根据产品标题或ID）

for i in range(MAX_SCROLLS):
    print(f"🔄 第 {i + 1} 次滚动...")

    # 1. 抓取当前已加载的产品
    # 根据该网站结构，产品卡片在 <div class="product"> 里
    cards = driver.find_elements(By.CSS_SELECTOR, "div.feed-item")

    for card in cards:
        try:
            author = card.find_element(By.CSS_SELECTOR, "span.DouWeb-SR-author-name").text.strip()
            preview = card.find_element(By.CSS_SELECTOR, "span.DouWeb-SR-article-preview-abstract").text.strip()
        except:
            continue

        # 用标题+价格作为唯一标识（不同网站可调整）
        unique_key = f"{author}_{preview}"
        if unique_key not in seen_ids:
            seen_ids.add(unique_key)
            all_products.append({"author": author, "preview": preview})

    print(f"   当前已采集 {len(all_products)} 个唯一评论")

    # 2. 滚动到底部（触发加载更多）
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE)

    # 可选：检查是否还有新内容加载（比如高度不再变化），可加判断，这里简化

# ---------- 关闭浏览器 ----------
driver.quit()
print(f"\n🎉 共采集 {len(all_products)} 个评论")

# ---------- 存储到 CSV ----------
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["author", "preview"])
    writer.writeheader()
    writer.writerows(all_products)
print(f"✅ 已保存 CSV: {OUTPUT_CSV}")

