class Configure(object):
    '''get configuration from file "config.json"'''
    def __init__(self):
        self.configDict = {}
        self.configDict['startProxyPage'] = None
        self.configDict['proxyPagesN'] = None
        self.configDict['minPrice'] = None
        self.configDict['maxPrice'] = None
        self.configDict['priceStartPage'] = None
        self.configDict['priceSearchPageN'] = None
        self.configDict['game'] = None

    def read(self):
        with open('config.ini') as c5Config:
            for line in c5Config:
                if line.startswith('#') or line.isspace():
                    continue
                else:
                    key, value = line.split(' = ')
                    if key in self.configDict:
                        self.configDict[key] = value.replace('\n', '')

    def printConfig(self):
        print(self.configDict)
