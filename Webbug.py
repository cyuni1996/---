import os,re,socket,time,requests,socks,timeit,tqdm,multiprocessing
from lxml import etree, html
from tqdm import tqdm
import pandas as pd
import logging
import logging.config

class Webbug(object):
    def __init__(self,video_query,video_type,page,vpn):
        self.url_data = []
        self.url_list = []
        self.VPN = vpn
        self.video_data = {}
        self.video_query = video_query
        self.video_type = video_type
        self.page = page
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"}
        self.download_path = f'E:\缓存\爬虫图片\{self.video_type}\{self.video_query}'
        self.debuglog_path = os.path.join(self.download_path,'log.txt').replace("\\","/")
        self.url_data_txt = os.path.join(self.download_path,'data.txt')
        self.url_data_csv = os.path.join(self.download_path,'data.csv')
        self.my_log = os.path.join(self.download_path,'log.txt')
        self.preprocess(vpn)

    #运行前预处理
    def preprocess(self,VPN):
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        else:
            try:
                os.remove(self.my_log)
                os.remove(self.url_data_csv)
            except FileNotFoundError:
                print(f"删除失败,{self.my_log},{self.url_data_csv}文件不存在")
            print(">>>>>>>>>>>>>>>>>>下载路径已存在<<<<<<<<<<<<<<<<<")
        logging.config.fileConfig('F:\work\python\代码库\logconf\logging.conf',defaults={'logfile': self.debuglog_path})
        socks.set_default_proxy(socks.SOCKS5, VPN, 65533)
        socket.socket = socks.socksocket

    #get爬取网页    
    def url_get(self,url): 
        logger = logging.getLogger("Url_get")
        try: 
            data = requests.get(url,headers=self.headers,timeout=(10,15)).text
            return data
        except requests.exceptions.RequestException as e: # 如果发生任何 requests 库中定义的异常，则执行以下代码块
            logger.error("%s \n访问报错,请检查url和代理是否正确",e)
            return "no_url_data"
        
    # 保存分析数据
    def url_AnalyzeDatasave(self,path,Data):
        df = pd.DataFrame(Data)     
        df = df.drop_duplicates()  # 去除重复的行
        if not os.path.exists(path):
            df.to_csv(path, index=False)
        else:
            df.to_csv(path, index=False, mode="a")

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
    def Download(self, download_url, download_name):
        logger = logging.getLogger("Download")
        try:
            url = requests.get(download_url, headers=self.headers, stream=True, timeout=(10, 15)) # 使用stream参数，可以让你一边下载一边写入文件，这样可以节省内存空间，提高效率，避免因为文件过大而导致的内存溢出错误。
            file_size = int(url.headers.get('content-length', 0))                                 # 获取文件大小
            progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, desc=download_name, miniters=1, bar_format="{l_bar}{bar:25}{r_bar}") # 创建进度条
            file_path = os.path.join(download_name[:-4], download_name)                           # 拼接文件路径
            with open(file_path, 'wb') as f:
                for data in url.iter_content(chunk_size=1024):
                    size = f.write(data)
                    progress_bar.update(size)
                progress_bar.close()                                                              # 关闭进度条
        except Exception as e:
            logger.warning(f'{e} \n开始尝试使用下载方法2')
            self.Download2(download_url, download_name)
        else:
            logger.info('下载成功:'+str(download_name).encode('gbk', errors='replace').decode('gbk'))
        finally:                                                                                  # 语句结束后必须执行的清理操作
            time.sleep(0.1)    
    def Download2(self, download_url, download_name):
        logger = logging.getLogger("Download2")
        try:
            os.system(f"you-get -o {download_name[:-4]} -O {download_name[:-4]} {download_url}")# 使用you-get命令行工具下载文件
        except Exception as e:
            logger.error(f'下载错误{download_name}'+str(download_name).encode('gbk', errors='replace').decode('gbk')+': {e}')

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

#-------------------------------------------------以下代码针对网页修改-------------------------------------------------------------