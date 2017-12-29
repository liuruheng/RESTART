#coding=utf-8

import sys
import talib
import traceback
import numpy as np
import pandas as pd
from copy import deepcopy
import StrategyMisc
from resource import Constant
from resource import Configuration

"""
    策略算法模块：提供策略算法接口API
"""
def check_candlestick_pattern(periodName,dataWithId):
    """ 外部接口API: 蜡烛图组合图形的识别
        periodName: 周期名称的字符串
    """
    dataDealed = StrategyMisc.process_quotes_candlestick_pattern(periodName,dataWithId)

    for pattern in Constant.CANDLESTICK_PATTERN:# 遍历蜡烛图组合模型
        result = None
        dataCsv = deepcopy(dataDealed)
        try:
            result = getattr(talib, pattern)(np.float64(dataDealed['open'].values),\
                np.float64(dataDealed['high'].values),np.float64(dataDealed['low'].values),\
                np.float64(dataDealed['close'].values))
            # result是numpy.ndarray数据结构
            if len(result)!=0 and result.any()==True:
                dataCsv[pattern] = result # 增加蜡烛图组合模式的名称列
                csvFile=Configuration.get_period_working_folder(periodName)+'%s-%s.csv'%(periodName,pattern)
                dataCsv[dataCsv[pattern]!=0].to_csv(csvFile,encoding='utf-8')#转存csv文件

        except (Exception),e:
            exc_type,exc_value,exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))


def check_strategy(periodName,dataWithId):
    """ 外部接口API: 检测行情，依据策略生成相关指令
        periodName:周期名称字符串
        dataWithID: 来自行情数据库的dataframe结构数据
    """
    indx = Constant.QUOTATION_DB_PREFIX.index(periodName)
    # 微尺度周期不匹配蜡烛图模式（减少策略生成的频度）
    if Constant.SCALE_CANDLESTICK[indx] < Constant.DEFAULT_SCALE_CANDLESTICK_PATTERN:
        return

    check_candlestick_pattern(periodName,dataWithId)
