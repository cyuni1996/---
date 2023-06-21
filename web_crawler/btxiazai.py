import os,re,time,timeit
from crawler_code import Webbug as Webbug

class btxiazai(Webbug):
    def __init__(self, video_query, video_type, page ,vpn ,datapath):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"}
        logconf_path = "logconf/logging.conf"
        super().__init__(video_query, video_type, page, headers, logconf_path, vpn, datapath)
        self.video_data = []
        self.url_data = []
        self.url_list = []
#-------------------------------------------------以下代码针对网页修改-------------------------------------------------------------
    # 分析url数据
    def url_analyze(self,Data): 
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
            self.logger.error("没有分析到url数据")
            return "no_url_data"
        else:
            self.url_AnalyzeDatasave(self.url_data_csv,self.url_data)
            self.logger.info("分析完成已保存数据")
    #分析url_video数据
    def url_analyzevideo(self, data): 
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
            self.logger.error("没有分析到url数据")
            return "no_url_data"
    # 下载前判断文件是否存在
    def Downloadimage_examine(self, data):
        for item in data:
            image_url = (item['video_url'])
            image_name = (item['video_name'])
            if not os.path.isfile(image_name):
                self.Download(image_url,image_name)
            else:
                self.logger.info('文件存在:'+str(image_name).encode('gbk', errors='replace').decode('gbk'))
                
    def run(self):
        start = timeit.default_timer()
        if self.video_query == "动漫":
            self.video_query = "981"
        if self.video_type == "日本":
            self.video_type = "-typeid1-0-typeid2-0-typeid3-0-typeid4-205082"
        # url = f"https://www.btbtt16.com/forum-index-fid-{self.video_query}{self.video_type}.htm"
        url = "https://www.btbtt16.com/thread-index-fid-981-tid-4508536.htm"
        self.url_analyzevideo(self.url_get(url))
        self.Downloadimage_examine(self.video_data)


        end = timeit.default_timer()
        self.logger.info(f"运行时间: {int(end - start)} 秒") 

if __name__ == "__main__":
    video_query = "动漫"
    video_type = "日本"
    page = 5
    datapath = "E:\缓存\爬虫图片"
    vpn = "192.168.31.50"
    w = btxiazai(video_query,video_type,page,vpn,datapath)
    w.run()
