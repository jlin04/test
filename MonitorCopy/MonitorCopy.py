#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import os.path
import time
import shutil
import sys
import win32com.client 


mteos = 'mteos'
mteosdisk = 'Y:\\'
def CopyMTEOS(sourcefolder):
  print("CopyMTEOS", sourcefolder)
  shell = win32com.client.Dispatch("WScript.Shell")
  for fpathe,dirs,fs in os.walk(sourcefolder):
    #print("fs",fs)
    for f in fs:
      #print(f)
      if f.find('.lnk') > 0:
        linkpath = os.path.join(fpathe, f)
        print("link:",linkpath)
        shortcut = shell.CreateShortCut(linkpath)
        print("shortcut:",shortcut.Targetpath)
        tmp = shortcut.Targetpath.split('\\')
        mteosfolder = os.path.join(mteosdisk, tmp[-1])
        print("mteosfoler",mteosfolder)                              
        #shutil.copytree(shortcut.Targetpath,mteos)

######################################################################
# Main
######################################################################    
starttime=time.time()
print("start",starttime)
source = 'log'
des = 'result2'
#source = 'z:\\ev2'
keepfind = True
current=time.time()
print(current)
while(keepfind and current-starttime<10):
  current=time.time()
  time.sleep(1)
  print("sleep...")
  #print(current)
  dirs = os.listdir(source)
  for folder in dirs:
    folderpath = os.path.join(source, folder)
    #print(folderpath)
    if os.path.isdir(folderpath):
     dirCreateAt = os.path.getctime(folderpath)
     #print(dirCreateAt)
     if dirCreateAt > current:
       print("folderpath",folderpath)
       #shutil.copytree(folderpath,des)
       CopyMTEOS(folderpath)
       keepfind = False
       

  #for f in fs:
    #print(f)
    #print(os.path.getctime(os.path.join(source, f)))
    #if f.find("_KoreEnumerationTest_")!= -1:
      #print(f)
      #GetMachineAndFW(os.path.join(fpathe,f))
