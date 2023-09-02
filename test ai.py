import requests
from bs4 import BeautifulSoup
import re

# 定义网页url
url = "https://www.liblibai.com/works/"

# 发送请求，获取源代码
response = requests.get(url)
html = response.text

# 解析网页，找到图片和AI模型的下载链接的标签
soup = BeautifulSoup(html, "lxml")
tags = soup.find_all("div", class_="card")

# 遍历标签，提取出图片和AI模型的下载链接
for tag in tags:
    # 提取图片链接
    img_tag = tag.find("img", class_="card-img-top")
    img_url = img_tag["src"]
    # 提取AI模型下载链接
    model_tag = tag.find("a", class_="btn btn-primary")
    model_url = model_tag["href"]
    # 打印或保存图片和AI模型的下载链接
    print(img_url, model_url)