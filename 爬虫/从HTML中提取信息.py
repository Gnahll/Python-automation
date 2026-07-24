import requests
from bs4 import BeautifulSoup
import csv

url = 'https://movie.douban.com/top250'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0'
}
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

soup = BeautifulSoup(response.text, 'lxml')

movie_list = []
# 方法1：find_all 提取链接
links = soup.find_all('div', class_='item')
for link in links:
    # 进入容器内部，找到 <a> 和 <img>
    a_tag = link.find('a')
    img_tag = link.find('img')

    href = a_tag.get('href')  # 从 a 标签取链接
    title = img_tag.get('alt')  # 从 img 标签取电影名
    src = img_tag.get('src')  # 从 img 标签取图片地址

    if href and title:
        print(title, '->', href, '| 图片:', src)
        movie_list.append([title, href, src])

# 写入 CSV 文件
with open('douban_top250.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['电影名', '链接', '图片地址'])
    writer.writerows(movie_list)
print(f'已将 {len(movie_list)} 条数据写入 douban_top250.csv')

# # 方法2：提取所有图片的 src
# print('\n--- 提取图片 ---')
# imgs = soup.find_all('img')                    # ✅ 找所有 img 标签
# print(f'静态 HTML 中找到 {len(imgs)} 个 img 标签')
# for img in imgs:
#     src = img.get('src')                       # ✅ 取 src 属性
#     alt = img.get('alt', '无描述')
#     if src:
#         print(f'[{alt}] -> {src}')

