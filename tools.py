import requests
import json
import xlsxwriter
from bs4 import BeautifulSoup

isConf = True

def readDict():
    f = open('Names.txt', 'r')
    abbr2full = eval(f.read())
    f.close()
    return abbr2full

    # {
    # 'MOBICOM': 'ACM International Conference on Mobile Computing and Networking',
    # 'SIGCOMM': 'ACM International Conference on the applications, technologies, architectures, and protocols for computer communication',
    # 'INFOCOM': 'IEEE International Conference on Computer Communications',
    # 'ICNP': 'IEEE International Conference on Network Protocols',
    # 'SenSys': 'ACM Conference on Embedded Networked Sensor Systems',
    # 'CoNEXT': 'ACM International Conference on emerging Networking EXperiments and Technologies',
    # 'SECON': 'IEEE Communications Society Conference on Sensor and Ad Hoc Communications and Networks',
    # 'IPSN': 'International Conference on Information Processing in Sensor Networks',
    # 'MobiHoc': 'International Symposium on Mobile Ad Hoc Networking and Computing',
    # 'MobiSys': 'International Conference on Mobile Systems, Applications, and Services',
    # 'IWQoS': 'International Workshop on Quality of Service',
    # 'IMC': 'Internet Measurement Conference',
    # 'NOSSDAV': 'Network and Operating System Support for Digital Audio and Video',
    # 'NSDI': 'Symposium on Network System Design and Implementation',
    # # 期刊
    # 'TON': 'IEEE/ACM Transactions on Networking',
    # 'JSAC': 'IEEE Journal of Selected Areas in Communications',
    # 'TMC': 'IEEE Transactions on Mobile Computing'
    # }

def storeDict(abbr2full):
    f = open('Names.txt','w')
    f.write(str(abbr2full))
    f.close()

def adddict(abbr, full):
    abbr2full = readDict()
    abbr2full[str.upper(abbr)] = full
    storeDict(abbr2full)

# 将用户输入的简称正规化
def getTrueName(venue):
    abbr2full = readDict()
    for abbr in abbr2full.keys():
        if str.lower(abbr)==str.lower(venue):
            return abbr
    return None

# 由年份获得期刊卷号
def getVolume(venue, year):
    url = 'https://dblp.uni-trier.de/db/journals/'+str.lower(venue)+'/'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    volumes = soup.find('div', id='main').find('ul').find_all('a')
    for volume in volumes:
        text = volume.string
        if text.find(str(year))>=0:
            start = text.find(' ')+1
            end = text.find(':')
            return int(text[start, end])


header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36'}


def get_json_url(venue, year):
    return 'https://dblp.uni-trier.de/search/publ/api?q=toc%3Adb/conf/' + str.lower(venue) + '/' + str.lower(
        venue) + str(year) + '.bht%3A&format=json'

def filename(venue, year, volume=None):
    if volume:
        return venue + '-' + str(year)+'-'+str(volume)
    else:
        return venue + '-' + str(year)

# 下载json文件，保存到filename.json
def download_json(url, venue, year):
    print('downloading json...')
    venue = str.upper(venue)
    f = open(filename(venue, year) + '.json', 'w', encoding='utf-8')
    json_text = requests.get(url, headers=header).text
    f.write(json_text)
    f.close()
    print('json downloaded')

# json到xlsx转换
def json2xlsx(venue, year):
    abbr2full = readDict()
    print('创建 xlsx...')
    venue = str.upper(venue)
    json_file = open(filename(venue, year) + '.json', 'r')
    data = json.load(json_file)
    papers = data['result']['hits']['hit']

    # 创建xlsx格式文件
    book = xlsxwriter.Workbook(filename(venue, year) + '.xlsx')
    sheet = book.add_worksheet()

    sheet.write(0, 0, 'authors')
    sheet.write(0, 1, 'title')
    sheet.write(0, 2, 'conference/journal')
    sheet.write(0, 3, 'abbr')
    sheet.write(0, 4, 'page')
    sheet.write(0, 5, 'year')
    sheet.write(0, 6, 'url')
    sheet.write(0, 7, 'topic')
    sheet.write(0, 8, 'abstract')
    sheet.write(0, 9, 'written by')

    index = 0
    for paper in papers:
        index += 1
        info = paper['info']
        # 输入作者
        s = ''
        try:
            authors = info['authors']['author']
            for i in range(len(authors) - 1):
                s += authors[i] + ", "
            s += authors[len(authors) - 1]
        except KeyError:
            pass
        sheet.write(index, 0, s)

        # 输入标题
        s = info['title']
        sheet.write(index, 1, s)

        # 输入论文全称和简称
        sheet.write(index, 2, abbr2full[str.upper(venue)])
        sheet.write(index, 3, venue)

        # 输入页数
        s = info['pages']
        sheet.write(index, 4, s)

        # 输入年份
        sheet.write(index, 5, year)

        # 输入url
        url = info['ee']
        sheet.write(index, 6, url)

    book.close()
    print('xlsx generated')

