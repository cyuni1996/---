import os,re,socket,time,requests,socks,timeit,tqdm,multiprocessing
from lxml import etree, html
from tqdm import tqdm
import pandas as pd
import logging
import logging.config
from web_crawler.web_bug import Webbug as Webbug

class Animepc(Webbug):
    def __init__(self, video_query, video_type, page):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"}
        logconf_path = "logconf/logging.conf"
        vpn = "192.168.31.50"
        datapath = "E:\缓存\爬虫图片"
        super().__init__(video_query, video_type, page, headers, logconf_path, vpn, datapath)
  
#-------------------------------------------------以下代码针对网页修改-------------------------------------------------------------
    # 分析url数据
    def url_analyze(self,Data): 
        logger = logging.getLogger("url_analyze")
        glgz = re.compile(
            r'.*?<a style="text-decoration: none;".*?href="(?P<url>.*?)"' # 匹配链接
            r'.*?<img style="border-radius: 3px".*?src="(?P<image>.*?)"' # 匹配图片链接
            r'.*?<div class="home-rows-videos-title".*?border-radius: 3px">(?P<name>.*?)</div>' # 匹配视频名字
            ,re.S)  
        jx = glgz.finditer(Data)  
        for i in jx:     
            filename = i.group("name").strip()  # 从 i 中提取文件名，去掉空格
            print(filename)
            filename = re.sub(r"[\/\]\!\?\s・\xa0]", "", filename)     # 用正则表达式替换掉文件名中的特殊字符
            dic = {
                "name":i.group("name"),
                "image_url":i.group("image"),
                "video_url":i.group("url"),
                "image_name":os.path.join(self.download_path, filename + '.jpg'),
                "video_name":os.path.join(self.download_path, filename + '.mp4'),
            }
            self.url_data.append(dic)
        if self.url_data == []:
            logger.error("没有分析到url数据")
            return "no_url_data"
        else:
            self.url_AnalyzeDatasave(self.url_data_csv,self.url_data)
            logger.info("分析完成已保存数据")
    #分析url_video数据
    def url_analyzevideo(self, data, video_name): 
        logger = logging.getLogger("url_analyzevideo")
        videodata = {}
        video_info = {}
        glgz = re.compile(
            r'.*?<source src="(?P<video_url>.*?)"' # 匹配链接
            r'.*?size="(?P<sizi>.*?)"> ' # 匹配视频分辨率
            )
        glgz2 = re.compile(
            r'.*?"contentUrl": "(?P<video_url>.*?)"' # 匹配链接
            )   
        glgz3 = re.compile(
            r'.*?<video style=.*?src="(?P<video_url>.*?)"' # 匹配链接
            )
        jx = glgz.finditer(data) 
        videodata = {i.group("sizi"): i.group("video_url") for i in jx}
        time.sleep(3)
        if not videodata:
            logger.warning("尝试数据分析2")
            jx2 = glgz2.finditer(data) 
            videodata = {"720": i.group("video_url") for i in jx2}
        elif not videodata:
            logger.warning("尝试数据分析3")
            jx3 = glgz3.finditer(data) 
            videodata = {"720": i.group("video_url") for i in jx3}

        video_url = videodata.get('1080', videodata.get('720', videodata.get('480', videodata.get('320', None))))
        # 判断视频是否加密
        if video_url is not None:
            if '.m3u8' in video_url:
                logger.error("视频数据加密，跳过下载")
                return "no_url_data"
            else:
                video_info = {
                    "video_name":video_name,
                    "video_url":video_url
                }
                self.video_data.update(video_info)
        else:
            logger.error(f"{videodata}没有解析到视频数据")
            return "no_url_data"
    # 下载图片前判断文件是否存在
    def Downloadimage_examine(self, data):
        logger = logging.getLogger("Downloadimage_examine")
        for item in data:
            image_url = (item['image_url'])
            image_name = (item['image_name'])
            if not os.path.isfile(image_name):
                self.Download(image_url,image_name)
            else:
                logger.info('文件存在:'+str(image_name).encode('gbk', errors='replace').decode('gbk'))
    # 下载视频前判断文件是否存在        
    def Downloadvideo_examine(self, video_url, video_name):
        logger = logging.getLogger("Downloadvideo_examine")
        if self.url_analyzevideo(self.url_get(video_url),video_name) != "no_url_data":
            self.Download(self.video_data["video_url"],video_name)
        else:
            logger.error(f"未下载{str(video_name).encode('gbk', errors='replace').decode('gbk')}视频数据")
    # 获取url_list
    def url_pages(self):
        start = timeit.default_timer()
        logger = logging.getLogger("url_pages")
        logger.info(f"分析链接列表")
        pages = [i for i in range(1, self.page + 1)]
        for i in pages:
            if self.video_query:
                url = f"https://hanime1.me/search?genre={self.video_type}&page={i}"
            else:
                url = f"https://hanime1.me/search?query={self.video_query}&type=&genre={self.video_type}&page={i}"
            logger.info(str(url).encode('gbk', errors='replace').decode('gbk'))
            self.url_list.append(url)
        end = timeit.default_timer()
        logger.info(f"运行时间: {int(end - start)} 秒")
    # 运行脚本
    def run(self,url):
        logger = logging.getLogger("run")
        start = timeit.default_timer()
        logger.info(">>>>>>>>>>>>>>>>>>开始分析图片文件<<<<<<<<<<<<<<<<<")
        if self.url_analyze(self.url_get(url)) != "no_url_data":
            self.Downloadimage_examine(self.url_data)
        else:
            logger.error("没有分析到url数据")
        time.sleep(0.3)
        logger.info(">>>>>>>>>>>>>>>>>>开始分析视频文件<<<<<<<<<<<<<<<<<")
        for item in self.url_data:
            video_url = (item['video_url'])
            video_name = (item['video_name'])
            if not os.path.isfile(video_name):
                logger.info(f'下载链接:{video_url}')
                self.Downloadvideo_examine(video_url,video_name)
            else:
                logger.info('文件存在:'+str(video_name).encode('gbk', errors='replace').decode('gbk'))  

        end = timeit.default_timer()
        logger.info(f"运行时间: {int(end - start)} 秒")   
    # 多页爬取直到爬取结束
    def pages_run(self):
        start = timeit.default_timer()
        logger = logging.getLogger("pages_run")
        self.url_pages()
        for i in self.url_list:
            logger.info(f"页面{str(i).encode('gbk', errors='replace').decode('gbk')}爬取开始")
            self.url_data.clear()
            self.run(i)
            logger.info(f"页面{str(i).encode('gbk', errors='replace').decode('gbk')}爬取完成")
        end = timeit.default_timer()
        logger.info(">>>>>>>>>>>>>>>>>>全部爬取完成<<<<<<<<<<<<<<<<<")
        logger.info(f"运行时间: {int(end - start)} 秒")

if __name__ == "__main__":
    video_query = ""
    video_type = "裏番"
    page = 2
    w = Animepc(video_query,video_type,page)
    w.pages_run()

# f"https://hanime1.me/search?genre={self.video_type}&page={page}"
# url = f"https://hanime1.me/search?query={self.video_query}&type=&genre={self.video_type}&page={page}"