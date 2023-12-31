import os,re,time,requests,timeit,sys
from tqdm import tqdm
from crawler_code import Webbug as Webbug
from concurrent.futures import ThreadPoolExecutor,as_completed

# 下载
# def Download(download):


#     try:
#         url = requests.get(download_url, headers=w.headers, stream=True, timeout=(10, 15)) # 使用stream参数，可以让你一边下载一边写入文件，这样可以节省内存空间，提高效率，避免因为文件过大而导致的内存溢出错误。
#         file_size = int(url.headers.get('content-length', 0))                                 # 获取文件大小
#         progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, desc=download_name, miniters=1, bar_format="{l_bar}{bar:25}{r_bar}") # 创建进度条
#         file_path = os.path.join(download_name[:-4], download_name)                           # 拼接文件路径
#         with open(file_path, 'wb') as f:
#             for data in url.iter_content(chunk_size=1024):
#                 size = f.write(data)
#                 progress_bar.update(size)
#             progress_bar.close()                                                              # 关闭进度条
#     except Exception as e:
#         w.logger.info(f'{e} \n开始尝试使用下载方法2')
#         Download2(download_url, download_name)
#     else:
#         w.logger.info('下载成功:'+str(download_name).encode('gbk', errors='replace').decode('gbk'))
#     finally:                                                                                  # 语句结束后必须执行的操作
#         time.sleep(0.2)

# def Download2(download_url, download_name):
#     try:
#         os.system(f"you-get -o {download_name[:-4]} -O {download_name[:-4]} {download_url}")# 使用you-get命令行工具下载文件
#     except Exception as e:
#         w.logger.error(f'下载错误{download_name}'+str(download_name).encode('gbk', errors='replace').decode('gbk')+': {e}')

class Animepc(Webbug):
    def __init__(self, video_query, video_type, page, vpn, datapath):
        super().__init__(video_query, video_type, page, vpn, datapath)
        self.url_list = []
        self.Downloadimagelink = []
        self.Downloadvideolink = []
