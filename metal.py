# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 09:59:16 2016
    Crawling the member list of Taiwan  Metal Indsutry Association
    (http://www.trmsa.org.tw/Member.aspx)
    Using Selenium package to request page. Parsing page with Selenium and BeautifulSoup package.
    Python version: built from Anaconda 2.
@author: Wu
"""

def main(filePath, test, retryPath):
#%%
    from bs4 import BeautifulSoup as bs
    import pandas as pd
    from selenium import webdriver
    import time
    import traceback
    import pickle

#%%    

    saved={'dataList':None, 'index':None, 'load':False} if retryPath==None else pickle.load(open(retryPath,'rb'))
    if saved['load']:
        dataList=saved['dataList']
        start=saved['index']-1
        print 'start from {}'.format(start)
    else:
        dataList=[]; start=0
        
    try:
        fileCon=open(filePath,mode='w')
        driver = webdriver.Firefox()
        driver.implicitly_wait(10)
        driver.get('http://www.trmsa.org.tw/Member.aspx')
        submit=driver.find_element_by_id('ctl00_ContentPlaceHolder1_queryImageButton')
        submit.click()
        
    #%%
        
        enName=driver.find_elements_by_css_selector('.catalog1 a:nth-of-type(2)')
        enName.extend(driver.find_elements_by_css_selector('.catalog2 a:nth-of-type(2)'))
        enName=[x.text for x in enName]

        #test=10
        pageN=len(enName) if test==0 else test        
        for index in range(start,pageN):
            # has to 'refind' element whenver page has any chaged. even just reload
            entries=driver.find_elements_by_css_selector('.catalog1 a:nth-of-type(1)')  
            entries.extend(driver.find_elements_by_css_selector('.catalog2 a:nth-of-type(1)'))
            entry=entries[index]
            entry.click()
            page=driver.page_source
            driver.back()
            soup=bs(page,'lxml')
            dataDict={'name':soup.select('#ctl00_ContentPlaceHolder1_nameLabel')[0].text,
                      'registerNo':soup.select('#ctl00_ContentPlaceHolder1_uidLabel')[0].text,
                      'address':soup.select('#ctl00_ContentPlaceHolder1_addrLabel')[0].text,
                      'since':soup.select('#ctl00_ContentPlaceHolder1_setDateLabel')[0].text,
                      'capital':soup.select('#ctl00_ContentPlaceHolder1_capitalLabel')[0].text,
                      'employee':soup.select('#ctl00_ContentPlaceHolder1_employeeLabel')[0].text,
                      'productType':soup.select('#ctl00_ContentPlaceHolder1_itemLabel')[0].text,
                      'product':soup.select('#ctl00_ContentPlaceHolder1_productLabel')[0].text,
                      'source':driver.current_url,
                      'enName':enName[index]}
            dataList.append(dataDict)
            time.sleep(1)
            if index%10==0:
                time.sleep(3)
                
    except:
        traceback.print_exc()
        saved['dataList']=dataList
        saved['index']=index
        saved['load']=True
        pickle.dump(saved,open('metalSaved.pkl','wb'))
        return saved
    
#%%
    data=pd.DataFrame(dataList)
    data=data.drop_duplicates()
    data['NGOname']=u'台灣區金屬品冶製工業同業公會'
    data['NGOtype']=u'產業公會'
    data['orgType']=u''
    data['id']=u''
    data=data.reindex_axis(['id','NGOname','NGOtype','name','orgType','address','employee','capital','since','registerNo','productType','product','source','enName'],1)
    data.to_csv(fileCon,encoding='utf8',index=False,sep=';')
    return data
    fileCon.close()
    print 'job has done for metal Association'
    print 'file Destination '+filePath
    print ''
    

#%%
if __name__=='__main__':
    import argparse
    import os
        
    parser = argparse.ArgumentParser()
    parser.add_argument('filePath',nargs='?',default=os.getcwd())
    parser.add_argument('test',nargs='?',type=int, default=0)
    parser.add_argument('--retryPath',nargs='?')   
    args = parser.parse_args()
    
    filePath=os.getcwd()+'\\'+args.filePath+'\\metal.csv' if ':' not in args.filePath else args.filePath
    retryPath=os.getcwd()+'\\'+args.retryPath if ((args.retryPath!=None) and (':' not in args.retryPath))  else args.retryPath
    data=main(filePath, args.test, retryPath)