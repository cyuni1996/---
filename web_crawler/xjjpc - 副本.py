# -*- coding: utf-8 -*-
import os,re,socket,time,requests,socks,timeit,tqdm,multiprocessing
import logging # 导入 logging 库，用于记录日志
from lxml import etree, html
from tqdm import tqdm
import pandas as pd
import sys
import logging
import logging.config

#get爬取网页 
def url_get(url): 
    logger = logging.getLogger("Url_get")
    try: 
        data = requests.get(url,headers=headers,timeout=(10,15)).text
        return data
    except requests.exceptions.RequestException as e: # 如果发生任何 requests 库中定义的异常，则执行以下代码块
        logger.error("%s 访问报错,请检查url和代理是否正确",e)
        return None
# 保存分析数据
def url_AnalyzeDatasave(Data):
    df = pd.DataFrame(Data)     
    df = df.drop_duplicates()  # 去除重复的行
    if not os.path.exists(url_Data_csv):
        df.to_csv(url_Data_csv, index=False)
    else:
        df.to_csv(url_Data_csv, index=False, mode="a")
# 文件保存
def save_data(path,data): 
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)
# 文件读取
def read_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    return data
# 下载
def Download(download_url,download_name): 
    logger = logging.getLogger("Download")
    try:
        url=requests.get(download_url,headers=headers,timeout=(10,15))
        if os.path.exists(download_name) != True: 
            with open(download_name,'wb') as f:
                f.write(url.content)
                logger.info("下载成功:"+download_name)
                time.sleep(0.1)
                f.close
        time.sleep(0.1)
        #进度条
        progress_bar = tqdm(total=int(url.headers.get('content-length', 0)), unit='kB', unit_scale=True, unit_divisor=1024, desc=download_name, miniters=1, bar_format="{l_bar}{bar:25}{r_bar}")
        with open(download_name, "wb") as f:
            for data in url.iter_content(chunk_size=1024):
                sizi=f.write(data)
                progress_bar.update(sizi)   
    except:
        logger.warning('尝试下载方法2')
        try:
            os.system(f"you-get -o {download_name[:-4]} -O {download_name[:-4]} {download_url}")
        except:
            logger.error('下载错误'+download_name) 
#-------------------------------------------------以下代码针对网页修改-------------------------------------------------------------
# 分析url数据
def url_analyze(Data): 
    logger = logging.getLogger("url_analyze")
    glgz = re.compile(
        r'.*?<a style="text-decoration: none;".*?href="(?P<url>.*?)"' # 匹配链接
        r'.*?<img style="border-radius: 3px".*?src="(?P<image>.*?)"' # 匹配图片链接
        r'.*?<div class="home-rows-videos-title".*?border-radius: 3px">(?P<name>.*?)</div>' # 匹配视频名字
        ,re.S)  
    jx = glgz.finditer(Data)  
    for i in jx:     
        filename = os.path.splitext(i.group("name").strip(""))[0]  # 从 i 中提取文件名，并去掉后缀和空格
        filename = re.sub(r"[\/\]\!\?\s・\xa0]", "", filename)     # 用正则表达式替换掉文件名中的特殊字符
        dic = {
            "name":i.group("name"),
            "image_url":i.group("image"),
            "video_url":i.group("url"),
            "image_name":os.path.join(Download_path, filename + '.jpg'),
            "video_name":os.path.join(Download_path, filename + '.mp4'),
        }
        url_Data.append(dic)
    if url_Data == []:
        logger.error("没有分析到url数据")
        return "no_url_data"
    else:
        url_AnalyzeDatasave(url_Data)
        logger.info("分析完成已保存数据")
#分析url_video数据
def url_analyzevideo(Data,video_name): 
    logger = logging.getLogger("url_analyzevideo")
    videoData = {}   
    glgz = re.compile(
        r'.*?<source src="(?P<video_url>.*?)"' # 匹配链接
        r'.*?size="(?P<sizi>.*?)"> ' # 匹配视频分辨率
        )  
    jx = glgz.finditer(Data)  
    # 使用字典推导式来构造videoData
    videoData = {i.group("sizi"): i.group("video_url") for i in jx}
    if not videoData:
        logger.warning("尝试数据分析2")
        glgz2 = re.compile(
        r'.*?"contentUrl": "(?P<video_url>.*?)"' # 匹配链接
        )
        jx2 = glgz2.finditer(Data) 
        # 使用字典推导式来构造videoData
        videoData = {"720": i.group("video_url") for i in jx2}
    video_url = videoData.get('1080', videoData.get('720', videoData.get('480', videoData.get('320', None))))
    if video_url is not None:
        # 判断视频是否加密
        if '.m3u8' in video_url:
            logger.error("视频数据加密，跳过下载")
            return "no_url_data"
        else:
            video_info = {
                "video_name":video_name,
                "video_url":video_url
            }
            url_videoData.update(video_info)
    else:
        # 使用f-string来格式化日志消息
        logger.error(f"{videoData}没有解析到视频数据")
        return "no_url_data"
