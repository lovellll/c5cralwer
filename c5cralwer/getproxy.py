#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys,re,requests,random,asyncio,aiohttp
from bs4 import BeautifulSoup

header={'Host': 'www.gatherproxy.com',
'Origin': 'http://www.gatherproxy.com',
'Referer': 'http://www.gatherproxy.com/proxylist/anonymity/?t=Elite',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

class GatherProxy(object):
    '''To get proxy from http://gatherproxy.com/'''
    url='http://gatherproxy.com/proxylist'

    #getEliteProxySet form one page
    def getEliteProxySet(self,page,uptime=70,fast=True):
        '''Get Elite Anomy proxy
        Pages define how many pages to get
        Uptime define the uptime(L/D)
        fast define only use fast proxy with short reponse time'''
        proxies = set()
        data = {"Type":"elite","PageIdx":str(page),"Uptime":str(uptime)}
        r=requests.post(self.url+"/anonymity/?t=Elite",data=data,headers=header)
        soup = BeautifulSoup(r.text, features='lxml')
        proxy_list = soup.find('div', {'class': 'proxy-list'})
        tempProxies = proxy_list.find_all('tr')
        for textline in tempProxies:
            #check if it is a fast proxy
            ping = re.search(r'(\d+)ms', textline.get_text())
            if not ping:
                continue
            elif int(ping.group(1)) > 400:
                continue
            else:
                address = re.findall(r"document.write\('((\d+\.?)+)'", textline.get_text())[0][0]
                port = re.findall(r"gp\.dep\('(.{2,4})(?=')", textline.get_text())[0]
                proxies.add(str(address)+":"+str(int('0x'+port,16)))
        return proxies

class ProxyPool(object):
    '''A proxypool class to obtain proxy'''

    gatherproxy=GatherProxy()

    def __init__(self, configDict):
        self.pool = set()
        self.poolValid = set()
        self.pageIndexes = list(range(1, 300))    #page numbers are 1-300
        #defaul page numbers
        self.startPage = 1
        self.pagesNumber = 1
        self.workingPages = []
         #deep copy config
        self.configGetProxy = {}
        for item in configDict:
            self.configGetProxy[item] = configDict[item]
        self.initPages(True)
        self.updateGatherProxy()
        self.validateProxyPoorLoop()
       

    def initPages(self, ifFisrtTime = False):
        if ifFisrtTime:
            if  self.configGetProxy['startProxyPage']:
                self.startPage = int(self.configGetProxy['startProxyPage'])
            else:
                self.startPage = int(input('Please input START proxy spages to obtain'))

            if self.configGetProxy['proxyPagesN']:
                self.pagesNumber = int(self.configGetProxy['proxyPagesN'])
            else:
                self.pagesNumber = int(input('Please input proxy pages to obtain'))
            #pop item in pageIndexes to workingPages
            for i in range(self.pagesNumber):
                self.workingPages.append(self.pageIndexes.pop(self.startPage -1))
        else:
            for i in range(10):
                self.workingPages.append(self.pageIndexes.pop(random.randrange(len(self.pageIndexes))))

    #update valid proxies form input pages
    def updateGatherProxy(self):
        '''Use this to update proxy valid pool'''
        print("updating proxy lists form " + str(self.workingPages) + " page")
        for i in self.workingPages.copy():
            self.pool.update(self.gatherproxy.getEliteProxySet(i))
            self.workingPages.remove(i)
        
    def removeProxy(self,proxy):
        '''Remove a proxy from pool'''
        if (proxy in self.pool):
            self.pool.remove(proxy)

    async def validateOne(self, client, proxy):
        try:
            async with client.request('get', 'https://www.google.com', proxy = 'http://' + str(proxy), timeout = 5) as resp:
                #if OK
                print('Found a valid proxy: ' + proxy)
                self.poolValid.add(proxy)
                self.pool.remove(proxy)
                return resp.status
        except :
            #if an exception was araised
            self.pool.remove(proxy)
            return 999

    async def validateProxyPoor(self):
        '''Use this to validate proxy pool'''
        async with aiohttp.ClientSession() as client:
            tasks = [self.validateOne(client, proxy) for proxy in self.pool]
            await asyncio.wait(tasks)
        #all objects in self.pool has been validated, so clear it
        self.pool.clear()

    def validateProxyPoorLoop(self):
        #create a validating loop and run it
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.validateProxyPoor())
        loop.close()

    def updateAndValidateProxies(self):
        self.initPages()
        self.updateGatherProxy()
        self.validateProxyPoorLoop()

    def getProxy(self):
        '''Get a dict format proxy randomly'''
        if self.poolValid:
            proxy = self.poolValid.pop()
        else:
            self.updateAndValidateProxies()
            return self.getProxy()
        print('get a proxy: ' + str(proxy))
        return proxy
  

if __name__ == '__main__':
    proxyPool = ProxyPool()
    print(proxyPool.getProxy())
    print(proxyPool.poolValid)
    print(proxyPool.pool)

