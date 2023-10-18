chcp 65001
@echo off

set PYfile=F:\work\python\代码库\web_crawler\animepc.py
set PY=python

set sousuo="S1 NO.1 STYLE"
set leixing="3D動畫"
set yeshu=1
set xiazai="E:\缓存\爬虫图片"
set vpn="192.168.31.160"

echo 搜索:%sousuo%
echo 类型:%leixing%
echo 页数:%yeshu%
echo 下载路径:%xiazai%
echo vpn:%vpn%
echo -------------------开始执行脚本-------------------
%PY% %PYfile% %sousuo% %leixing% %yeshu% %xiazai% %vpn%

pause