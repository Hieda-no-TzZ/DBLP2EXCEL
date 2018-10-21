from tools import *

isConf = input('查找会议(C)/期刊(J)：')
if str.upper(isConf)=='C':
    venue = input('请输入会议简称：')
    abbr = getTrueName(venue)
    if abbr==None:
        fullname = input('请输入会议全称：')
        adddict(venue, fullname)
    year = input('请输入年份：')
else:
    venue = input('请输入期刊简称：')
    abbr = getTrueName(venue)
    if abbr==None:
        fullname = input('请输入期刊全称：')
        adddict(venue, fullname)
    year = input('请输入年份：')
    volume = input('请输入卷号：')

Downloader(venue, year)