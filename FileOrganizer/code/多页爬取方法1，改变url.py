"""
多页爬虫实战（翻页处理）
目标：爬取 quotes.toscrape.com 的全部名言（共10页）
核心技能：找到 URL 规律，循环请求
"""

import requests
from bs4 import BeautifulSoup
import csv
import time


def scrape_all_pages():
    all_quotes = []
    base_url = "https://movie.douban.com/top250?start={}&filter="

    print("🚀 开始多页爬取...")

    # 我们不知道总页数，先设一个范围（比如先试10页），或者用 while True 直到没有下一页
    for page_num in range(0,501,25):  # 先爬前10页
        url = base_url.format(page_num)
        print(f"📄 正在抓取第 {page_num//25} 页: {url}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"❌ 第 {page_num//25} 页请求失败: {e}")
            break  # 如果某页失败，就停止

        soup = BeautifulSoup(resp.text, "lxml")

        # 提取当前页的名言
        quote_divs = soup.find_all("div", class_="item")

        # 如果没有抓到任何名言，说明到底了，退出循环
        if not quote_divs:
            print("📭 没有更多数据了，停止爬取。")
            break

        for item in quote_divs:
            text = item.find("span", class_="title").text
            author = item.find("div", class_="bd").text
            all_quotes.append([text, author])

        print(f"   ✅ 第 {page_num//25} 页抓取完成，本页 {len(quote_divs)} 条")

        # 礼貌停顿，避免给服务器压力
        time.sleep(0.5)

    # 保存到 CSV
    if all_quotes:
        filename = "all_quotes.csv"
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["电影名", "导演"])
            writer.writerows(all_quotes)
        print(f"🎉 大功告成！共采集 {len(all_quotes)} 条名言，已保存到 {filename}")
    else:
        print("⚠️ 没有采集到任何数据")


if __name__ == "__main__":
    scrape_all_pages()