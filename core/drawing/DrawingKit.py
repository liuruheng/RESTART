#coding=utf-8
import sys
import csv
import sqlite3
import datetime
import traceback
import platform
if (platform.system() == "Linux"):#适配Linux系统下运行环境
    import matplotlib
    matplotlib.use("Pdf")

import matplotlib.pyplot as plt
from pandas import DataFrame
from matplotlib.finance import candlestick_ohlc
from matplotlib.dates import DateFormatter
from matplotlib.dates import MinuteLocator,HourLocator,DayLocator,WeekdayLocator
import DrawingMisc
from resource import Constant
from resource import Configuration
from quotation import QuotationKit

def show_candlestick(quotes, periodName, isDraw):
    """ 内部接口API:
        quotes: 数据序列。参照finance类中candlestick_ohlc()方法的入参说明。
        periodName: 周期名称的字符串。
    """
    # 定义相关周期坐标的锚定对象。为了显示清楚锚定值要大于本周期值。
    fiveMinLocator = MinuteLocator(interval=30)
    fifteenMinLocator = MinuteLocator(interval=60)
    thirtyMinLocator = MinuteLocator(interval=120)
    oneHourLocator = HourLocator(interval=4)
    twoHourLocator = HourLocator(interval=8)
    fourHourLocator = HourLocator(interval=16)
    sixHourLocator = HourLocator(interval=24)
    twelveHourLocator = HourLocator(interval=48)

    oneDayLocator = DayLocator(interval=2)
    oneWeekLocator = WeekdayLocator(interval=1)

    # 坐标横轴锚定对象列表
    axLocatorList = [None, fiveMinLocator, fifteenMinLocator, thirtyMinLocator,\
        oneHourLocator,twoHourLocator,fourHourLocator,sixHourLocator,twelveHourLocator,\
        oneDayLocator,oneWeekLocator]

    # 定义相关的格式对象。DateFormatter接收的格式化字符与`strftime`相同（参见DateFormatter类定义）
    fiveMinFormatter = fifteenMinFormatter = thirtyMinFormatter = \
        oneHourFormatter = twoHourFormatter = DateFormatter('%H:%M')
    fourHourFormatter = sixHourFormatter = DateFormatter('%b%d %H:%M')
    twelveHourFormatter = oneDayFormatter = DateFormatter('%b %d')
    oneWeekFormatter = DateFormatter('%Y-%m-%d')

    # 坐标横轴格式对象列表
    axFormatterList = [None,fiveMinFormatter, fifteenMinFormatter, thirtyMinFormatter,\
        oneHourFormatter, twoHourFormatter, fourHourFormatter, sixHourFormatter,\
        twelveHourFormatter, oneDayFormatter, oneWeekFormatter]

    fig, ax = plt.subplots(figsize=(20,5))
    fig.subplots_adjust(bottom=0.2)

    # 获取序号--坐标横轴的锚定对象和格式对象列表下标。
    index = Constant.QUOTATION_DB_PREFIX.index(periodName)

    ax.xaxis.set_major_locator(axLocatorList[index])
    ax.xaxis.set_major_formatter(axFormatterList[index])

    try:
        # 设置坐标横轴的起止位置。参见numpy.ndarray类的处理方法。
        ax.set_xlim([quotes.item(0,0),quotes.item(-1,0)])
        candlestick_ohlc(ax, quotes,width=0.001,colorup='red',colordown='green')
        # 坐标横轴锚定数目太多，为避免报错直接返回。
        if len(ax.get_xticklabels()) >= max(Constant.CANDLESTICK_PERIOD_CNT):
            return

        ax.grid(True)

        if (platform.system() == "Windows"):#Linux环境下不进行下列优化
            plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
        plt.title(periodName)
        timestamp = datetime.datetime.now().strftime('%b%d_%H_%M')
        plt.savefig('%s%s-%s.png'%(Configuration.get_period_working_folder(periodName),periodName,timestamp),dpi=200)
        if isDraw == True:
            plt.show()
    except (Exception),e:
        exc_type,exc_value,exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
        traceback.print_exc(file=open(Configuration.get_working_directory()+'trace.txt','a'))

def show_period_candlestick(periodName,dataWithId,isDraw=False):
    """ 外部接口API:
        periodName:周期名称的字符串（用于计算蜡烛图展示根数）
        dataWithId:行情数据库中dateframe结构的数据。
        isDraw:是否展示图画的标志。对于后台运行模式默认不展示。
    """
    # 为降低系统负荷和增加实时性，对于零/小尺度周期的蜡烛图不再实时绘制
    indx = Constant.QUOTATION_DB_PREFIX.index(periodName)
    if Constant.SCALE_CANDLESTICK[indx] < Constant.DEFAULT_SCALE_CANDLESTICK_SHOW:
        return
    dataPicked = DrawingMisc.process_quotes_drawing_candlestick(periodName,dataWithId)
    show_candlestick(dataPicked,periodName,isDraw)

def show_period_candlestick_withCSV(index,path,cnt=-1,isDraw=False):
    """ 外部接口API:通过CSV文件进行绘制。
        参数说明类同于show_period_candlestick()方法。
    """
    data = []
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            t = row['time'].replace('/','-')#csv文件中时间存储方式需要加以处理
            data.append([int(row['id']),t,float(row['open']),float(row['high']),float(row['low']),float(row['close'])])

    title = ['id'] + map(lambda x:x , Constant.QUOTATION_STRUCTURE)
    dataframe = DataFrame(data,columns=title)

    # 组装数据进行加工
    dataPicked = DrawingMisc.process_quotes_drawing_candlestick(index,path,dataframe)
    show_candlestick(dataPicked,path,isDraw)
