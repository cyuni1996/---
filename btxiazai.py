import os,re,socket,time,requests,socks,timeit,tqdm,multiprocessing
from lxml import etree, html
from tqdm import tqdm
import pandas as pd
import logging
import logging.config

class Webbug(object):
    def __init__(self,video_query,video_type,page):
        self.url_data = []
        self.url_list = []
        self.video_data = []
        self.video_query = video_query
        self.video_type = video_type
        self.page = page
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"}
        self.download_path = f'E:\缓存\爬虫图片\{self.video_type}\{self.video_query}'
        self.debuglog_path = os.path.join(self.download_path,'log.txt')
        self.url_data_txt = os.path.join(self.download_path,'data.txt')
        self.url_data_csv = os.path.join(self.download_path,'data.csv')
        self.my_log = os.path.join(self.download_path,'log.txt')
        self.preprocess()
    #运行前预处理
    def preprocess(self):
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        else:
            try:
                os.remove(self.my_log)
                os.remove(self.url_data_csv)
            except FileNotFoundError:
                print(f"删除失败,{self.my_log},{self.url_data_csv}文件不存在")
            print(">>>>>>>>>>>>>>>>>>下载路径已存在<<<<<<<<<<<<<<<<<")
        logging.config.fileConfig('E:\工作\python\代码库\logging.conf',defaults={'logfile': self.debuglog_path})
        socks.set_default_proxy(socks.SOCKS5, "192.168.31.205", 65533)
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
    def save_data(self,path,data): 
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
    # 文件读取
    def read_data(self,path):
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
            # self.Download2(download_url, download_name)
        else:
            logger.info(f"下载成功:{download_name}")
        finally:                                                                                  # 语句结束后必须执行的清理操作
            time.sleep(0.2)    
    def Download2(self, download_url, download_name):
        logger = logging.getLogger("Download2")
        try:
            os.system(f"you-get -o {download_name[:-4]} -O {download_name[:-4]} {download_url}")# 使用you-get命令行工具下载文件
        except Exception as e:
            logger.error(f'下载错误{download_name}: {e}')
#-------------------------------------------------以下代码针对网页修改-------------------------------------------------------------
    # 分析url数据
    def url_analyze(self,Data): 
        logger = logging.getLogger("url_analyze")
        glgz = re.compile(
            r'.*?<table width.*?<a href="thread-index-(?P<url>.*?)"' # 匹配链接
            r'.*?class="subject_link thread.*?title="(?P<name>.*?)"' # 匹配名字
            ,re.S)  
        jx = glgz.finditer(Data)  
        for i in jx:    
            filename = os.path.splitext(i.group("name").strip(""))[0]  # 从 i 中提取文件名，并去掉后缀和空格
            filename = re.sub(r"[\/\]\!\?\s・\xa0]", "", filename)     # 用正则表达式替换掉文件名中的特殊字符
            url = i.group("url")
            url = f"https://www.btbtt16.com/thread-index-{url}"
            dic = {
                "name":i.group("name"),
                "url":url,
            }
            self.url_data.append(dic)
        if self.url_data == []:
            logger.error("没有分析到url数据")
            return "no_url_data"
        else:
            self.url_AnalyzeDatasave(self.url_data_csv,self.url_data)
            logger.info("分析完成已保存数据")
    #分析url_video数据
    def url_analyzevideo(self, data): 
        logger = logging.getLogger("url_analyzevideo")
        glgz = re.compile(
        r'.*?<a href="attach-dialog(?P<video_url>.*?)"' # 匹配链接
        r'.*?height="16" />(?P<name>.*?)</a>' # 匹配名字
        )
        jx = glgz.finditer(data) 
        for i in jx:    
            filename = os.path.splitext(i.group("name").strip(""))[0]  # 从 i 中提取文件名，并去掉后缀和空格
            filename = re.sub(r"[\/\]\!\?\s・\xa0]", "", filename)     # 用正则表达式替换掉文件名中的特殊字符
            video_url = "https://www.btbtt16.com/attach-download" + i.group("video_url")
            dic = {
                "video_name":os.path.join(self.download_path,filename+".torrent"),
                "video_url":video_url,
            }
            self.video_data.append(dic)
        if self.video_data == {}:
            logger.error("没有分析到url数据")
            return "no_url_data"
    # 下载前判断文件是否存在
    def Downloadimage_examine(self, data):
        logger = logging.getLogger("Downloadimage_examine")
        for item in data:
            image_url = (item['video_url'])
            image_name = (item['video_name'])
            if not os.path.isfile(image_name):
                self.Download(image_url,image_name)
            else:
                logger.info('文件存在:'+str(image_name).encode('gbk', errors='replace').decode('gbk'))
    # 获取url_list
    def url_pages(self):
        start = timeit.default_timer()
        logger = logging.getLogger("url_pages")
        logger.info(f"分析链接列表")
        pages = [i for i in range(1, self.page + 1)]
        for i in pages:
            url = f"https://hanime1.me/search?query={self.video_query}&type=&genre={self.video_type}&page={i}"
            logger.info(url)
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
            logger.info(f"{i}")
            self.url_data.clear()
            self.run(i)
            logger.info(f"{i}完成")
        end = timeit.default_timer()
        logger.info(">>>>>>>>>>>>>>>>>>全部爬取完成<<<<<<<<<<<<<<<<<")
        logger.info(f"运行时间: {int(end - start)} 秒")

    def save_urldata(self,data):
        self.save_data(self.url_data_txt,self.url_get(data))

    def test(self):
        start = timeit.default_timer()
        logger = logging.getLogger("test")
        if self.video_query == "动漫":
            self.video_query = "981"
        if self.video_type == "日本":
            self.video_type = "-typeid1-0-typeid2-0-typeid3-0-typeid4-205082"
        # url = f"https://www.btbtt16.com/forum-index-fid-{self.video_query}{self.video_type}.htm"
        url = "https://www.btbtt16.com/thread-index-fid-981-tid-4508536.htm"
        self.url_analyzevideo(self.url_get(url))
        self.Downloadimage_examine(self.video_data)


        end = timeit.default_timer()
        logger.info(f"运行时间: {int(end - start)} 秒") 


if __name__ == "__main__":
    video_query = "动漫"
    video_type = "日本"
    page = 5
    w = Webbug(video_query,video_type,page)
    w.test()

