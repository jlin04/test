import json
from multiprocessing import Pool
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
ua = UserAgent()
headers1 = {'User-Agent':'ua.ramdom'}
import re
import pandas as pd
import os
import time
from selenium import webdriver

def generate_allurl(user_in_nub,user_in_city):      #生成url
    #print("--generate_allurl: city:", user_in_nub, " num:",user_in_nub)
    url = 'http://' + user_in_city + '.lianjia.com/ershoufang/pg{}/'
    for url_next in range(1,int(user_in_nub)):
        yield url.format(url_next)


def get_allurl(generate_allurl):                    #分析url解析出每一页的详细url
    print("--get all url", generate_allurl)
    get_url = requests.get(generate_allurl,'lxml',headers = headers1)
    #print("get_url result",get_url.status_code)
    if get_url.status_code == 200:
        print(get_url)
        re_set = re.compile('<li.*?class="clear LOGCLICKDATA">.*?<a.*?class="noresultRecommend img.*?".*?href="(.*?)"')
        re_get = re.findall(re_set,get_url.text)
        print("re_get",re_get)
        return re_get

def open_url(re_get):           #分析详细url获取所需信息
    print("--Open url:", re_get)
    if re_get.find('https://') == -1:
        return
    res = requests.get(re_get,'lxml',headers = headers1)
    if res.status_code == 200:
        info = {}
        soup = BeautifulSoup(res.text,'lxml')
        #print(soup)
        info['标题'] = soup.select('.main')[0].text
        info['总价'] = soup.select('.total')[0].text + '万'
        info['每平方售价'] = soup.select('.unitPriceValue')[0].text
        info['参考总价'] = soup.select('.taxtext')[0].text
        info['建造时间'] = soup.select('.subInfo')[2].text
        info['小区名称'] = soup.select('.info')[0].text
        info['所在区域'] = soup.select('.info a')[0].text + ':' +  soup.select('.info a')[1].text
        info['链家编号'] = str(re_get)[33:].rsplit('.html')[0]

        for i in soup.select('.base li'):
            i = str(i)
            if '</span>' in i or len(i) > 0 :
                key,value = (i.split('</span>'))
                info[key[24:]] = value.rsplit('</li>')[0]
        info['Link'] = re_get
        spans = soup.find_all('span', attrs={'class':'label'})
        for span in spans:
            if span.string.find('挂牌时间') != -1:
                info['挂牌时间'] = span.next_sibling.next_sibling.string
            elif span.string.find('上次交易') != -1:
                info['上次交易'] = span.next_sibling.next_sibling.string        
        #url = 'https://sh.lianjia.com/ershoufang/houseseerecord?id=107101077074'
        url_record = 'https://sh.lianjia.com/ershoufang/houseseerecord?id='+info['链家编号'][1:]
        res_record = requests.get(url_record,'lxml',headers = headers1)
        splitresult = res_record.text.split(',',4)
        
        indexW = splitresult[0].find('thisWeek')
        if indexW != -1:
            info['ThisWeek'] = splitresult[0][indexW+10:]
        indexT = splitresult[1].find('totalCnt')
        if indexT != -1:
            info['TotalCnt']=splitresult[1][indexT+10:]

        return info

def pandas_to_xlsx(info, line):               #储存到xlsx
    print("info",info, "line:",line)
    if info is None:
        return
    pd_look = pd.DataFrame.from_records([info])
    print(pd_look)
    pd_look.to_excel('detail.xlsx',sheet_name='detail',startrow=line)

def pandas_to_csv(filename,info):               #储存到csv
    print("info",info)
    if info is None:
        return
    isheader = not os.path.exists(filename)
    pd_look = pd.DataFrame.from_records([info])
    if filename.find('detail.csv') != -1:
        columns = ['标题', '总价', '每平方售价', '参考总价', '建造时间', '小区名称', '所在区域', '链家编号', '房屋户型',
               '所在楼层', '建筑面积', '户型结构', '套内面积', '建筑类型', '房屋朝向', '建筑结构', '装修情况', '梯户比例',
               '配备电梯', '产权年限','挂牌时间','上次交易','ThisWeek','TotalCnt','Link']
        pd_look.to_csv(filename,mode='a',encoding='utf_8_sig',header=isheader,index=False,columns=columns)
    elif filename.find('summary.csv') != -1:
        columns = ['Date', '普通住宅', '200万以下', '200-300万', '300-400万', '400-500万']
        pd_look.to_csv(filename,mode='a',encoding='utf_8_sig',header=isheader,index=False,columns=columns)

def writer_to_text(list):               #储存到text
    with open('detail.txt','a',encoding='utf-8')as f:
        f.write(json.dumps(list,ensure_ascii=False)+'\n')
        f.close()

def main(url):
    print("main")
    open_list = open_url(url)
    # writer_to_text(list)    #储存到text文件
    #update_to_MongoDB(open_list)   #储存到Mongodb

if __name__ == '__main__':
    url = 'https://sh.lianjia.com/ershoufang/huangpu/co52pg1sf1p1p2p3p4/'
    #url = 'https://sh.lianjia.com/ershoufang/houseseerecord?id=107101077074'
    #headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
    datestr=time.strftime("%Y%m%d", time.localtime())
    get_url = requests.get(url,'lxml',headers = headers1)
    #print("response",get_url.text)

    if get_url.status_code == 200:
        print(get_url)
        re_set = re.compile('<a class="img" href="(.*?)"')
        re_get = re.findall(re_set,get_url.text)
        info = {}
        info['Date']=datestr
        soup = BeautifulSoup(get_url.text,'lxml')
        #print(soup.prettify())
        spans = soup.find_all('span', attrs={'class':'name'})
        for span in spans:
            if span.string.find('200万以下') != -1:
                info['200万以下'] = span.next_sibling.next_sibling.string[1:-1]
            elif span.string.find('200-300万') != -1:
                info['200-300万'] = span.next_sibling.next_sibling.string[1:-1]
            elif span.string.find('300-400万') != -1:
                info['300-400万'] = span.next_sibling.next_sibling.string[1:-1]
            elif span.string.find('400-500万') != -1:
                info['400-500万'] = span.next_sibling.next_sibling.string[1:-1]
            elif span.string.find('普通住宅') != -1:
                info['普通住宅'] = span.next_sibling.next_sibling.string[1:-1]              
        pages = soup.find('div', attrs={'class':'page-box house-lst-page-box'})
        text = pages['page-data']
        indexT = text.find("totalPage")
        indexC = text.find("curPage")
        if indexT != -1:
            print(text)
            print("Start:", indexT)
            print("End:", indexC)
            totalpage = text[indexT+11:indexC-2]
            print("totalPage:", totalpage)
    pandas_to_csv(datestr+'_summary.csv',info)

    if True:
        for eachurl in re_get:
            open_list = open_url(eachurl)
            pandas_to_csv(datestr+'_detail.csv',open_list)