# 不用了
def failedProcess(venue, fullname, year):
    adddict(venue, fullname)
    url = get_json_url(venue, year)
    download_json(url, venue, year)
    json2xlsx(venue, year)

# 获得显示页
def get_url(venue, year, volume=None):
    if isConf:
        return 'https://dblp.uni-trier.de/db/conf/'+str.lower(venue)+'/'+str.lower(venue)+str(year)+'.html'
    else:
        return 'https://dblp.uni-trier.de/db/journals/'+str.lower(venue)+'/'+str.lower(venue)+str(volume)+'.html'

def get_html(venue, url, year, volume=None):
    print('下载页面 '+url)
    f = open(filename(venue, year, volume)+'.html', 'w')
    html = requests.get(url).text
    f.write(html)
    f.close()
    print('页面下载完成')

def read_html(venue, year, volume=None):
    print('读取页面 '+filename(venue, year, volume)+'.html')
    f = open(filename(venue, year, volume)+'.html', 'r')
    html = f.read()
    f.close()
    return html

def parse_html(venue, html, year, volume):
    abbr2full = readDict()
    print('创建 '+filename(venue, year, volume) + '.xlsx')
    # 创建xlsx格式文件
    book = xlsxwriter.Workbook(filename(venue, year, volume) + '.xlsx')
    sheet = book.add_worksheet()

    bold = book.add_format({'bold': True})

    sheet.set_column('A:A', 30)
    sheet.write(0, 0, 'authors', bold)
    sheet.set_column('B:B', 40)
    sheet.write(0, 1, 'title', bold)
    sheet.set_column('C:C', 20)
    sheet.write(0, 2, 'conference/journal', bold)
    sheet.set_column('D:D', 8)
    sheet.write(0, 3, 'abbr', bold)
    sheet.set_column('E:E',10)
    sheet.write(0, 4, 'page', bold)
    sheet.set_column('F:F', 5)
    sheet.write(0, 5, 'year', bold)
    sheet.set_column('G:G', 5)
    sheet.write(0, 6, 'url', bold)
    sheet.set_column('H:H', 25)
    sheet.write(0, 7, 'topic', bold)
    sheet.set_column('I:I', 45)
    sheet.write(0, 8, 'abstract', bold)
    sheet.set_column('J:J', 11)
    sheet.write(0, 9, 'written by', bold)

    itemStyle = book.add_format({'text_wrap':1}) # 自动换行
    soup = BeautifulSoup(html, 'html.parser')
    publ_lists = soup.find_all('ul', class_='publ-list')
    index = 0
    number = 0
    for publ_list in publ_lists:
        number += 1
        if isConf:
            papers = publ_list.find_all('li', class_='entry inproceedings')
        else:
            papers = publ_list.find_all('li', class_='entry article')
        for paper in papers:
            index += 1
            # 解析作者名
            authors = paper.find_all('span', class_='', itemprop='name')
            s = ''
            try:
                for i in range(len(authors) - 1):
                    s += authors[i].string + ", "
                s += authors[len(authors) - 1].string
            except TypeError:
                print(authors)
                exit(1)
            sheet.write(index, 0, s, itemStyle)
            # 解析标题
            try:
                title = paper.find('span',class_="title").string
            except TypeError:
                print(title)
                exit(1)
            sheet.write(index, 1, title, itemStyle)
            # 输出会议全称简称
            sheet.write(index, 2, abbr2full[venue])
            sheet.write(index, 3, venue)
            # 解析页数
            try:
                page = paper.find('span', itemprop='pagination').string
                if not isConf:
                    page = str(volume)+'('+str(number)+'):'+page
            except AttributeError:
                index -= 1
                continue
            sheet.write(index, 4, page, itemStyle)
            # 输入年份
            sheet.write(index, 5, year)
            # 解析url
            url = paper.find('div', class_='head').find('a')['href']
            sheet.write(index, 6, url)
            # topic, abstract写空文字自动换行
            sheet.write(index, 7, ' ', itemStyle)
            sheet.write(index, 8, '', itemStyle)
    book.close()
    print('完成')

def Downloader(venue, year, volume=None):
    global isConf
    if volume==None:
        isConf = True
        print('下载会议 ' + venue + ' ' + str(year) + '年')
    else:
        isConf = False
        print('下载期刊 ' + venue + ' ' + str(year) + '年' + ' ' + str(volume) + '卷')
    url = get_url(venue, year, volume)
    get_html(venue, url, year, volume)
    html = read_html(venue, year, volume)
    parse_html(venue, html, year, volume)