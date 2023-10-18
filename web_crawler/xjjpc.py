import os,re,time,requests,timeit,sys
from tqdm import tqdm
from crawler_code import Webbug as Webbug
from concurrent.futures import ThreadPoolExecutor,as_completed



class xjjpc(Webbug):
    def __init__(self, video_query, video_type, page ,vpn ,datapath):
        super().__init__(video_query, video_type, page, vpn, datapath)
        self.video_data = {}
        self.url_list = []
#-------------------------------------------------以下代码针对网页修改-------------------------------------------------------------
    # 分析链接列出url_list
    def url_page(self):
        url = f"https://ffjav.com/torrent/tag/{self.video_query}"
        glgz = r'.*?<li><a href="https://ffjav.com/.*?data-wpel-link="internal">(\d+)'
        page_list = re.findall(glgz, self.url_get(url))
        if isinstance(page_list, list) and page_list:
            self.logger.info(f"分析到{len(page_list)}页")
            if len(page_list) == 5:
                page_list = [str(i) for i in range(1, int(page_list[4]) + 10)]
                print(page_list)
                
            for i in page_list:
                url = f"https://ffjav.com/page/{i}?s={self.video_query}"
                self.logger.info(str(url).encode('gbk', errors='replace').decode('gbk'))
                self.url_list.append(url)
            self.logger.info(f"列表分析完成")
        else:
            self.url_list.append(url)

    # 分析url数据
    def url_analyze(self,Data):
        url_data = []
        glgz = re.compile(
            r'.*?<img class="image".*?src="(?P<image>.*?)"' # 匹配图片链接
            r'.*?<h5 class="title is-4 is-spaced".*?link="internal">(?P<name>.*?) </a>' # 匹配视频名字
            r'.*?<p class="control is-expanded".*?<a class="button is-primary is-fullwidth".*?href="(?P<torrent>.*?)"' # 匹配种子链接
            ,re.S)  
        
        jx = glgz.finditer(Data)  
        for i in jx:     
            filename = i.group("name").strip()  # 从 i 中提取文件名，去掉空格
            filename = re.sub(r"[^\w\-_\. ]", "", filename)     # 用正则表达式替换掉文件名中的特殊字符
            dic = {
                "name":filename,
                "image_url":i.group("image"),
                "torrent_url":i.group("torrent"),
                "image_name":os.path.join(self.download_path, filename + '.jpg'),
                "torrent_name":os.path.join(self.download_path, filename + '.torrent'),
            }
            url_data.append(dic)
        if url_data == []:
            return "no_url_data"
        else:
            self.url_AnalyzeDatasave(self.url_data_csv,url_data)
            self.logger.info("分析完成已保存数据")
            return url_data

    def Download_examine(self,Data):
        for item in Data:
            image_url = item["image_url"]
            image_name = item["image_name"]
            torrent_url = item['torrent_url']
            torrent_name = item['torrent_name']
            if not os.path.isfile(image_name):
                self.Download(image_url,image_name)
            else:
                self.logger.info('文件存在:'+str(image_name).encode('gbk', errors='replace').decode('gbk'))
                
            if not os.path.isfile(torrent_name):
                self.Download(torrent_url,torrent_name)
            else:
                self.logger.info('文件存在:'+str(torrent_name).encode('gbk', errors='replace').decode('gbk'))
        
    # 单页爬取流程
    def url_run(self,url):
        time.sleep(0.2)
        url_data = self.url_analyze(self.url_get(url))
        if url_data != "no_url_data":
            self.Download_examine(url_data)
            self.logger.info(f"第{url}页爬取完成")
        else:
            self.logger.error(f"第{url}页爬取失败")

    def run(self,nuber):
        self.url_page()
        start = timeit.default_timer()
        with ThreadPoolExecutor(max_workers = nuber) as pool:
            for i in self.url_list:
                pool.submit(self.url_run, i)
        end = timeit.default_timer()
        self.logger.info(f"运行时间: {int(end - start)} 秒")  

if  __name__=="__main__":
    video_query = "月雲よる"
    video_type = ""
    page = 1
    datapath = "E:\缓存\爬虫图片"
    vp = "192.168.31.248"
    w = xjjpc(video_query,video_type,page,vp,datapath)
    w.run(10)
