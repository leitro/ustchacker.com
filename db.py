'''
'''
import sqlite3
import time
import hashlib
import random
import urllib.parse

db = sqlite3.connect('hacker.db')  # 表格:user chat blog comment
c = db.cursor()


def newsFlagInit(name):
    c.execute('insert into newsFlag(name,flag) values("' + name + '","yes")')
    db.commit()


def getTime():
    t = time.localtime()
    res = str(t.tm_hour) + ':' + str(t.tm_min) + ':' + str(t.tm_sec)
    return res


def insert(mail, name, pw, score=0):
    regtime = time.ctime()
    c.execute('insert into user(name,pw,score,regtime) values("' +
              name + '","' + pw + '",' + str(score) + ',"' + regtime + '")')
    db.commit()
    preid = name + pw + regtime
    m = hashlib.md5(preid.encode('utf8'))
    secretid = m.hexdigest()

    code = name + regtime + 'fuckU'
    m2 = hashlib.md5(code.encode('utf8'))
    md5code = m2.hexdigest() + '.' + str(random.randint(11111111, 99999999))
    c.execute('insert into loginid(mail,name,secretid,verify,verifyCode) values("' +
              mail + '","' + name + '","' + secretid + '","False","' + md5code + '")')
    db.commit()
    rank = getRank(name, score)
    updateRank(name, rank)
    newsFlagInit(name)
    return secretid


def update(name, **info):
    res = ''
    for i in info.items():
        if i[1]:  # 如果更改设置的时候没有更改某项则此项为None
            res += (i[0] + '="' + i[1] + '",')
    res = res[:-1]
    if res:
        c.execute('update user set ' + res + ' where name="' + name + '"')
        db.commit()


def verifyMail(mail, code):
    c.execute('select name,verifyCode from loginid where mail="' + mail + '"')
    data = c.fetchall()
    if data == []:
        return False
    else:
        name = data[0][0]
        verifyCode = data[0][1]
        if code == verifyCode:
            c.execute(
                'update loginid set verify="True" where name="' + name + '"')
            db.commit()
            return True
        else:
            return False


def whetherVerified_name(name):
    c.execute('select verify from loginid where name="' + name + '"')
    res = c.fetchall()
    if res == []:
        return False
    else:
        if res[0][0] == 'True':
            return True
        elif res[0][0] == 'False':
            return False


def getVerifyCode(mail):
    c.execute('select verifyCode from loginid where mail="' + mail + '"')
    res = c.fetchall()
    if res == []:
        return False
    else:
        return res[0][0]


def getMailName(mail):
    c.execute('select name from loginid where mail="' + mail + '"')
    res = c.fetchall()
    if res == []:
        return False  # 此邮箱没有被使用过
    else:
        return res[0][0]  # 返回使用该邮箱的用户名


def fetchID(name):
    if not name:
        return None
    c.execute('select * from loginid')
    data = c.fetchall()
    for i in data:
        if i[2] == name:
            return i[3]
    return None  # 未注册用户返回None


def fetchName(userid):
    if not userid:
        return None
    c.execute('select * from loginid')
    data = c.fetchall()
    for i in data:
        if i[3] == userid:
            return i[2]
    return None  # 没有此ID


def fetchMail(userid):
    if not userid:
        return None
    c.execute('select * from loginid')
    data = c.fetchall()
    for i in data:
        if i[3] == userid:
            return i[1]
    return None  # 没有此ID


def check(name, pw=None):
    c.execute('select * from user')
    data = c.fetchall()
    if not pw:  # 没有密码，则查询用户是否存在
        for i in data:
            if name == i[1]:
                return True
        return False
    else:  # 存在密码，则查询用户名和密码是否对应
        for i in data:
            if name == i[1]:
                if pw == i[2]:
                    return True
                else:
                    return False
        return False  # 都不存在这个用户


def checkMail(mail):
    c.execute('select name from loginid where mail="' + mail + '"')
    res = c.fetchall()
    if not res:
        return False  # 邮箱没有注册 此时res是[]
    else:
        return True


def getScore(name):
    c.execute('select score from user where name="' + name + '"')
    data = c.fetchall()
    return data[0][0]

'''
每个用户的rank不是实时更新的，当刷新用户页面时才更新该
用户的rank排名，点击member成员页面的时候只是按score由大
到小排列，并不更新rank字段。

这里留个性能问题，以后解决：
我其实每次显示排名的时候调用getRank函数都是根据score排序
实时获得的，所以并不需要updateRank的过程，user表中也不需
要保存rank字段，但是每次都实时排名性能不优，比如csdn中的
排名就是每天更新一次的，这个以后去改进。
'''


def getRank(name, score):
    c.execute('select name,score from user order by score desc')
    data = c.fetchall()
    # data.sort(key=lambda x:x[1],reverse=True)
    return data.index((name, score)) + 1


