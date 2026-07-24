# -*- coding: utf-8 -*-
"""
豆瓣电影 Top250 爬虫
功能：爬取豆瓣电影Top250榜单，提取电影名称、导演、演员、年代、地区、类型、评分、评价人数、一句话点评
依赖：requests, beautifulsoup4
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re


def fetch_page(url, headers):
    """
    获取指定URL的页面HTML内容
    :param url: 目标网页地址
    :param headers: 请求头字典，用于伪装浏览器身份
    :return: 成功返回HTML字符串，失败返回None
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None


def parse_movie_item(item):
    """
    解析单个电影条目，提取电影名称、导演、演员、年代、地区、类型、评分、评价人数、一句话点评
    :param item: BeautifulSoup解析后的单个电影div节点
    :return: 包含所有字段的字典
    """
    # 提取电影名称
    title_tag = item.find("span", class_="title")
    title = title_tag.text.strip() if title_tag else ""

    # 提取评分
    rating_tag = item.find("span", class_="rating_num")
    rating = rating_tag.text.strip() if rating_tag else ""

    # 提取评价人数：在整个 item 内搜索"数字+人评价"
    people = ""
    full_text = item.get_text()
    people_match = re.search(r"(\d+)\s*人评价", full_text)
    if people_match:
        people = people_match.group(1)

    # 提取一句话点评
    quote_tag = item.find("span", class_="inq")
    quote = quote_tag.text.strip() if quote_tag else ""

    # 提取导演、演员、年代、地区、类型——在 bd 区域的第一个 <p> 标签中
    # HTML 结构:
    # <p>
    #     导演: 弗兰克·德拉邦特&nbsp;&nbsp;&nbsp;主演: 蒂姆·罗宾斯 / ...<br>
    #     1994&nbsp;/&nbsp;美国&nbsp;/&nbsp;犯罪 剧情
    # </p>
    director = ""
    actor = ""
    year = ""
    country = ""
    genre = ""
    bd_tag = item.find("div", class_="bd")
    if bd_tag:
        info_p = bd_tag.find("p")
        if info_p:
            # 按 <br> 拆成两行：第1行是导演+主演，第2行是年代/地区/类型
            # get_text() 默认不分隔<br>，需要先拿到完整文本再按\n拆分
            full_text = info_p.get_text("\n", strip=True)
            lines = full_text.split("\n")
            line1 = lines[0].strip() if len(lines) > 0 else ""
            line2 = lines[1].strip() if len(lines) > 1 else ""

            # 第1行: "导演: xxx   主演: xxx"
            # 用连续空格或 &nbsp; 分割导演和主演
            parts_line1 = re.split(r"\s{2,}", line1)
            for part in parts_line1:
                part = part.strip()
                if part.startswith("导演:"):
                    director = part.replace("导演:", "").strip()
                elif part.startswith("主演:"):
                    actor = part.replace("主演:", "").strip()

            # 第2行: "1994 / 美国 / 犯罪 剧情"
            if line2:
                parts_line2 = [p.strip() for p in line2.replace("\xa0", " ").split("/") if p.strip()]
                if parts_line2:
                    # 第一个是年代（4位数字）
                    if re.match(r"^\d{4}$", parts_line2[0]):
                        year = parts_line2[0]
                        parts_line2 = parts_line2[1:]
                    # 接着是地区
                    if parts_line2:
                        country = parts_line2[0]
                        parts_line2 = parts_line2[1:]
                    # 剩下的是类型
                    if parts_line2:
                        genre = " / ".join(parts_line2)

    return {
        "电影名称": title,
        "导演": director,
        "主演": actor,
        "年代": year,
        "地区": country,
        "类型": genre,
        "评分": rating,
        "评价人数": people,
        "一句话点评": quote,
    }


def scrape_douban_top250():
    """
    主爬取逻辑：遍历豆瓣Top250的全部10页，逐页爬取并解析
    :return: 包含所有电影信息的列表
    """
    base_url = "https://movie.douban.com/top250"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7"
        ),
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    }

    all_movies = []

    for page in range(10):
        start = page * 25
        url = f"{base_url}?start={start}&filter="
        print(f"正在爬取第 {page + 1} 页: {url}")

        html = fetch_page(url, headers)
        if html is None:
            print(f"第 {page + 1} 页请求失败，跳过")
            continue

        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("div", class_="item")

        if not items:
            print(f"第 {page + 1} 页未找到电影条目，可能被反爬限制")
            page_title = soup.find("title")
            if page_title:
                print(f"  页面标题: {page_title.text.strip()}")
            continue

        for item in items:
            movie = parse_movie_item(item)
            all_movies.append(movie)

        print(f"第 {page + 1} 页解析完成，共 {len(items)} 条")
        time.sleep(2)

    return all_movies


def save_to_csv(movies, filename="豆瓣电影Top250.csv"):
    """
    将电影数据保存为CSV文件
    :param movies: 电影数据列表
    :param filename: 输出的CSV文件名
    """
    if not movies:
        print("没有数据可保存")
        return

    fieldnames = ["电影名称", "导演", "主演", "年代", "地区", "类型", "评分", "评价人数", "一句话点评"]
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(movies)

    print(f"数据已保存到 {filename}，共 {len(movies)} 条记录")


def main():
    """程序入口"""
    print("=" * 50)
    print("豆瓣电影 Top250 爬虫")
    print("=" * 50)

    movies = scrape_douban_top250()
    save_to_csv(movies)

    print("\n--- 前5条数据预览 ---")
    for i, movie in enumerate(movies[:5], 1):
        print(f"{i}. {movie['电影名称']} | 导演: {movie['导演']} | 评分: {movie['评分']} | 年代: {movie['年代']}")


if __name__ == "__main__":
    main()
