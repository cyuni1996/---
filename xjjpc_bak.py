import json,multiprocessing,os,re,socket,time,requests,socks,timeit,tqdm,threading
import logging # 导入 logging 库，用于记录日志
from lxml import etree, html
from tqdm import tqdm
import pandas as pd
import datetime


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
        filename = os.path.splitext(i.group("name").strip(""))[0].replace("/", "").replace("]", "")
        dic={
            "name":i.group("name"),
            "image_url":i.group("image"),
            "torrent_url":i.group("torrent"),
            "image_name":os.path.join(Download_path, filename + '.jpg'),
            "torrent_name":os.path.join(Download_path, filename + '.torrent')
        }
        url_Data.append(dic)
    if url_Data == []:
        logging.error("没有分析到url数据")
        return "no_url_data"
    else:
        url_Datasave(url_Data)

def url_Datasave(Data):
    df = pd.DataFrame(Data)
    # 去除重复的行
    df = df.drop_duplicates()
    if not os.path.exists(scv_path):
        df.to_csv(scv_path, index=False)
    else:
        df.to_csv(scv_path, index=False, mode="a")
    
def Download(download_url,download_name): # 下载
    url=requests.get(download_url,headers=headers,timeout=(10,15))
    time.sleep(0.1)
    try:
        progress_bar = tqdm(total=int(url.headers.get('content-length', 0)), unit_scale=True ,desc=download_name, miniters=1, bar_format="{l_bar}{bar:25}{r_bar}")
        with open(download_name, "wb") as f:
            for data in url.iter_content(chunk_size=1024):
                sizi=f.write(data)
                progress_bar.update(sizi)     
    except requests.exceptions.RequestException as e:
        logging.error('下载错误'+download_name,e)   

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
    if not os.path.exists(Download_path):
        os.makedirs(Download_path)
    else:
        try:
            os.remove(scv_path)
        except:
            print("scv删除失败,文件不存在")
        print(">>>>>>>>>>>>>>>>>>下载路径存在<<<<<<<<<<<<<<<<<")
    Pool = multiprocessing.Pool(number)
    Pool.map(url_pages,pages)
    Pool.close()
    Pool.join()


shousuo = "八掛うみ"
pages = re.findall(r'\d+',str(list(range(1,20))))
url_Data = []
video_Downloadinfo = []
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.0.0"} 
Download_path = f'E:\缓存\爬虫图片\{shousuo}'
scv_path = os.path.join(Download_path,"Data" + '.csv')
video_txt_info = None
socks.set_default_proxy(socks.SOCKS5, "192.168.31.50", 65533)
socket.socket = socks.socksocket    
if  __name__=="__main__":
    start = timeit.default_timer()
    run(10)
    end = timeit.default_timer()
    print(f"运行时间: {int(end - start)} 秒")

    
