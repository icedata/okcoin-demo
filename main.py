#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果

from OkcoinSpotAPI import OKCoinSpot
from OkcoinFutureAPI import OKCoinFuture
import time
import numpy as np

#初始化apikey，secretkey,url
apikey = 'your apikey'
secretkey = 'your secretkey'
okcoinRESTURL = 'www.okcoin.com'

def log(content):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    filename = time.strftime('%Y%m%d', time.localtime(time.time()))
    content = timestamp + '\t' + content + '\n'
    print(content)
    with open('.\\Logs\\' + filename + '.log', 'a+') as f:
        f.write(content)
    return content
   
def check_signal(okcoinSpot):
    #获取深度数据
    ok_depth = okcoinSpot.depth('btc_usd')
    ok_ask = ok_depth['asks'][-1][0]
    ok_bid = ok_depth['bids'][0][0]
    #获取K线数据（5min级别）
    ok_kline = okcoinSpot.kline('btc_usd','5min')
    Kline_high_288 = []
    for i in range(1,289):
        Kline_high_288.append(float(ok_kline[-i][2]))
    Kline_low_288 = []
    for i in range(1,289):
        Kline_low_288.append(float(ok_kline[-i][3])) 
    
    global signal
    signal = 0
    if ok_bid > max(Kline_high_288):
        signal = 1
    elif ok_ask < min(Kline_low_288):
        signal = -1
    else:
        signal = 0
    return signal

def buy(lst_coin,okcoinSpot):
    global buy_price
    ok_depth = okcoinSpot.depth('btc_usd')
    buy_price = ok_depth['asks'][-1][0]
    amount = total_pool/buy_price
    log('以%f价位买入btc数量%f,总价值 %f' %(buy_price,amount,total_pool))
    
def sell(lst_coin,okcoinSpot):
    global sell_price
    ok_depth = okcoinSpot.depth('btc_usd')
    sell_price = ok_depth['bids'][0][0]
    amount = total_pool/sell_price
    log('以%f价位买入btc数量%f,总价值 %f' %(buy_price,amount,total_pool))

def buy_clear(lst_coin,okcoinSpot):
    ok_depth = okcoinSpot.depth('btc_usd')
    sell_price1 = ok_depth['bids'][0][0]
    total_pool = sell_price1 * amount
    log('多单清仓价位%f,本单交易盈利%f,现在总价值%f' %(sell_price1,amount*(sell_price1-buy_price),total_pool))

def sell_clear(lst_coin,okcoinSpot):
    ok_depth = okcoinSpot.depth('btc_usd')
    buy_price1 = ok_depth['asks'][-1][0]
    total_pool = (sell_price - buy_price1)*amount + sell_price*amount
    log('空单清仓价位%f,本单交易盈利%f,现在总价值%f' %(buy_price1,amount*(sell_price-buy_price1),total_pool))
    
if __name__ == '__main__':
    #配置参数
    lst_coin = 'btc_usd'
    total_pool = 3000.0
    amount = 0.0
    empty = True    #空仓状态
    buy_side = False  #多单为空仓
    sell_side = False  #空单为空仓
    log('开始测试...初始资金：%d' %total_pool)
    
    while True:
        try:
            #现货API
            okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)
            check_signal(okcoinSpot)
            if empty == True and signal ==1:
                buy(lst_coin,okcoinSpot)
                buy_side = True
                empty = False
            elif empty == True and signal == -1:
                sell(lst_coin,okcoinSpot)
                sell_side = True
                empty = False
            elif empty == False and signal == -1 and buy_side == True:
                buy_clear(lst_coin,okcoinSpot)
                empty = True
                buy_side = False
            elif empty == False and signal == 1 and sell_side == True:
                sell_clear(lst_coin,okcoinSpot)
                empty = True
                sell_side = False
            else:
                pass
            log('5min后继续刷新交易,目前交易信号状态是%d' %signal )
            time.sleep(300)
        except Exception as ex:
            log('ERROR\t' + str(ex.args))
            time.sleep(300)
            continue