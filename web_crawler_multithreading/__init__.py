import os,socket,time,requests,socks,tqdm
from tqdm import tqdm
import pandas as pd
import logging
import logging.config


def __init__():
    headers = headers
    logconf_path = logconf_path
    vpn = vpn
    datapath = datapath
    video_query = video_query
    video_type = video_type
    page = page
    download_path = f'{datapath}\{video_type}\{video_query}'
    debuglog_path = os.path.join(download_path,'log.txt').replace("\\","/")
    url_data_txt = os.path.join(download_path,'data.txt')
    url_data_csv = os.path.join(download_path,'data.csv')
    my_log = os.path.join(download_path,'log.txt')