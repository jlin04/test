#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import os.path
import time
import shutil
import sys
import win32com.client 
import pandas as pd

def pandas_to_csv(filename,info):
    print("info",info)
    if info is None:
        return
    isheader = not os.path.exists(filename)
    pd_look = pd.DataFrame.from_records([info])
    columns = ['RunID', 'TestName', 'SN','ECCount', 'Result']
    #pd_look['SN'] = st_look['SN'].astype('str')
    pd_look.to_csv(filename,mode='a',encoding='utf_8_sig',header=isheader,index=False,columns=columns)


def logAnalysis(logpath):
#  print(logpath)
  try:
    fo = open(logpath, "r")
    line = fo.readline()
    ECList = []
    ECcount = 0
    if line.find("FileLocation, Date,") != -1:
      Islog = True
    else:
      Islog = False

    if Islog:
      lineList = fo.readlines()
      for line in lineList:
        if line.find(": 0x")!= -1:
          ECcount=ECcount+1
          tmp=line.split(',')
          #print(tmp[6])
          ECList.append('###--'+str(ECcount)+'--###')
          ECList.append(tmp[6][0:250])          
  
  finally:
    if fo:
      fo.close()
  return ECcount, ECList

######################################################################
# Main
######################################################################    
starttime=time.time()
print("start",starttime)
logpth = 'MNZ_OptimusCC'
#current=time.time()
#print(current)
err = []
info = {}

for fpathe,dirs,fs in os.walk(logpth):
  for f in fs:
    #if f.find(".err")!= -1:
      #err.append(f)
    if f.find(".log")!= -1:
      #print(f)
      logname=f
      #logname = filename[1].replace(".err",".log")
      print(logname)
      tmp=logname.split('_')
      info['RunID'] = str('RunID:'+tmp[0])
      info['TestName']=tmp[1]
      info['SN']='SN:'+str(tmp[2]).replace('.log','')
      #info['SN']=tmp[2].replace('.log','')
      ECnum, Result = logAnalysis(logpth+'\\'+logname)
      #print(Result)
      info['Result']=Result
      info['ECCount']=ECnum
      pandas_to_csv(logpth+'_tmp.csv',info)

#sort csv by TestName     
df = pd.read_csv(logpth+'_tmp.csv', header = 0, index_col=0)
df=df.sort_values(by=['TestName'])
df.to_csv(logpth+'_result.csv',mode='a',encoding='utf_8_sig')