def updateRank(name, rank):  # 执行updateScore时和注册用户时
    c.execute('update user set rank=' +
              str(rank) + ' where name="' + name + '"')
    db.commit()


def updateScore(name, plusScore):
    c.execute('select score from user where name="' + name + '"')
    score = c.fetchall()[0][0]
    score += plusScore
    c.execute('update user set score=' +
              str(score) + ' where name="' + name + '"')
    db.commit()
    rank = getRank(name, score)
    updateRank(name, rank)


def updatePw(name, pw):  # 只能用户来更新密码
    c.execute('update user set pw="' + pw + '" where name="' + name + '"')
    db.commit()
    regtime = time.ctime()
    preid = name + pw + regtime
    m = hashlib.md5(preid.encode('utf8'))
    secretid = m.hexdigest()
    c.execute('update loginid set secretid="' +
              secretid + '" where name="' + name + '"')
    db.commit()


def show():
    c.execute('select * from user')
    return c.fetchall()


def showMember():
    c.execute('select name,score,rank from user order by score desc')
    return c.fetchall()


def showUser(name):
    c.execute('select * from user where name="' + name + '"')
    return c.fetchall()[0]


def insertChat(name, content):
    now = time.ctime()
    c.execute(
        'insert into chat(name,content,time) values("' + name + '","' + content + '","' + now + '")')
    db.commit()


def showChat():
    c.execute('select * from chat')
    tmp = c.fetchall()
    return tmp[::-1]  # 逆序，最新贴放在最上面


def showBlogCategory(idvalue):
    c.execute('select category from blog where id=' + idvalue)
    return c.fetchall()[0][0]


def showBlogAuthor(idvalue):
    c.execute('select name from blog where id=' + idvalue)
    return c.fetchall()[0][0]


def insertBlog(name, title, blog, tag, category):
    now = time.ctime()
    c.execute('insert into blog(name,title,blog,time,tag,category,upCount) values("' +
              name + '","' + title + '","' + blog + '","' + now + '","' + tag + '","' + category + '",0)')
    db.commit()
    c.execute('select max(id) from blog')
    return c.fetchone()[0]  # 新插入数据的id


def delBlog(blogid):
    c.execute('delete from blog where id=' + blogid)
    db.commit()
    c.execute('delete from up where blogid=' + blogid)
    db.commit()
    c.execute('delete from comment where blogid=' + blogid)
    db.commit()


def updateBlog(blogid, title, blog, tag, category):
    c.execute('update blog set title="' + title + '",blog="' + blog +
              '",tag="' + tag + '",category="' + category + '" where id=' + blogid)
    db.commit()


def showOneBlog(idvalue):
    c.execute('select * from blog where id=' + idvalue)
    return c.fetchall()[0]


def showOneBlogTitle(idvalue):
    c.execute('select title from blog where id=' + idvalue)
    title = c.fetchall()[0][0]
    title = urllib.parse.unquote(title)
    return title


def showUserBlog(name):
    c.execute('select id,name,title,time,tag,category from blog where name="' +
              name + '" and category!="ask"')
    tmp = c.fetchall()
    return tmp[::-1]


def showUserBlogID(name):
    c.execute('select id from blog where name="' + name + '"')
    data = c.fetchall()
    return [i[0] for i in data]


def showUserAsk(name):
    c.execute('select id,name,title,time,tag,category from blog where name="' +
              name + '" and category="ask"')
    tmp = c.fetchall()
    return tmp[::-1]


def showAllBlog(tag, order):
    if not tag:
        if order == 'latest':
            c.execute(
                'select id,name,title,time,tag,category,upCount from blog where category!="ask"')
            tmp = c.fetchall()
            return tmp[::-1]
        else:  # hottest
            c.execute(
                'select id,name,title,time,tag,category,upCount from blog where category!="ask" order by upCount desc')
            tmp = c.fetchall()
            return tmp
    else:
        if order == 'latest':
            c.execute(
                'select id,name,title,time,tag,category,upCount from blog where tag="' + tag + '" and category!="ask"')
            tmp = c.fetchall()
            return tmp[::-1]
        else:  # hottest
            c.execute('select id,name,title,time,tag,category,upCount from blog where tag="' +
                      tag + '" and category!="ask" order by upCount desc')
            tmp = c.fetchall()
            return tmp


def showAllAsk(tag, order):
    if not tag:
        if order == 'latest':
            c.execute(
                'select id,name,title,time,tag,category,upCount from blog where category="ask"')
            tmp = c.fetchall()
            return tmp[::-1]
        else:  # hottest
            c.execute(
                'select id,name,title,time,tag,category,upCount from blog where category="ask" order by upCount desc')
            tmp = c.fetchall()
            return tmp
    else:
        if order == 'latest':
            c.execute(
                'select id,name,title,time,tag,category,upCount from blog where tag="' + tag + '" and category="ask"')
            tmp = c.fetchall()
            return tmp[::-1]
        else:  # hottest
            c.execute('select id,name,title,time,tag,category,upCount from blog where tag="' +
                      tag + '" and category="ask" order by upCount desc')
            tmp = c.fetchall()
            return tmp


