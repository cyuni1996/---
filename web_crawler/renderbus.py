import json
import os
import re
from pprint import pprint

import requests


class renderbus(object):
    def __init__(self,taskId):
        self.Data = {"taskId":int(taskId)}
        self.PreTask = {}
        self.analyseTask = {}
        self.url_Data = None
        self.TaskFrameRenderList_Data = []
        self.renderbus_api = "https://admin.renderbus.com/api/"
        #获取全局信息
        self.getGlobalSearchList_url = os.path.join(self.renderbus_api,"rendering/admin/task/common/getGlobalSearchList")
        #获取task
        url2 = "https://admin.renderbus.com/api/rendering/admin/task/rendering/loadingTaskParameter"
        #获取task.json
        url_getTaskJson = "https://admin.renderbus.com/api/rendering/admin/task/rendering/getTaskJson"

        self.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        "x-auth-token": "8d4aefee-62b2-4411-be8b-02c206acbc3d",
        "signature": "rayvision2017",
        "platform": "10",
        "version": "1.0.0",
        "content-type": "application/json",
        } 

        #获取任务节点信息
        #请求需要 taskId 并且headers里"platform"的信息正确才能获取
        self.TaskFrameRenderList = {
            "url":"https://admin.renderbus.com/api/rendering/admin/task/rendering/getTaskFrameRenderList",
            "request_data":{
            # pageNum设置页数
            # pageSize每页显示多少信息
            # frameType：4 设置优先帧
            # statusList设置筛选类型 (1:等待帧 2:渲染帧 4：完成帧 5：失败帧 11：超时停止)
            "pageNum": 1,
            "pageSize": 50,
            "taskId": str(self.Data["taskId"]),
            "statusList": [4]
            }
        }
        
        #获取渲染日志
        #请求需要给 id userid renderingType 这三个参数信息才能查询具体的任务信息
        self.rendering_showLog = {
            "url":"https://admin.renderbus.com/api/rendering/admin/task/rendering/showLog",
            "request_data":
            {
            "id": 2490201541,
            "userId": 100000767,
            "renderingType": "debug",
            "pageSize": 6000000,
            "pageNum": 0,
            }
        }

        #获取预处理日志
        self.rendering_pre_showLog = {
            "url":"https://admin.renderbus.com/api/rendering/admin/task/pre/showLog",
            "request_data":
            {
            "id": 2490201541,
            "userId": 100000767,
            "renderingType": "debug",
            "pageSize": 6000000,
            "pageNum": 0,
            }
        }

        #获取分析日志
        self.rendering_analyse_showLog = {
            "url":"https://admin.renderbus.com/api/rendering/admin/task/analyse/getAnalyseLog",
            "request_data":
            {
            "taskId": str(self.Data["taskId"]),
            "logType": 0,
            "pageSize": 6000000,
            "pageNum": 0
            }
        }

    def analysis_GlobalSearchList(self,url_data):
        #预处理参数获取
        glgz = re.compile(
            r'.*?"respGlobelPreTask":.*?"taskId":(?P<taskId>.*?),' 
            r'.*?"userId":(?P<userId>.*?),' 
            r'.*?"platform":(?P<platform>.*?),' 
            ,re.S)  
        jx = glgz.finditer(url_data)  
        for i in jx:  
            PreTask={
            "id":int(i.group("taskId")),
            "userId":int(i.group("userId"))
            }
            self.headers['platform'] = str(i.group("platform"))
            self.PreTask.update(PreTask)

        #参数为空判断
        if self.PreTask == {}:
            print("未拾取到预处理参数")
        else:
            self.rendering_pre_showLog["request_data"]["id"] = self.PreTask["id"]
            self.rendering_pre_showLog["request_data"]["userId"] = self.PreTask["userId"]
            print(self.PreTask)

    def analysis_TaskFrameRenderList(self,url_data):
        glgz = re.compile(
            r'.*?"averageCpu":(?P<averageCpu>.*?),' 
            r'.*?"avgMemory":(?P<avgMemory>.*?),' 
            r'.*?"id":(?P<id>.*?),' 
            r'.*?"userId":(?P<userId>.*?),' 
            r'.*?"nodeIp":(?P<nodeIp>.*?),' 
            r'.*?"frameExecuteTime":(?P<frameExecuteTime>.*?),' 
            r'.*?"currentRenderTime":(?P<currentRenderTime>.*?),' 
            ,re.S)  
        jx = glgz.finditer(url_data)  
        for i in jx:  
            data={
            # average   Cpu平均值
            # avgMemory  内存峰值
            # nodeIp       节点机
            "id":int(i.group("id")),
            "averageCpu":int(i.group("averageCpu")),
            "avgMemory":str(i.group("avgMemory")).replace('"',''),
            "nodeIp":str(i.group("nodeIp")).replace('"',''),
            "frameExecuteTime": i.group("frameExecuteTime"),
            "currentRenderTime": i.group("currentRenderTime"),
            }

            self.Data.update({"userId":int(i.group("userId"))})
            self.rendering_showLog["request_data"]["userId"] = int(i.group("userId"))
            self.TaskFrameRenderList_Data.append(data)

    def analysis_rendering_showLog(self,url_data):

        pass

    #post请求
    def post_qinqiu(self,url,request_data):
        data=json.dumps(request_data)
        self.url_Data = requests.post(url,headers=self.headers,data=data,timeout=(10,15)).text
        if self.url_Data.find('"code":200') != -1:
            print(self.url_Data.replace('\\','/').replace('//','\\').replace('/r/r','\n').replace('/r','\n').replace('","','').replace(' ',''))
        else:
            print(self.url_Data)
            print("请求错误,检查haders和请求数据是否正常")
        
    # 爬取headers
    def get_headers(self,url):
        url=requests.post(url=url,headers=self.headers,timeout=(10,15))
        #响应标头
        response = url.headers.get
        #请求标头
        request = url.request.headers.get
        print(request)

    #爬取任务ID的全局信息
    def get_SearchList(self):

        print("--------------------爬取全局信息中--------------------")
        self.post_qinqiu(self.getGlobalSearchList_url,self.Data)
        self.analysis_GlobalSearchList(self.url_Data)
        print(self.Data)
        print("--------------------爬取完成--------------------")

    #爬取任务帧渲染列表
    def get_TaskFrameRenderList(self):
        User_in=[]
        User_in.append(input("设置筛选类型 (1:等待帧 2:渲染帧 4:完成帧 5:失败帧 11:超时停止)\n"))
        print(type(User_in))

        self.get_SearchList()
        print("--------------------爬取任务帧渲染列表中--------------------")
        self.TaskFrameRenderList["request_data"]["statusList"] = User_in
        self.post_qinqiu(self.TaskFrameRenderList["url"],self.TaskFrameRenderList["request_data"])
        self.analysis_TaskFrameRenderList(self.url_Data)
        print("--------------------爬取完成--------------------")
        print("--------------------打印分析结果--------------------")
        jishu=0
        for i in self.TaskFrameRenderList_Data:
            print(i)
            jishu+=1
        print("分析出"+ str(jishu) +"个失败帧")

    #爬取分析日志
    def get_rendering_analyse_showLog(self):
        print("--------------------爬取分析日志中--------------------")
        analyse_Log=self.post_qinqiu(self.rendering_analyse_showLog["url"],self.rendering_analyse_showLog["request_data"])
        print("--------------------爬取完成--------------------")
        self.save_log("analyse_Log.txt",analyse_Log)
     
    #爬取预处理日志
    def get_rendering_pre_showLog(self):
        self.get_SearchList()
        print("--------------------爬取分析日志中--------------------")
        pre_log=self.post_qinqiu(self.rendering_pre_showLog["url"],self.rendering_pre_showLog["request_data"])
        print("--------------------爬取完成--------------------")
        self.save_log("pre_Log.txt",pre_log)
        self.check_log("pre_log.txt")

    #爬取任务渲染日志
    def get_rendering_showLog(self):
        # self.get_SearchList()
        # self.get_TaskFrameRenderList()
        self.post_qinqiu(self.rendering_analyse_showLog["url"],self.rendering_analyse_showLog["request_data"]) 



    #保存日志
    def save_log(self,path,log):
        log=self.url_Data.replace('\\','/').replace('//','\\').replace('/r/r','\n').replace('/r','\n').replace('","','').replace(' ','')
        with open(path,'w+',encoding='utf-8') as f:
            f.write(log)
            f.close

    #日志分析
    def check_log(self,path):
        log_data=[]
        log_path=os.path.join("check",path)
        if not os.path.exists("check"):                  
            os.makedirs("check")

        with open(path,"r",encoding='utf-8') as checkFile:
            line = checkFile.readline()
            while line:   
                if "error" in line:
                    print(line)
                    log_data.append(line)
                line=checkFile.readline()
            checkFile.close()

        with open(log_path,'w+',encoding='utf-8') as f:
            for i in log_data:
                f.write(i)
            f.close
        
    def shuchu(self):
        self.get_rendering_pre_showLog()
        #全局信息分析做好来


a=renderbus(102937019)
a.shuchu()