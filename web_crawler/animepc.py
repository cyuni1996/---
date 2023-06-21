import os,re,time,timeit,multiprocessing
from crawler_code import Webbug as Webbug

class Animepc(Webbug):
    def __init__(self, video_query, video_type, page ,vpn ,datapath):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"}
        logconf_path = "logconf/logging.conf"
        super().__init__(video_query, video_type, page, headers, logconf_path, vpn, datapath)
        self.video_data = {}
        self.url_data = []
        self.url_list = []
#-------------------------------------------------以下代码针对网页修改-------------------------------------------------------------
    # 分析url数据
    def url_analyze(self,Data): 
        glgz = re.compile(
            r'.*?<a style="text-decoration: none;".*?href="(?P<url>.*?)"' # 匹配链接
            r'.*?<img style="border-radius: 3px".*?src="(?P<image>.*?)"' # 匹配图片链接
            r'.*?<div class="home-rows-videos-title".*?border-radius: 3px">(?P<name>.*?)</div>' # 匹配视频名字
            ,re.S)  
        jx = glgz.finditer(Data)  
        for i in jx:     
            filename = i.group("name").strip()  # 从 i 中提取文件名，去掉空格
            self.logger.debug(filename)
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
            self.logger.error("没有分析到url数据")
            return "no_url_data"
        else:
            self.url_AnalyzeDatasave(self.url_data_csv,self.url_data)
            self.logger.info("分析完成已保存数据")
    #分析url_video数据
    def url_analyzevideo(self, data, video_name): 
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
        videodata = {i.group("sizi"): i.group("video_url") for i in glgz.finditer(data)}
        time.sleep(1)
        if not videodata:
            self.logger.warning("尝试数据分析2") 
            videodata = {"720": i.group("video_url") for i in glgz2.finditer(data)}
        elif not videodata:
            self.logger.warning("尝试数据分析3")
            videodata = {"720": i.group("video_url") for i in glgz3.finditer(data)}
        video_url = videodata.get('1080', videodata.get('720', videodata.get('480', videodata.get('320', None))))
        # 判断视频是否加密
        if video_url is not None:
            if '.m3u8' in video_url:
                self.logger.error("视频数据加密，跳过下载")
                return "no_url_data"
            else:
                video_info = {
                    "video_name":video_name,
                    "video_url":video_url
                }
                self.video_data.update(video_info)
        else:
            self.logger.error(f"{videodata}没有解析到视频数据")
            return "no_url_data"
    # 下载图片前判断文件是否存在
    def Downloadimage_examine(self, data):
        for item in data:
            image_url = (item['image_url'])
            image_name = (item['image_name'])
            if not os.path.isfile(image_name):
                self.Download(image_url,image_name)
            else:
                self.logger.info('文件存在:'+str(image_name).encode('gbk', errors='replace').decode('gbk'))
    # 下载视频前判断文件是否存在        
    def Downloadvideo_examine(self, video_url, video_name):
        if self.url_analyzevideo(self.url_get(video_url),video_name) != "no_url_data":
            self.Download(self.video_data["video_url"],video_name)
        else:
            self.logger.error(f"未下载{str(video_name).encode('gbk', errors='replace').decode('gbk')}视频数据")

    # 获取url_list
    def url_page(self):
        self.logger.info(f"分析链接列表")
        for i in self.page:
            if self.video_query:
                url = f"https://hanime1.me/search?genre={self.video_type}&page={i}"
            else:
                url = f"https://hanime1.me/search?query={self.video_query}&type=&genre={self.video_type}&page={i}"
            self.logger.info(str(url).encode('gbk', errors='replace').decode('gbk'))
            self.url_list.append(url)
        self.logger.info(f"列表分析完成")
    # 单页爬取流程
    def url_run(self,url):
        start = timeit.default_timer()
        self.logger.info(">>>>>>>>>>>>>>>>>>开始分析图片文件<<<<<<<<<<<<<<<<<")
        if self.url_analyze(self.url_get(url)) != "no_url_data":
            self.Downloadimage_examine(self.url_data)
        else:
            self.logger.error("没有分析到url数据")
        time.sleep(0.3)
        self.logger.info(">>>>>>>>>>>>>>>>>>开始分析视频文件<<<<<<<<<<<<<<<<<")
        for item in self.url_data:
            video_url = (item['video_url'])
            video_name = (item['video_name'])
            if not os.path.isfile(video_name):
                self.logger.info(f'下载链接:{video_url}')
                self.Downloadvideo_examine(video_url,video_name)
            else:
                self.logger.info('文件存在:'+str(video_name).encode('gbk', errors='replace').decode('gbk'))  
        end = timeit.default_timer()
        self.logger.info(f"运行时间: {int(end - start)} 秒")   
    # 多页爬取直到爬取结束     
    def pages_run(self):
        start = timeit.default_timer()
        self.url_page()
        for i in self.url_list:
            self.logger.info(f"{str(i).encode('gbk', errors='replace').decode('gbk')} 爬取开始")
            self.url_data.clear()
            self.url_run(i)
            self.logger.info(f"{str(i).encode('gbk', errors='replace').decode('gbk')} 爬取完成")
        end = timeit.default_timer()
        self.logger.info(">>>>>>>>>>>>>>>>>>全部爬取完成<<<<<<<<<<<<<<<<<")
        self.logger.info(f"运行时间: {int(end - start)} 秒")

    def duoxianc(self,page):
        url = f"https://hanime1.me/search?genre={self.video_type}&page={page}"
        self.logger.info(f"{str(url).encode('gbk', errors='replace').decode('gbk')} 爬取开始")
        self.url_run(url)
        self.logger.info(f"{str(url).encode('gbk', errors='replace').decode('gbk')} 爬取完成")
        time.sleep(2)

    def run(self,thread):
        start = timeit.default_timer()
        Pool = multiprocessing.Pool(thread)
        Pool.map(self.duoxianc,self.page)
        Pool.close()
        Pool.join()
        self.logger.info(">>>>>>>>>>>>>>>>>>全部爬取完成<<<<<<<<<<<<<<<<<")
        end = timeit.default_timer()
        self.logger.info(f"运行时间: {int(end - start)} 秒")

if __name__ == "__main__":
    video_query = ""
    video_type = "裏番"
    page = 3
    datapath = "E:\缓存\爬虫图片"
    vpn = ""
    w = Animepc(video_query,video_type,page,vpn,datapath)
    #w.pages_run()
    w.run(5)

# f"https://hanime1.me/search?genre={self.video_type}&page={page}"
# url = f"https://hanime1.me/search?query={self.video_query}&type=&genre={self.video_type}&page={page}"