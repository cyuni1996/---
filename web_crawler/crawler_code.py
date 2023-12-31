import os,socket,time,requests,socks,tqdm,re,sys
from tqdm import tqdm
import pandas as pd
import logging
import logging.config

class Webbug(object):
    def __init__(self,video_query,video_type,page,vpn,datapath):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60"}
        self.logconf_path = "../logconf/logging.conf"
        self.vpn = vpn
        self.page = int(page)
        self.datapath = datapath
        self.video_query = video_query
        self.video_type = video_type
        self.download_path = f'{self.datapath}\{self.video_type}\{self.video_query}'
        self.debuglog_path = os.path.normpath(os.path.join(self.download_path,'log.txt')).replace('\\','/')
        self.url_data_txt = os.path.normpath(os.path.join(self.download_path,'data.txt'))
        self.url_data_csv = os.path.normpath(os.path.join(self.download_path,'data.csv'))
        self.preprocess()
    #运行前预处理
    def preprocess(self):
        #pre1:检查日志路径是否存在
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        else:
            if os.path.exists(self.debuglog_path):
                os.remove(self.debuglog_path)
                print('已清理log文件')
            if os.path.exists(self.url_data_csv):
                os.remove(self.url_data_csv)
                print('已清理csv文件')
    
        #pre2:加载日志程序
        if os.path.exists(os.path.abspath(self.logconf_path)): 
            logging.config.fileConfig(self.logconf_path,defaults={'logfile': self.debuglog_path})
            self.logger = logging.getLogger(__name__)
        else:
            print("error:日志配置文件不存在:{}".format(os.path.abspath(self.logconf_path)))
            sys.exit()
            
        #pre3:设置代理
        if self.vpn:
            print(f"已挂载VPN:{self.vpn}")
            socks.set_default_proxy(socks.SOCKS5, self.vpn, 65533)
            socket.socket = socks.socksocket
        else:    
            print("没有设置VPN")

        #pre4:page检查
        if self.page != 1 or self.page:
            self.page = re.findall(r'\d+',str(list(range(1,self.page+1))))
        else:
            print("没有设置页数")

#-----下面是爬取网页的方法--------
    #get爬取网页    
    def url_get(self,url): 
        try: 
            data = requests.get(url,headers=self.headers,timeout=(10,15)).text
            return data
        except requests.exceptions.RequestException as e: # 如果发生任何 requests 库中定义的异常，则执行以下代码块
            self.logger.error("%s \n访问报错,请检查url和代理是否正确",e)
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
    def Download(self, download_url,download_name):
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
            self.logger.warning(f'{e} \n开始尝试使用下载方法2')
            self.Download2(download_url, download_name)
        else:
            self.logger.info('下载成功:'+str(download_name).encode('gbk', errors='replace').decode('gbk'))
        finally:                                                                                  # 语句结束后必须执行的操作
            time.sleep(0.1)    
    def Download2(self, download_url, download_name):
        try:
            os.system(f"you-get -o {download_name[:-4]} -O {download_name[:-4]} {download_url}")# 使用you-get命令行工具下载文件
        except Exception as e:
            self.logger.error(f'下载错误{download_name}'+str(download_name).encode('gbk', errors='replace').decode('gbk')+': {e}')
