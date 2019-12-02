# -*- coding: utf-8 -*-
import requests,json,asyncio,aiohttp
from getproxy import ProxyPool
import math

class GetSteamPrice(object):
    """get the steam market price of an item"""
    ratio = 6.9 #USD to CNY
    steam_url = "https://steamcommunity.com"
    appid = {'csgo': 730, 'dota2': 570}
    
    def __init__(self, itemsStorage, proxyPool):
        self.itemsStorage = itemsStorage
        self.proxyPool = proxyPool
        self.itemsStorageCaculated = []
        self.statusCheck = []  #A list to check if all caculating is finished

    async def getSteamPrice(self, game, name, client, proxy):
        search_url = "/market/search/render/?count=1&q=&appid=" + str(self.appid[game]) + "&norender=1&query=" + str(name)
        try:
            async with client.request('get', self.steam_url + search_url, proxy = 'http://' + str(proxy), timeout = 15) as resp:
                 #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!要来一个if，看是否是200，如果是，在json.loads，如果出界，那就是名字有问题，或者没有正在出售的，那么就要另外处理
                 #如果不是，那就是time out，raise exception
                 if resp.status == 200:
                    resptext = await resp.json()
                    try:
                        steamSellingPrice = float(resptext['results'][0]['sell_price']) / 100 * self.ratio
                        return steamSellingPrice                  #if it returns steamSellingPrice, it succeeded. all other returns are failure
                    except Exception as e:
                        print(e)
                        return float(0.00000000000000000001)      #if it reaches this exception, it means there is no such item in steam market, so set the price to a very small price 
                 else:
                     return float(-1)
        except Exception as e:
            print(e)
            return float(-1)

    async def caculateSteamPriceOne(self, item, client, proxy):
        steamSellingPrice = await self.getSteamPrice(item['game'], item['name'], client, proxy)
        if steamSellingPrice == -1:
            #if reched server limit, put it back in itemsStorage
            self.itemsStorage.append({'game': item['game'], 'name': item['name'], 'c5Price': item['c5Price']})
            return -1
        else:
            if steamSellingPrice == 0:
                steamSellingPrice = 0.0001
            steamPrice  = steamSellingPrice
            realGotPrice = steamSellingPrice/1.15
            profitRatio = item['c5Price'] / realGotPrice
            if realGotPrice == 0:
                realGotPrice = 0.0000001
            self.itemsStorageCaculated.append({'game': item['game'], 'name': item['name'], 'c5Price': item['c5Price'], 'steamPrice': steamPrice, 
                                           'realGotPrice':  realGotPrice, 'profitRatio': profitRatio})
            print(self.itemsStorageCaculated[-1])  #for testing
            return 0

    async def caculateSteamPriceAll_new(self):
        if len(self.itemsStorage)== 0:
            print('All items in itemsStorage has been caculated!')
            self.statusCheck = ['ALLFINISHED']
            #if itemsStorage has no objects, do not caculate
        else :
            #get 20 items' price using each proxy, if the number of items is less than 20, get all of them
            groupN = math.ceil(len(self.itemsStorage)/20)
            tasks = []
            async with aiohttp.ClientSession() as client:
                for _ in range(groupN):
                    if len(self.itemsStorage) > 20:
                        caculatingN = 20
                    else:
                        caculatingN = len(self.itemsStorage)
                    proxy = self.proxyPool.getProxy()
                    tasks.extend([self.caculateSteamPriceOne(self.itemsStorage.pop(0), client, proxy) for _ in range(caculatingN)]) 
                    #we eventually warped (kind like) groupN*tasks tasks in tasks coroutine warper
                #now, every group of caculating tasks is in the tasks warper(tasks), then start await(yielding from)
                fResult, _  = await asyncio.wait(tasks)
                self.statusCheck = [r.result() for r in fResult]

    def getCaculatedList(self):
        return self.itemsStorageCaculated

    def caculateSteamPriceAllLoop_new(self):
        #create a validating loop and run it
        while True:
            if self.statusCheck == ['ALLFINISHED']:
                break
            else:
                #if the number of proxies is less than searching groups, get more proxies
                #修改成边获得代理列表，边获取价格
                #有多少代理就用多少代理
                while len(self.proxyPool.poolValid) < math.ceil(len(self.itemsStorage) / 20.0):
                    self.proxyPool.updateAndValidateProxies()
                print('one more getsteam price round')
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.caculateSteamPriceAll_new())
                loop.close()

if __name__ == '__main__':
    proxyPool = ProxyPool()
    itemsStorage = [{'name': 'M4A4', 'c5Price': float(77)}]
    getSteamPrice = GetSteamPrice(itemsStorage, proxyPool)
    getSteamPrice.caculateSteamPriceAllLoop_new()
    print(getSteamPrice.getCaculatedList())
    

