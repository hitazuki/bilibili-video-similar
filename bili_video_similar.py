import pymysql
import math
import jieba

conn = pymysql.connect(host='localhost', user='root', passwd='123456', db='bili_video', charset='utf8')
cur = conn.cursor()


#计算两个输入向量之间的余弦距离
def calcu_cos_distance(a, b):
    if len(a) != len(b):
        print('length unequal')
        return None
    part_up = 0.0
    a_sq = 0.0
    b_sq = 0.0
    for a1, b1 in zip(a,b):
        part_up += a1*b1
        a_sq += a1**2
        b_sq += b1**2
    part_down = math.sqrt(a_sq*b_sq)
    if part_down == 0.0:
        return 0.0
    else:
        return part_up / part_down


def get_avlist():
    sql = "SELECT av FROM video"
    cur.execute(sql)
    rows = cur.fetchall()
    avlist = []
    for i in range(len(rows)):
        avlist.append(rows[i][0])
    return avlist


def num_av_havetag(tag):
    sql = "SELECT count(*) FROM avtag WHERE tag = '%s'" \
          % (tag)
    cur.execute(sql)
    rows = cur.fetchall()
    return rows[0][0]


def num_av():
    sql = "SELECT count(*) FROM video"
    cur.execute(sql)
    rows = cur.fetchall()
    return rows[0][0]


def get_zone(av):
    sql = "SELECT zone1, zone2 FROM video where av = '%s'" \
          %(av)
    cur.execute(sql)
    rows = cur.fetchall()
    return (rows[0][0], rows[0][1])


def get_title(av):
    sql = "SELECT title FROM video where av = '%s'" \
          % (av)
    cur.execute(sql)
    rows = cur.fetchall()
    return (rows[0][0])


#根据原视频的标签计算一个视频的相似向量
def vec_similar(av, wordSet_m, idf, zone):
    #读取tag
    sql = "SELECT tag FROM avtag WHERE av = '%s'"\
          % (av)
    cur.execute(sql)
    rows = cur.fetchall()
    wordSet_s = set()
    for row in rows:
        wordSet_s.add(row[0].upper())

    #读取标题和分区，并将标题切分为关键词
    sql = "SELECT title, zone1, zone2 FROM video WHERE av = '%s'" \
          % (av)
    cur.execute(sql)
    rows = cur.fetchall()
    title = rows[0][0]
    title_segs = list(jieba.cut(title))
    for seg in title_segs:
        wordSet_s.add(seg)

    #根据分区计算向量
    vec_s = []
    for i in range(len(zone)):
        if rows[0][1+i] == zone[i]:
            vec_s.append(1.0)
        else:
            vec_s.append(0.0)

    #根据tag计算向量
    tf = []
    for tag in wordSet_m:
        if tag in wordSet_s:
            tf.append(1/len(wordSet_m))
        else:
            tf.append(0)

    for i in range(len(idf)):
        vec_s.append(tf[i]*idf[i])

    return vec_s


#计算原视频与其他视频的余弦距离，输出值最大的10个视频
def similar(av):
    #读取主分区和子分区
    zone = get_zone(av)
    print('zone:', zone)
    #取得关键词集合
    sql = "SELECT tag FROM avtag WHERE av = '%s'"\
          %(av)
    cur.execute(sql)
    rows = cur.fetchall()
    wordSet = set()
    for row in rows:
        wordSet.add(row[0].upper())
    print('tag:', wordSet)

    tf_m = []
    for i in range(len(wordSet)):
        tf_m.append(1/len(wordSet))
    print('tf_m:', tf_m)

    N = num_av()
    print('N:', N)

    Nt = []
    for tag in wordSet:
        Nt.append(num_av_havetag(tag))
    print('Nt:', Nt)

    idf = []
    for i in range(len(Nt)):
        idf.append(math.log(N/Nt[i]))
    print('idf:', idf)

    vec_m = [1.0, 1.0]
    for i in range(len(tf_m)):
        vec_m.append(tf_m[i]*idf[i])
    print('vec_m:', vec_m)

    #计算余弦距离
    res = []
    avlist = get_avlist()
    for i in avlist:
        cos = calcu_cos_distance(vec_m, vec_similar(i, wordSet, idf, zone))
        for j in range(len(res)):
            if cos > res[j][1]:
                res.insert(j, (i,cos))
                break
        else:
            if len(res) <= 10:
                res.append((i,cos))
        if len(res) > 10:
            res.pop()

    print('similar top 10:')
    print(res[0:5])
    print(res[5:10])

if __name__ == "__main__":
    av = input('请输入视频号：')
    print('title:', get_title(av))
    similar(av)