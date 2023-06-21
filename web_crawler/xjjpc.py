import os,re,time,timeit,multiprocessing
from crawler_code import Webbug as Webbug

class xjjpc(Webbug):
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
            r'.*?<img class="image".*?src="(?P<image>.*?)"' # 匹配图片链接
            r'.*?<h5 class="title is-4 is-spaced".*?link="internal">(?P<name>.*?) </a>' # 匹配视频名字
            r'.*?<p class="control is-expanded".*?<a class="button is-primary is-fullwidth".*?href="(?P<torrent>.*?)"' # 匹配种子链接
            ,re.S)  
        jx = glgz.finditer(Data)  
        for i in jx:                                        
            filename = os.path.splitext(i.group("name").strip(""))[0].replace("/", "").replace("]", "")
            dic={
                "name":i.group("name"),
                "image_url":i.group("image"),
                "torrent_url":i.group("torrent"),
                "image_name":os.path.join(self.download_path, filename + '.jpg'),
                "torrent_name":os.path.join(self.download_path, filename + '.torrent')
            }
            self.url_data.append(dic)
        if self.url_data == []:
            self.logger.error("没有分析到url数据")
            return "no_url_data"
        else:
            self.url_AnalyzeDatasave(self,self.url_data)
            self.logger.info("分析完成已保存数据")
        
    def Download_examine(self,Data):
        for item in Data:
            image_url = (item['image_url'])
            image_name = (item['image_name'])
            torrent_url = (item['torrent_url'])
            torrent_name = (item['torrent_name'])
            if not os.path.isfile(image_name):
                self.Download(image_url,image_name)
            else:
                self.logger.info('文件存在:'+str(image_name).encode('gbk', errors='replace').decode('gbk'))
                
            if not os.path.isfile(torrent_name):
                self.Download(torrent_url,torrent_name)
            else:
                self.logger.info('文件存在:'+str(torrent_name).encode('gbk', errors='replace').decode('gbk'))   
    def url_pages(self,page):
        url = f"https://ffjav.com/page/{page}?s={self.video_query}"
        print(url)
        if self.url_analyze(self.url_get(url)) != "no_url_data":
            self.Download_examine(self.url_data)
            print(f"第{page}页爬取完成")
        else:
            print(f"第{page}页爬取失败")
        time.sleep(0.5)   
    def run(self,thread):
        Pool = multiprocessing.Pool(thread)
        Pool.map(self.url_pages,self.page)
        Pool.close()
        Pool.join()
 
if  __name__=="__main__":
    video_query = "test"
    video_type = ""
    page = 5
    datapath = "E:\缓存\爬虫图片"
    vpn = ""
    w = xjjpc(video_query,video_type,page,vpn,datapath)
    w.run(3)
