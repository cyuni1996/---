import os,re,socket,time,requests,socks,timeit,tqdm,multiprocessing
from lxml import etree, html
from tqdm import tqdm
import pandas as pd
import logging
import logging.config

class Webbug(object):
    def __init__(self,video_query,video_type,page):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"}
        self.logconf_path = "logconf/logging.conf"
        self.vpn = "192.168.31.160"
        #---------------下面参数勿动-------------
        self.url_data = []
        self.url_list = []
        self.video_data = {}
        self.video_query = video_query
        self.video_type = video_type
        self.page = page
        self.download_path = f'E:\缓存\爬虫图片\{self.video_type}\{self.video_query}'
        self.debuglog_path = os.path.join(self.download_path,'log.txt').replace("\\","/")
        self.url_data_txt = os.path.join(self.download_path,'data.txt')
        self.url_data_csv = os.path.join(self.download_path,'data.csv')
        self.my_log = os.path.join(self.download_path,'log.txt')
        self.preprocess()
    #运行前预处理
    def preprocess(self):
        #pre1:检查下载路径是否存在
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        else:
            try:
                os.remove(self.my_log)
                os.remove(self.url_data_csv)
            except FileNotFoundError:
                print(f"删除失败,{self.my_log},{self.url_data_csv}文件不存在")
            print(">>>>>>>>>>>>>>>>>>下载路径已存在<<<<<<<<<<<<<<<<<")
        #pre2:初始化日志配置
        logging.config.fileConfig(self.logconf_path,defaults={'logfile': self.debuglog_path})
        #pre3:设置代理
        if self.vpn:
            socks.set_default_proxy(socks.SOCKS5, self.vpn, 65533)
            socket.socket = socks.socksocket
        else:    
            print("没有设置VPN")
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
    w = Webbug(video_query,video_type,page)
    w.pages_run()

# f"https://hanime1.me/search?genre={self.video_type}&page={page}"

#  ピンクパイナップル メリー・ジェーン Collaboration Works
    # url = f"https://hanime1.me/search?query={self.video_query}&type=&genre={self.video_type}&page={page}"