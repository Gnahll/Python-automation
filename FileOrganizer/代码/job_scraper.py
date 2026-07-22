"""
招聘信息采集器（练习版）
目标网站：https://realpython.github.io/fake-jobs/
功能：采集岗位名称、公司名、地点，保存为CSV
"""

import requests
from bs4 import BeautifulSoup
import csv
import time

def scrape_jobs():
    print("🚀 开始采集招聘信息...")

    # 1. 发送网络请求（模拟浏览器访问）
    url = "https://realpython.github.io/fake-jobs/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 如果状态码不是200，报错
        print(f"✅ 网页请求成功，状态码：{response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败：{e}")
        return

    # 2. 解析网页（用 BeautifulSoup 把 HTML 变成可搜索的对象）
    soup = BeautifulSoup(response.text, "lxml")

    # 3. 找到所有招聘卡片（通过观察网页，每个工作都在 <div class="card"> 里）
    job_cards = soup.find_all("div", class_="card")
    print(f"📦 共找到 {len(job_cards)} 个职位")

    # 4. 准备保存数据
    jobs = []
    for card in job_cards:
        # 提取标题（岗位名）
        title_element = card.find("h2", class_="title")
        title = title_element.text.strip() if title_element else "无标题"

        # 提取公司
        company_element = card.find("h3", class_="company")
        company = company_element.text.strip() if company_element else "无公司"

        # 提取地点
        location_element = card.find("p", class_="location")
        location = location_element.text.strip() if location_element else "无地点"

        # 存入列表
        jobs.append([title, company, location])
        print(f"   ✅ 抓取：{title} | {company} | {location}")

        # 礼貌一点，暂停0.1秒，防止访问过快
        time.sleep(0.1)

    # 5. 保存为 CSV 文件（客户最喜欢这种格式）
    if jobs:
        filename = "jobs_data.csv"
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["岗位名称", "公司名称", "工作地点"])  # 表头
            writer.writerows(jobs)
        print(f"🎉 采集完成！共 {len(jobs)} 条数据已保存到 {filename}")
        print("📂 你可以在当前文件夹用 Excel 打开该 CSV 文件查看。")
    else:
        print("⚠️ 没有采集到任何数据，请检查网页结构是否变化。")

if __name__ == "__main__":
    scrape_jobs()