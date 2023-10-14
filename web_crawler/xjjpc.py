import os,re,time,timeit,multiprocessing
from crawler_code import Webbug as Webbug


def url_pages(page):
    url = f"https://ffjav.com/page/{page}?s={video_query}"
    print(url)
    if w.url_analyze(w.url_get(url)) != "no_url_data":
        w.Download_examine(w.url_data)
        print(f"第{page}页爬取完成")
    else:
        print(f"第{page}页爬取失败")
    time.sleep(0.5) 

class xjjpc(Webbug):
    def __init__(self, video_query, video_type, page ,vpn ,datapath):
        super().__init__(video_query, video_type, page, vpn, datapath)
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
            filename = i.group("name").strip()  # 从 i 中提取文件名，去掉空格
            filename = re.sub(r"[\/\]\!\?\s・\xa0]", "", filename)     # 用正则表达式替换掉文件名中的特殊字符
            self.logger.debug(filename)                                   
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
  
    def run(self,thread):
        start = timeit.default_timer()
        Pool = multiprocessing.Pool(thread)
        Pool.map(url_pages,w.page)
        Pool.close()
        Pool.join()
        end = timeit.default_timer()
        self.logger.info(f"总运行时间: {int(end - start)} 秒")

video_query = "ba"
video_type = ""
page = 5
datapath = "E:\缓存\爬虫图片"
vp = "192.168.31.160"
if  __name__=="__main__":
    w = xjjpc(video_query,video_type,page,vp,datapath)
    w.run(3)
