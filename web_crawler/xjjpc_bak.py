import multiprocessing,os,re,socket,time,requests,socks,timeit,tqdm
from lxml import etree, html
from tqdm import tqdm
import pandas as pd
import logging
import logging.config

def url_get(url): #get爬取网页 
    try: 
        data = requests.get(url,headers=headers,timeout=(10,15)).text
        return data
    except requests.exceptions.RequestException as e: # 如果发生任何 requests 库中定义的异常，则执行以下代码块
        logging.error("%s 访问报错,请检查url和代理是否正确",e)
        return None

def url_analyze(Data): #分析url数据
    glgz = re.compile(
        r'.*?<img class="image".*?src="(?P<image>.*?)"' # 匹配图片链接
        r'.*?<h5 class="title is-4 is-spaced".*?link="internal">(?P<name>.*?) </a>' # 匹配视频名字
        r'.*?<p class="control is-expanded".*?<a class="button is-primary is-fullwidth".*?href="(?P<torrent>.*?)"' # 匹配种子链接
        ,re.S)  
    jx = glgz.finditer(Data)  
    for i in jx:                                        
        filename = i.group("name").strip()  # 从 i 中提取文件名，去掉空格
        filename = re.sub(r"[^\w\-_\. ]", "", filename)     # 用正则表达式替换掉文件名中的特殊字符
        logger.debug(filename)
        dic={
            "name":filename,
            "image_url":i.group("image"),
            "torrent_url":i.group("torrent"),
            "image_name":os.path.join(download_path, filename + '.jpg'),
            "torrent_name":os.path.join(download_path, filename + '.torrent')
        }
        url_Data.append(dic)
    if url_Data == []:
        return "no_url_data"
    else:
        url_Datasave(url_Data)

def url_Datasave(Data):
    df = pd.DataFrame(Data)
    # 去除重复的行
    df = df.drop_duplicates()
    if not os.path.exists(url_data_csv):
        df.to_csv(url_data_csv, index=False)
    else:
        df.to_csv(url_data_csv, index=False, mode="a")
    
def Download(download_url, download_name):
    try:
        url = requests.get(download_url, headers=headers, stream=True, timeout=(10, 15)) # 使用stream参数，可以让你一边下载一边写入文件，这样可以节省内存空间，提高效率，避免因为文件过大而导致的内存溢出错误。
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
        Download2(download_url, download_name)
    else:
        logger.info('下载成功:'+str(download_name).encode('gbk', errors='replace').decode('gbk'))
    finally:                                                                                  # 语句结束后必须执行的操作
        time.sleep(0.1)    
def Download2(download_url, download_name):
    try:
        os.system(f"you-get -o {download_name[:-4]} -O {download_name[:-4]} {download_url}")# 使用you-get命令行工具下载文件
    except Exception as e:
        logger.error(f'下载错误{download_name}'+str(download_name).encode('gbk', errors='replace').decode('gbk')+': {e}')


def Download_examine(url_Data):
    for item in url_Data:
        image_url = (item['image_url'])
        image_name = (item['image_name'])
        torrent_url = (item['torrent_url'])
        torrent_name = (item['torrent_name'])
        if not os.path.isfile(image_name):
            Download(image_url,image_name)
        else:
            tqdm.write(f"文件存在:{image_name}")
            
        if not os.path.isfile(torrent_name):
            Download(torrent_url,torrent_name)
        else:
            tqdm.write(f"文件存在:{torrent_name}")

def url_pages(pages):
    url = "https://ffjav.com/page/%s?s=%s"%(pages,shousuo)
    if url_analyze(url_get(url)) != "no_url_data":
        Download_examine(url_Data)
        print(f"第{pages}页爬取完成")
    else:
        print(f"第{pages}页爬取失败")
    time.sleep(0.5)
    
def run(number):
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    if os.path.isfile(url_data_csv):
        os.remove(url_data_csv)
    else:
        print(f"无需清理,{url_data_csv}文件不存在")
        
    Pool = multiprocessing.Pool(number)
    Pool.map(url_pages,pages)
    Pool.close()
    Pool.join()





















shousuo = "桃乃木かな"
pages = re.findall(r'\d+',str(list(range(1,20))))
url_Data = []
video_Downloadinfo = []
logconf_path = "../logconf/logging.conf"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.0.0"} 
download_path = f'E:\缓存\爬虫图片\{shousuo}'
url_data_csv = os.path.join(download_path,"Data" + '.csv')
debuglog_path = os.path.join(download_path,'log.txt')
video_txt_info = None
socks.set_default_proxy(socks.SOCKS5, "192.168.31.248", 65533)
socket.socket = socks.socksocket    
logger = logging.getLogger(__name__)

if  __name__=="__main__":
    start = timeit.default_timer()

    if not os.path.isfile(debuglog_path):  
        os.makedirs(download_path) 
    logging.config.fileConfig(logconf_path,defaults={'logfile': debuglog_path})
    run(10)
    end = timeit.default_timer()
    print(f"运行时间: {int(end - start)} 秒")
