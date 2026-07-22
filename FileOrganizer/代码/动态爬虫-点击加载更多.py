"""
点击加载更多（Click Load More）爬虫模板
目标：模拟真实用户点击“加载更多”按钮，直到数据全部加载完毕
"""

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv
import json
import os
# ---------- 配置 ----------
URL = "https://movie.douban.com/explore"
OUTPUT_CSV = "products_click.csv"
MAX_CLICKS = 10  # 最大点击次数，防止死循环
CLICK_PAUSE = 2  # 点击后等待加载的时间

# ---------- 启动浏览器 ----------
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
driver.get(URL)

# 显式等待对象（后续复用）
wait = WebDriverWait(driver, 10)

all_products = []
seen_ids = set()
click_count = 0

print("🚀 开始抓取...")

while click_count < MAX_CLICKS:
    # 1. 等待产品卡片加载（每次点击后页面会更新）
    # 这里先等至少一个产品出现，确保页面渲染完成
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li")))
    except TimeoutException:
        print("⚠️ 未检测到产品，可能页面加载失败")
        break

    # 2. 抓取当前页面的所有产品
    cards = driver.find_elements(By.CSS_SELECTOR, "li")
    print(f"📦 当前共 {len(cards)} 个产品卡片（可见）")

    # 提取数据（去重存储）
    for card in cards:
        try:
            title = card.find_element(By.CSS_SELECTOR, "span.drc-subject-info-title-text").text.strip()
            author = card.find_element(By.CSS_SELECTOR, "div.drc-subject-info-subtitle").text.strip()
        except:
            continue

        unique_key = f"{title}_{author}"
        if unique_key not in seen_ids:
            seen_ids.add(unique_key)
            all_products.append({"title": title, "author": author})

    print(f"✅ 已采集 {len(all_products)} 个唯一产品")
    click_count += 1

    # 3. 查找“加载更多”按钮并点击
    try:
        # 注意：网站按钮文本可能是 "Load More" 或 "加载更多"，这里是英文
        # 方法：通过 XPath 查找文本包含 "Load More" 的按钮
        load_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '加载更多')]")))
        load_btn.click()
        print(f"🖱️ 第 {click_count} 次点击 'Load More'")
        time.sleep(CLICK_PAUSE)  # 等待新数据加载

        # 可选：滚动到按钮位置确保它在可视区（有些网站需要）
        # driver.execute_script("arguments[0].scrollIntoView();", load_btn)

    except TimeoutException:
        # 如果超时找不到按钮，说明“加载更多”可能已经不可用（全部加载完了）
        print("🔚 未找到可点击的 'Load More' 按钮，已加载全部内容。")
        break
    except NoSuchElementException:
        print("🔚 按钮元素不存在，已到达底部。")
        break
    except Exception as e:
        print(f"⚠️ 点击异常: {e}")
        break

# ---------- 关闭浏览器 ----------
driver.quit()

print(f"\n🎉 采集结束！共 {len(all_products)} 条数据")

# 存储到 CSV
with open("D:\\Python自动化\\FileOrganizer\\数据文件\\products_click.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "author"])
    writer.writeheader()
    writer.writerows(all_products)
print(f"✅ 已保存 CSV: {OUTPUT_CSV}")

