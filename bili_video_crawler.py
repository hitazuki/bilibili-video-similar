import requests
import pymysql
import bs4
import random
from multiprocessing.dummy import Pool as ThreadPool

# 收集到的Header
user_agent = [
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; msn OptimizedIE8;ZHCN)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Zune 4.0; Tablet PC 2.0; InfoPath.3; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; chromeframe/11.0.696.57)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:2.0b10) Gecko/20110126 Firefox/4.0b10",
    "Mozilla/5.0 (Windows; Windows NT 5.1; es-ES; rv:1.9.2a1pre) Gecko/20090402 Firefox/3.6a1pre",
    "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.7) Gecko/20100723 Fedora/3.6.7-1.fc13 Firefox/3.6.7",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; ko; rv:1.9.2.4) Gecko/20100523 Firefox/3.6.4"
]


#处理带引号的标题使数据库能够读入
def addslashes(s):
    d = {'"': '\\"', "'": "\\'", "\0": "\\\0", "\\": "\\\\"}
    return ''.join(d.get(c, c) for c in s)



urls = []
#输入要爬取的av号
for i in range(6521000,6600000):
    url = 'https://www.bilibili.com/video/av' + str(i)
    urls.append(url)


def crawler(url):
    av = url.replace("https://www.bilibili.com/video/av", "")
    #print('crawler', av)
    my_header = {"User-Agent":random.choice(user_agent)}
    res = requests.get(url, headers = my_header)
    res.encoding = 'utf-8'
    soup = bs4.BeautifulSoup(res.text, 'lxml')

    try:
        title = soup.select('#viewbox_report > h1')[0].text
        title_slash = addslashes(title)

        v_zone = soup.select('#viewbox_report > div > .crumb')
        zone = []
        for i in range(1,len(v_zone)):
            zone.append(v_zone[i].text.split()[0])  #除去后缀" > "

        v_tag = soup.select('div#v_tag > ul > li')
        tag = []
        for i in range(len(v_tag)):
            tag.append(v_tag[i].text)

        #print(av)
        #print(title)
        #print(title_slash)
        #print(zone)
        #print(tag)

        try:
            # insert data into MySQL.
            conn = pymysql.connect(
                host='localhost', user='root', passwd='123456', db='bili_video', charset='utf8')
            cur = conn.cursor()
            cur.execute('INSERT INTO video(av, title, zone1, zone2) \
            VALUES ("%s","%s","%s","%s")'
                        %
                        (av, title_slash, zone[0], zone[1]))
            for i in range(len(tag)):
                cur.execute('INSERT INTO avtag(av, tag) \
                        VALUES ("%s","%s")'
                            %
                            (av, tag[i]))
            conn.commit()
            print('insert', av, 'succeed')
        except Exception as e:
            print(e,av)

    except Exception as e:
        print(e,av)



if __name__ == "__main__":
    pool = ThreadPool(10)
    try:
        results = pool.map(crawler, urls)
    except Exception as e:
        print(e)
        print('thread error')

    pool.close()
    pool.join()