#-------------------------------------------------以下代码针对网页修改-------------------------------------------------------------
    # 分析链接列出url_list
    def url_page(self):
        self.logger.info(f"分析链接列表")
        for i in self.page:
            url = f"https://hanime1.me/search?query={self.video_query}&type=&genre={self.video_type}&page={i}"
            self.logger.info(str(url).encode('gbk', errors='replace').decode('gbk'))
            self.url_list.append(url)
        self.logger.info(f"列表分析完成")

    # 分析url数据
    def url_analyze(self,Data): 
        url_data = []
        if video_type == "裏番":
            glgz = re.compile(
                r'.*?<a style="text-decoration: none;".*?href="(?P<url>.*?)"' # 匹配链接
                r'.*?<img style=".*?border-radius: 3px".*?src="(?P<image>.*?)"' # 匹配图片链接
                r'.*?<div class="home-rows-videos-title".*?border-radius: 3px">(?P<name>.*?)</div>' # 匹配视频名字
                ,re.S)  
        else:
            glgz = re.compile(
                r'.*?<div class="col-xs-6.*?<a class="overlay".*?href="(?P<url>.*?)"></a>' # 匹配链接
                r'.*?<img style=".*?3px" src="(?P<image>.*?)"' # 匹配图片链接
                r'.*?<div class="card-mobile-title" style="font-weight.*?>(?P<name>.*?)</div>' # 匹配视频名字
                ,re.S)  
            
        jx = glgz.finditer(Data)  
        for i in jx:     
            filename = i.group("name").strip()  # 从 i 中提取文件名，去掉空格
            filename = re.sub(r"[\/\]\!\?\s・\xa0():]", "", filename)     # 用正则表达式替换掉文件名中的特殊字符
            self.logger.debug(filename)
            dic = {
                "name":filename,
                "image_url":i.group("image"),
                "video_url":i.group("url"),
                "image_name":os.path.join(self.download_path, filename + '.jpg'),
                "video_name":os.path.join(self.download_path, filename + '.mp4'),
            }
            url_data.append(dic)
        if url_data == []:
            self.logger.error("没有分析到url数据")
            return "no_url_data"
        else:
            self.url_AnalyzeDatasave(self.url_data_csv,url_data)
            return url_data

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

        time.sleep(0.1)
        if not videodata:
            videodata = {"720": i.group("video_url") for i in glgz2.finditer(data)}
        elif not videodata:
            videodata = {"720": i.group("video_url") for i in glgz3.finditer(data)}
        video_url = videodata.get('1080', videodata.get('720', videodata.get('480', videodata.get('320', None))))
        
        # 判断视频是否加密
        if video_url is not None:
            if '.m3u8' in video_url:
                self.logger.error(f"{video_name}----视频为.m3u8,无法下载")
                return "no_url_data"
            else:
                video_info = {
                    "video_name":video_name,
                    "video_url":video_url
                }
                self.Downloadvideolink.append(video_info)
        else:
            self.logger.error(f"{video_name}----没有解析到视频数据")
            return "no_url_data"
        
    # 单页爬取流程
    def url_run(self,url):
        start = timeit.default_timer()
        url_data = self.url_analyze(self.url_get(url))
        if url_data != "no_url_data":
            # 下载图片前判断图片是否存在
            self.logger.info(">>>>>>>>>>>>>>>>>>开始分析图片文件<<<<<<<<<<<<<<<<<")
            for item in url_data:
                image_url = (item['image_url'])
                image_name = (item['image_name'])
                if not os.path.isfile(image_name):
                    self.Downloadimagelink.append({"image_url":image_url,"image_name":image_name})
                    self.logger.info('未下载文件:'+str(image_name).encode('gbk', errors='replace').decode('gbk'))
            self.logger.debug(f"分析到{len(self.Downloadimagelink)}张需下载的图片")

            # 下载图片前判断视频是否存在
            self.logger.info(">>>>>>>>>>>>>>>>>>开始分析视频文件<<<<<<<<<<<<<<<<<")
            for item in url_data:
                video_url = (item['video_url'])
                video_name = (item['video_name'])
                if not os.path.isfile(video_name):
                    if self.url_analyzevideo(self.url_get(video_url),video_name) != "no_url_data":
                        self.logger.info('未下载文件:'+str(video_name).encode('gbk', errors='replace').decode('gbk'))
            self.logger.debug(f"分析到{len(self.Downloadvideolink)}个需下载的视频")

        end = timeit.default_timer()
        self.logger.info(f"运行时间: {int(end - start)} 秒")  

    # 运行网页爬取     
    def run(self,number):
        start = timeit.default_timer()
        self.url_page()
        # 爬取网页
        with ThreadPoolExecutor(max_workers = number) as pool:
            for i in self.url_list:
                self.logger.info(f"{str(i).encode('gbk', errors='replace').decode('gbk')} 爬取开始")
                pool.submit(self.url_run, i)
                
                self.logger.info(f"{str(i).encode('gbk', errors='replace').decode('gbk')} 爬取完成")
        
        # 下载
        if self.Downloadimagelink or self.Downloadvideolink:
            task_log = []
            with ThreadPoolExecutor(max_workers = number) as pool:
                if self.Downloadimagelink:
                    self.logger.info(">>>>>>>>>>>>>>>>>>开始下载图片<<<<<<<<<<<<<<<<<")
                    for cmd in self.Downloadimagelink:
                        download_url = cmd["image_url"]
                        download_name = cmd["image_name"]
                        task = pool.submit(self.Download, download_url,download_name)
                        task_log.append(task)
                    for future in as_completed(task_log):
                        future.result()
                if self.Downloadvideolink:
                    self.logger.info(">>>>>>>>>>>>>>>>>>开始下载视频<<<<<<<<<<<<<<<<<")
                    for cmd in self.Downloadvideolink:
                        download_url = cmd["video_url"]
                        download_name = cmd["video_name"]
                        task = pool.submit(self.Download, download_url,download_name)
                        task_log.append(task)
                    for future in as_completed(task_log):
                        future.result()
                self.logger.info(">>>>>>>>>>>>>>>>>>全部下载完成<<<<<<<<<<<<<<<<<")
        else:
            self.logger.debug("没有可下载的数据")

        end = timeit.default_timer()
        self.logger.info(f"总运行时间: {int(end - start)} 秒")

if __name__ == "__main__":
    datapath = "E:\缓存\爬虫图片"
    video_query = ""
    video_type = "裏番"
    page = 2
    vpn = "192.168.31.248"
    w = Animepc(video_query, video_type, page, vpn, datapath)
   
    # w = Animepc(sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[5],sys.argv[4])
    w.run(5)