# 下载文件前判断文件是否存在
def Downloadimage_examine(url_Data):
    logger = logging.getLogger("Downloadimage_examine")
    for item in url_Data:
        image_url = (item['image_url'])
        image_name = (item['image_name'])
        if not os.path.isfile(image_name):
            Download(image_url,image_name)
        else:
            logger.info('文件存在:'+str(image_name).encode('gbk', errors='replace').decode('gbk'))
# 下载视频前判断文件是否存在        
def Downloadvideo_examine(video_url,video_name):
    logger = logging.getLogger("Downloadvideo_examine")
    if url_analyzevideo(url_get(video_url),video_name) != "no_url_data":
        time.sleep(2)
        Download(url_videoData["video_url"],video_name)
    else:
        logger.error(f"未下载{video_name}视频数据")
# 多页爬取直到爬取结束
def pages_run(pages):
    logger = logging.getLogger("pages_run")
    pages = list(range(1,pages+1))
    for i in pages:
        logger.info(f">>>>>>>>>>>>>>>>>>开始爬取第{i}页<<<<<<<<<<<<<<<<<")
        url = f"https://hanime1.me/search?query={video_shousuo}&type=&genre={video_type}&page={i}"
        url_Data.clear()
        run(url)
        logger.info(f">>>>>>>>>>>>>>>>>>第{i}页完成<<<<<<<<<<<<<<<<<")
    logger.info(">>>>>>>>>>>>>>>>>>爬取完成<<<<<<<<<<<<<<<<<")
# 运行脚本
def run(url):
    logger = logging.getLogger("run")
    start = timeit.default_timer()
    logger.info(">>>>>>>>>>>>>>>>>>开始分析图片文件<<<<<<<<<<<<<<<<<")
    if url_analyze(url_get(url)) != "no_url_data":
        Downloadimage_examine(url_Data)
    else:
        logger.error("没有分析到url数据")
    time.sleep(1)
    logger.info(">>>>>>>>>>>>>>>>>>开始分析视频文件<<<<<<<<<<<<<<<<<")
    for item in url_Data:
        video_url = (item['video_url'])
        video_name = (item['video_name'])
        if not os.path.isfile(video_name):
            time.sleep(5)
            logger.info(video_url)
            Downloadvideo_examine(video_url,video_name)
        else:
            logger.info('文件存在:'+str(video_name).encode('gbk', errors='replace').decode('gbk'))  
        
    end = timeit.default_timer()
    logger.info(f"运行时间: {int(end - start)} 秒")
# 测试脚本
def test(url):
    video_name = "text"
    url = "https://hanime1.me/watch?v=22492"
    Download("https://cdn5-videos.motherlessmedia.com/videos/FD0F927-720p.mp4",Download_path+"text.mp4")

#nur 鈴木みら乃 GOLD BEAR 魔人 PoRO Queen Bee ショーテン ピンクパイナップル メリー・ジェーン Collaboration Works
video_shousuo = "魔人"
video_type = "裏番"
video_page = 5

Download_path = f'E:\缓存\爬虫图片\{video_type}\{video_shousuo}'
url_Data_txt = os.path.join(Download_path,'Data.txt')
url_Data_csv = os.path.join(Download_path,'Data.csv')
my_log = os.path.join(Download_path,'log.txt')

url = f"https://hanime1.me/search?query={video_shousuo}&type=&genre={video_type}&page={video_page}"
# url = f"https://hanime1.me/search?query=&type=&genre={video_type}&tags%5B%5D={video_shousuo}&sort=最新上市&{video_page}"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"} 
url_Data = []
url_videoData= {}
video_txt_info = None

if  __name__=="__main__":
    if not os.path.exists(Download_path):
        os.makedirs(Download_path)
    else:
        try:
            os.remove(my_log)
            os.remove(url_Data_csv)
        except:
            print(f"删除失败,{my_log},{url_Data_csv}文件不存在")
        print(">>>>>>>>>>>>>>>>>>下载路径已存在<<<<<<<<<<<<<<<<<")
    sys.stdout.reconfigure(encoding='utf-8')
    logging.config.fileConfig('E:\工作\python\代码库\logging.conf',defaults={'logfile': my_log})
    socks.set_default_proxy(socks.SOCKS5, "192.168.31.160", 65533)
    socket.socket = socks.socksocket

    # test(url)
    pages_run(video_page)
    


    
