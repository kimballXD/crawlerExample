# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 22:58:25 2016
    Crawling the member list of Taiwan Foundry Association
    (http://www.foundry.org.tw:8080/institute/')
    Using Requests package with post method. Parsing page with BeautifulSoup package.
    Python version: built from Anaconda 2.
@author: Wu
"""

#%%
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import os,sys
import random, time

#%%
def main(filePath, test):
    #%%
    fileCon=open(filePath, mode='w')    
    host='http://www.foundry.org.tw:8080/institute/'
    queryUrl='http://www.foundry.org.tw:8080/institute/listFactory.do?forward=factorys&isFree=false'
        
    formData={'factory.corpName': '',
     'factory.corpType': '',
     'factory.moldingMethod': '-1',
     'factory.remark': '',
     'factoryConvert.breadWinningProduct': '-1',
     'factoryConvert.bwproductCondition': '-1',
     'factoryConvert.isoCondition': '-1',
     'x': '28',
     'y': '15'}
 
    formData2={'factory.corpName': '',
     'factory.corpType': '',
     'factory.moldingMethod': '-1',
     'factory.remark': '',
     'factoryConvert.breadWinningProduct': '-1',
     'factoryConvert.bwproductCondition': '-1',
     'factoryConvert.isoCondition': '-1',
     'toPage': '',
     'nextPages': '1'}
 
    productTypeDict={'aa':'鑄造設備廠',
    'zz':'其它',
    'bb':'鑄造材料廠',
    'cc':'模型製造廠',
    'dd':'鑄件生產廠',
    'gg':'材料設備代理',
    'ee':'鑄造顧問',
    'hh':'學術／研究機構',
    'ff':'鑄件買賣'} 
    
    itemTypeDict={'factory.autoPart':'汽機車零件',
    'factory.aviation':'航空國防零件',
    'factory.axis':'軸件',
    'factory.boatPart':'船舶及機械零件',
    'factory.engine':'壓縮機及發動機',
    'factory.handcraft':'手工具',
    'factory.motor':'馬達及減速機',
    'factory.mould':'模具',
    'factory.pipe':'管接頭、凸緣及閥',
    'factory.pump':'抽水機',
    'factory.sportingGoods':'休閒及體育用品',
    'factory.tool':'工具機及零件'}


    #%%
    dataDict={}
    for key in productTypeDict:
        formData['factory.corpType']=key
        session=requests.session()
        session.get('http://www.foundry.org.tw:8080/institute/listNotice.do?forward=manfactures')
        urlPage=session.post(queryUrl,data=formData)
        soup=bs(urlPage.text,'lxml')
        pages=len(soup.select('#pageselect option'))
        #pageN=pages if test==0 else test
        for page in range(1,pages+1):
            if page!=1:
                formData2['toPage']=str(page)
                formData2['factory.corpType']=key
                urlPage=session.post(queryUrl,data=formData2)
            soup=bs(urlPage.text,'lxml')
            urls=soup.select('a.aNews1')
            urls=[host+x.get('href') for x in urls]
            for url in urls:
                urlId=re.search('id=(\d+)',url).group(1)
                if urlId in dataDict: continue
                itemPage=requests.get(url)
                soup=bs(itemPage.text,'lxml')
                tables=soup.select('table')
                rows=tables[-4].select('td.zt12px_10')
                rows=[x.find_next_siblings('td')[1] for x in rows]
                productType=tables[-4].find_all(lambda tag: True if ((tag.name=='input')&(tag.get('checked')=='checked')&(tag.get('name')=='factory.corpType')) else False)
                productType=[productTypeDict[x.get('value')] for x in productType]
                itemType=tables[-4].find_all(lambda tag: True if ((tag.name=='input')&(tag.get('checked')=='checked')&(tag.get('name')in ['factory.autoPart', 'factory.aviation', 'factory.axis', 'factory.boatPart', 'factory.engine', 'factory.handcraft', 'factory.motor', 'factory.mould', 'factory.pipe', 'factory.pump', 'factory.sportingGoods', 'factory.tool'])) else False)
                itemType=[itemTypeDict[x.get('name')] for x in itemType]
                itemType=list(set(itemType))
                dataDict[urlId]={'id':rows[0].text.strip(),  #會員編號
                          'name':rows[3].text.strip(),  #公司名稱
                          'address':rows[18].text.strip(), #地址
                          'employee':rows[6].text.strip(),
                          'capital':rows[1].text.strip(),
                          'since':rows[5].text.strip(),
                          'registerNo':rows[11].text.strip(),      
                          'product':itemType, #產品
                          'productType':productType,
                          'source':url,
                          'enName':rows[4].text.strip()}

    #%%
    data=pd.DataFrame(dataDict).T
    data['NGOname']=u'台灣鑄造學會'
    data['NGOtype']=u'產業公會'
    data['orgType']=u''
    data=data.reindex_axis(['id','NGOname','NGOtype','name','orgType','address','employee','capital','since','registerNo','productType','product','source','enName'],1)
    data.to_csv(fileCon,encoding='utf8',index=False,sep=';')
    fileCon.close()
    print 'job has done for foundry Association, get {} records'.format(len(data))
    print 'file Destination '+filePath
    print ''
    return data
    #%%
if __name__=='__main__':
    import argparse
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument('filePath',nargs='?',default=os.getcwd())
    parser.add_argument('test',nargs='?',type=int, default=0)
    args = parser.parse_args()
    filePath=os.getcwd()+'\\'+args.filePath+'\\foundry.csv' if ':' not in args.filePath else args.filePath
    data=main(filePath, args.test)
        

