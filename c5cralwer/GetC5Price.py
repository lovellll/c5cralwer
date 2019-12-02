# -*- coding: utf-8 -*-
import requests,time,re,json,asyncio,aiohttp
from bs4 import BeautifulSoup
from getproxy import ProxyPool

class GetC5Price(object):
    """get the C5 price of an item"""
    s_url = 'https://www.c5game.com'
    page_url = {'csgo': '/csgo/default/result.html', 'dota2': '/dota.html'}
    games = ['csgo', 'dota2']
    cookies = {'C5Lang': 'en'}
    #default page
    
    def __init__(self, configDict):
        #self.page_url = "/csgo/default/result.html"

        #deep copy configuration
        self.configGetC5Price = {}
        for item in configDict:
            self.configGetC5Price[item] = configDict[item]
        
        if self.configGetC5Price['game']:
            self.game = self.configGetC5Price['game']
        else:
            self.game = 'csgo'
        self.pageNumbers = {'minPrice': 0, 'maxPrice': 100, 'priceStartPage': 1, 'endPage': 1, 'priceSearchPageN': 1, 'lastPage': 1}
        self.params = {'min': 0, 'max': 100, 'page': 1}
        self.itemsStorage = [] #itemsStorage dictionary for storing item information
        self.initPages()

    def initPages(self):
        for item in self.pageNumbers:
            if item in self.configGetC5Price:
                self.pageNumbers[item] = int(self.configGetC5Price[item])

        if not self.pageNumbers['minPrice']:
            self.pageNumbers['minPrice'] = int(input("Plz input the min price for searching: "))
        if not self.pageNumbers['maxPrice']:
            self.pageNumbers['maxPrice'] = int(input("Plz input the max price for searching: "))
        if not self.pageNumbers['priceStartPage']:
            self.pageNumbers['priceStartPage'] = int(input("Plz input the start searching page: "))
        if not self.pageNumbers['priceSearchPageN']:
            self.pageNumbers['priceSearchPageN'] = int(input("Plz input the number of max searching pages: "))
        self.pageNumbers['endPage'] = self.pageNumbers['priceStartPage'] + self.pageNumbers['priceSearchPageN'] -1
        self.checkOutBound()

    def checkOutBound(self):
        #check if out of bounder，if so adjust it
        r = requests.get(self.s_url + self.page_url[self.game], params = self.params)
        #debug
        print(re.findall(r'class="last.*page=(\d*)">', r.text))
        self.pageNumbers['lastPage'] = int(re.findall(r'class="last.*page=(\d*)">', r.text)[0])
        if self.pageNumbers['endPage'] > self.pageNumbers['lastPage']:
            self.pageNumbers['endPage'] = self.pageNumbers['lastPage']

    async def getC5ItemOne(self, page, client, proxy = ''):
        print("getting c5 prices from page " + str(page))
        self.params['page'] = str(page)
        async with client.get(self.s_url + self.page_url[self.game], params = self.params, timeout = 10) as resp:
            resptext = await resp.text()
            soup = BeautifulSoup(resptext, features = 'lxml')
            itemSelling = soup.find('ul', {"class": "list-item4 clearfix "}).find_all('li', {"class": "selling"})
            #iterinng all selling items in C5, store names and prices
            for item in itemSelling:     
                name = item.find('span', {"class": re.compile("^ text")}).get_text()
                c5Price = item.find('span', {"class": "price"}).get_text()
                #delete ￥ mark in price
                c5Price = re.findall(r'(\d+(\.\d+)?)', c5Price)[0][0]
                c5Price = float(c5Price)
                #store items in itemsStorage
                self.itemsStorage.append({'game':self.game, 'name':name, 'c5Price': c5Price})

    async def getC5ItemSellingList(self):
        self.params['min'] = self.pageNumbers['minPrice']
        self.params['max'] = self.pageNumbers['maxPrice']
        async with aiohttp.ClientSession(cookies=self.cookies) as client:
            tasks = [self.getC5ItemOne(pageN, client) for pageN in range(int(self.pageNumbers['priceStartPage']), int(self.pageNumbers['endPage']) + 1)]
            await asyncio.wait(tasks)

    def getC5Items(self):
        if self.itemsStorage:
            return self.itemsStorage
        else:
            print('C5 self.itemsStorage is None!, getC5ItemSellingList() again ')
            self.getC5ItemSellingList()
            return self.getC5Items()

    def getC5ItemLoop(self):
         loop = asyncio.new_event_loop()
         asyncio.set_event_loop(loop)
         loop.run_until_complete(self.getC5ItemSellingList())
         loop.close()




if __name__ == '__main__':
    getC5Price = GetC5Price('csgo')
    getC5Price.getC5ItemLoop()
    print(getC5Price.getC5Items())
    print('the number of items is ' + str(len(getC5Price.getC5Items())))