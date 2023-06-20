import os
import re

error_log = []


error_data=[]

with open(r"pre_log.txt","r",encoding='utf-8') as checkFile:
    line = checkFile.readline()
    while line:   
        if "error" in line:
            print(line)
            error_data.append(line)
        line=checkFile.readline()
    checkFile.close()

a=os.path.join("check","log.txt")
if not os.path.exists("check"):                  
    os.makedirs("check")

with open(a,'w+',encoding='utf-8') as f:
    for i in error_data:
        f.write(i)
    f.close

