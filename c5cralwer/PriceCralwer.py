# -*- coding: utf-8 -*-

import requests,time,re
from bs4 import BeautifulSoup
from getproxy import ProxyPool
from GetC5Price import GetC5Price
from GetSteamPrice import GetSteamPrice
from Configure import Configure

class PriceCralwer(object):

    def __init__(self):
        self.priceTableStorage = [] #itemsStorage dictionary for storing item information

    #def getPriceRatios(self):

    def getPriceTables(self, steamPriceList):     
        self.priceTableStorage.extend(steamPriceList)

    def getProfitRatio(dictionary):
        return dictionary['profitRatio']

    def findMostProfit(self):
        #sort to find the most profitable item 
        self.priceTableStorage.sort(key = lambda priceTableStorage: priceTableStorage['profitRatio'])
        n = 0
        print("now listing the MVPs in " + str(len(self.priceTableStorage)) + " items: " )
        for item in self.priceTableStorage:
            if n < 20:
                print (str(n+1) + ' ' +str(item['name']) + ' ' + str(format(item['c5Price'], '0.2f')) + ' ' + str(format(item['realGotPrice'], '0.2f')) + ' ' + str(format(item['profitRatio'], '0.2f')))
                n += 1
            else:
                break

    def getProfitRatio(dictionary):
        return dictionary['profitRatio']



if __name__ == '__main__':
    configure = Configure()
    configure.read()
    configure.printConfig()

    timenow = time.time()
    proxyPool = ProxyPool(configure.configDict)
    getC5Price = GetC5Price(configure.configDict)
    getC5Price.getC5ItemLoop()
    C5items = getC5Price.getC5Items()

    #Seperate work into many sequenced works
    priceCralwer = PriceCralwer()
    while C5items:
        if len(C5items) >= 100:
            courrent_working_items = [C5items.pop() for i in range(100)]
        else:
            courrent_working_items = [C5items.pop() for i in range(len(C5items))]
        getSteamPrice = GetSteamPrice(courrent_working_items, proxyPool)
        getSteamPrice.caculateSteamPriceAllLoop_new()
        steamPriceList = getSteamPrice.getCaculatedList()
        priceCralwer.getPriceTables(steamPriceList)

    priceCralwer.findMostProfit()
    timeS = timenow - time.time()
    print(timeS)