def addComment(blogid, name, comment):
    now = time.ctime()
    c.execute('insert into comment(blogid,name,comment,time) values(' +
              blogid + ',"' + name + '","' + comment + '","' + now + '")')
    db.commit()
    author = getBlogAuthor(blogid)
    c.execute('update newsFlag set flag="no" where name="' + author + '"')
    db.commit()


def showComment(blogid):
    c.execute('select * from comment where blogid=' + blogid)
    return c.fetchall()


def showCommentMsg(author):
    blogids = showUserBlogID(author)
    result = []
    for i in blogids:
        c.execute('select blogid,name from comment where blogid=' + str(i))
        data = c.fetchall()
        if data:
            title = showOneBlogTitle(str(i))
            result.append((data[0][0], data[0][1], title))
        else:
            pass
    return result[::-1]


def blogUpCountPlus(blogid):
    c.execute('select upCount from blog where id=' + blogid)
    upCount = int(c.fetchall()[0][0])
    upCount += 1
    c.execute('update blog set upCount=' +
              str(upCount) + ' where id=' + blogid)
    db.commit()


def addUp(blogid, name):  # 点赞
    c.execute(
        'insert into up(blogid,name) values(' + blogid + ',"' + name + '")')
    db.commit()
    author = getBlogAuthor(blogid)
    c.execute('update newsFlag set flag="no" where name="' + author + '"')
    db.commit()
    blogUpCountPlus(blogid)


def showUp(blogid):
    c.execute('select name from up where blogid=' + blogid)
    ups = c.fetchall()
    return [x[0] for x in ups]


def showUpMsg(author):
    blogids = showUserBlogID(author)
    result = []
    for i in blogids:
        c.execute('select blogid,name from up where blogid=' + str(i))
        data = c.fetchall()
        if data:
            title = showOneBlogTitle(str(i))
            result.append((data[0][0], data[0][1], title))
        else:
            pass
    return result[::-1]


def readNews(name):
    c.execute('select flag from newsFlag where name="' + name + '"')
    data = c.fetchall()
    if data[0][0] == 'no':
        return False
    else:
        return True


def setFlagYes(author):
    c.execute('update newsFlag set flag="yes" where name="' + author + '"')
    db.commit()


def checkUp(blogid, name):
    data = showUp(blogid)
    if name in data:
        return True
    else:
        return False


def follow(selfname, name):
    c.execute(
        'insert into follow(name,follow) values("' + selfname + '","' + name + '")')
    db.commit()
    c.execute(
        'insert into fan(name,fan) values("' + name + '","' + selfname + '")')
    db.commit()


def unfollow(selfname, name):
    c.execute('delete from follow where name="' +
              selfname + '" and follow="' + name + '"')
    db.commit()
    c.execute('delete from fan where name="' +
              name + '" and fan="' + selfname + '"')
    db.commit()


def showFans(name):
    c.execute('select fan from fan where name="' + name + '"')
    fans = c.fetchall()
    res = []
    for i in fans:
        res.append(i[0])
    return res


def showFollows(name):
    c.execute('select follow from follow where name="' + name + '"')
    follows = c.fetchall()
    res = []
    for i in follows:
        res.append(i[0])
    return res


def hasHeadPic(name):
    c.execute('select headpic from user where name="' + name + '"')
    data = c.fetchall()
    if data[0][0]:
        return True
    else:
        return False


def getHeadPic(name):
    c.execute('select headpic from user where name="' + name + '"')
    data = c.fetchall()
    if data[0][0]:
        return data[0][0]
    else:
        return 'static/head/default.png'


def getBlogAuthor(blogid):
    c.execute('select name from blog where id=' + blogid)
    return c.fetchall()[0][0]


def showMessage(name):
    commentMsg = showCommentMsg(name)
    upMsg = showUpMsg(name)
    return commentMsg, upMsg


def insertAdmin(link, flag):
    # flag:system--USTC Hacker资讯  nice--推荐文章
    c.execute(
        'insert into adminTable(link,flag) values("' + link + '","' + flag + '")')
    db.commit()


def getAdmin(flag):
    c.execute('select link,flag from adminTable where flag="' + flag + '"')
    return c.fetchall()[::-1]


def delAdmin(link):
    c.execute('delete from adminTable where link="' + link + '"')
    db.commit()


def addLink(url, title):
    c.execute('insert into link(url,title) values("%s", "%s")' % (url, title))
    db.commit()


def showLink():
    c.execute('select url,title from link')
    return c.fetchall()

if __name__ == '__main__':
    pass
