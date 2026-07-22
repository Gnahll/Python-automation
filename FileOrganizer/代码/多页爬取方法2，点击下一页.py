"""
智能翻页爬虫（不猜数字，跟着按钮走）
适用于：有“下一页”按钮且HTML里直接带链接的网站
"""

import requests
from bs4 import BeautifulSoup
import time
import csv

def get_page(url):
    """请求并解析一页"""
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    return BeautifulSoup(resp.text, "lxml")


def scrape_all_pages(start_url):
    """递归/循环爬取所有页面，直到没有下一页"""
    current_url = start_url
    page_num = 1
    all_quotes = []

    while current_url:  # 只要还有链接，就一直爬
        print(f"📄 正在抓取第 {page_num} 页: {current_url}")
        soup = get_page(current_url)

        # 1. 抓取当前页的数据
        quotes = soup.find_all("div", class_="quote")
        for item in quotes:
            text = item.find("span", class_="text").text
            author = item.find("small", class_="author").text
            all_quotes.append([text, author])

        print(f"   ✅ 本页抓取 {len(quotes)} 条")

        # 2. 寻找“下一页”按钮的链接
        next_button = soup.find("li", class_="next")
        if next_button:
            next_link = next_button.find("a")["href"]  # 提取 href 属性值
            # 拼接完整地址（因为 href 可能是 /page/2/）
            current_url = f"https://quotes.toscrape.com{next_link}"
            page_num += 1
            time.sleep(0.5)  # 礼貌等待
        else:
            print("🔚 已到达最后一页，停止爬取")
            break  # 没有下一页了，跳出循环

    return all_quotes
def save_data(data, csv_file="quotes.csv", json_file="quotes.json"):
    """将数据保存为 CSV """
    # 保存 CSV
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["名言", "作者"])
        writer.writerows(data)
    print(f"✅ CSV 已保存: {csv_file}")

if __name__ == "__main__":
    data = scrape_all_pages("https://quotes.toscrape.com/")
    print(f"🎉 总共抓取 {len(data)} 条名言")
    save_data(data)