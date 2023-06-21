import os,socket,time,requests,socks,tqdm
from tqdm import tqdm
import pandas as pd
import logging
import logging.config


#运行前预处理
def preprocess(download_path,my_log,url_data_csv,logconf_path,debuglog_path,vpn):
    #pre1:检查下载路径是否存在
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    else:
        try:
            os.remove(my_log)
            os.remove(url_data_csv)
        except FileNotFoundError:
            print(f"删除失败,{my_log},{url_data_csv}文件不存在")
        print(">>>>>>>>>>>>>>>>>>下载路径已存在<<<<<<<<<<<<<<<<<")
    #pre2:初始化日志配置
    logging.config.fileConfig(logconf_path,defaults={'logfile': debuglog_path})
    #pre3:设置代理
    if vpn:
        print(vpn)
        socks.set_default_proxy(socks.SOCKS5, vpn, 65533)
        socket.socket = socks.socksocket
    else:    
        print("没有设置VPN")
#-----下面是爬取网页的方法--------
#get爬取网页    
def url_get(url): 
    logger = logging.getLogger("Url_get")
    try: 
        data = requests.get(url,headers=headers,timeout=(10,15)).text
        return data
    except requests.exceptions.RequestException as e: # 如果发生任何 requests 库中定义的异常，则执行以下代码块
        logger.error("%s \n访问报错,请检查url和代理是否正确",e)
        return "no_url_data"
# 保存分析数据
def url_AnalyzeDatasave(path,Data):
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
def Download(download_url, download_name):
    logger = logging.getLogger("Download")
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
    finally:                                                                                  # 语句结束后必须执行的清理操作
        time.sleep(0.1)    
def Download2( download_url, download_name):
    logger = logging.getLogger("Download2")
    try:
        os.system(f"you-get -o {download_name[:-4]} -O {download_name[:-4]} {download_url}")# 使用you-get命令行工具下载文件
    except Exception as e:
        logger.error(f'下载错误{download_name}'+str(download_name).encode('gbk', errors='replace').decode('gbk')+': {e}')