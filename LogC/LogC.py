#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import os.path
import time
import shutil
import sys
import win32com.client 
import pandas as pd

logpath = 'MNZ_Mura'
err = []
info = {}
SumResult = {}
stationlist = ['MNZ_Inline','MNZ_Inline_PostBond','MNZ_Mura','MNZ_Sensor','MNZ_OptimusSIT','MNZ_OptimusCC',
               'Inline','Inline_PostBond','Mura','Sensor','SIT','CC']
#stationlist = ['Slot0']
               
def pandas_to_csv(filename,info):
    #print("info",info)
    if info is None:
        return
    isheader = not os.path.exists(filename)
    pd_look = pd.DataFrame.from_records([info])
    if filename.find('_sum') != -1:
        columns = ['Station','TestName', 'Result', 'FR', 'FailCount','TotalRun']
    else:
        columns = ['RunID', 'TestName', 'SN','ECCount', 'ECSkip','Result']
    pd_look.to_csv(filename,mode='a',encoding='utf_8_sig',header=isheader,index=False,columns=columns)

def logAnalysis(logpath):
#  print(logpath)
  try:
    fo = open(logpath, "r",encoding='UTF-8')
    line = fo.readline()
    ECList = []
    ECcount = 0
    ECSkip = 0
    if line.find("FileLocation, Date,") != -1:
      Islog = True
    else:
      Islog = False

    if Islog:
      lineList = fo.readlines()
      for line in lineList:
        if line.find(": 0x")!= -1:
          if line.find("not reported under data collection mode")!=-1:
              ECSkip=ECSkip+1
          else:
              ECcount=ECcount+1
          tmp=line.split(',')
          #print(tmp[6])
          ECList.append('###--'+str(ECcount+ECSkip)+'--###')
          ECList.append(tmp[6][0:250])          
  
  finally:
    if fo:
      fo.close()
  return ECcount, ECSkip, ECList

#sort csv by TestName
def sortResult(logpth):
    if os.path.exists(logpth+'_tmp.csv'):
        df = pd.read_csv(logpth+'_tmp.csv', header = 0, index_col=0)
        df=df.sort_values(by=['TestName'])
        df.to_csv(logpth+'_result.csv',mode='a',encoding='utf_8_sig')
    else:
        print("!!!!!!Path:",logpth,"_tmp.csv Not exist")


#result summary
def saveResult(logpth, Pre_test, failcnt, totalrun, sumpath):
    SumResult['Station'] = logpth
    SumResult['TestName'] = Pre_test
    SumResult['FR'] = ' '+str(failcnt)+'/'+str(totalrun)
    SumResult['TotalRun'] = totalrun
    SumResult['FailCount'] = failcnt
    if failcnt > 0:
       SumResult['Result'] = "Fail"
    else:
       SumResult['Result'] = "Pass"
       #print(SumResult)
    pandas_to_csv(sumpath,SumResult)

def resultSum(logpth, allinone):
    if os.path.exists(logpth+'_result.csv'):
        df = pd.read_csv(logpth+'_result.csv', header = 0, index_col=0)
        row,colume = df.shape
        #print("Row:",row,"Col:",colume)
        Pre_test=''
        totalrun = 0
        failcnt = 0
        if allinone:
            sumpath = 'all_sum.csv'
        else:
            sumpath = logpth+'_sum.csv'
    
        for i in range(0,row):
            #print("i:",i,'row:',row)
            Cur_test = df.iloc[i].at['TestName']
            testresult = df.iloc[i].at['ECCount']
                
            if Cur_test is Pre_test or Pre_test is '':
              totalrun=totalrun+1
              if testresult > 0:
                 failcnt=failcnt+1
            else:
              saveResult(logpth, Pre_test, failcnt, totalrun, sumpath)

              totalrun=1
              if int(testresult) > 0:
                failcnt=1
              else:
                failcnt=0
            Pre_test=Cur_test
        saveResult(logpth, Pre_test, failcnt, totalrun, sumpath)
    else:
        print("!!!!!!Path:",logpth,"_result.csv Not exist")


def startAnalysis(logpth):
    for fpathe,dirs,fs in os.walk(logpth):
      for f in fs:
        #if f.find(".err")!= -1:
          #err.append(f)
        if f.find(".log")!= -1 and f.find("_TestSuite_") == -1:
          #print(f)
          logname=f
          #logname = filename[1].replace(".err",".log")
          print(logname)
          tmp=logname.split('_')
          info['RunID'] = str('RunID:'+tmp[0])
          info['TestName']=tmp[1]
          info['SN']='SN:'+str(tmp[2]).replace('.log','')
          #info['SN']=tmp[2].replace('.log','')
          ECnum, ECSkip, Result = logAnalysis(logpth+'\\'+logname)
          #print(Result)
          info['Result']=Result
          info['ECCount']=ECnum
          info['ECSkip']=ECSkip
          pandas_to_csv(logpth+'_tmp.csv',info)

######################################################################
# Main
######################################################################    
starttime=time.time()
print("start",starttime)

for logpth in stationlist:
    startAnalysis(logpth)
    sortResult(logpth)
    resultSum(logpth, True)
