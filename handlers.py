from db import *
from mdFilter import *
from sendMail import *
import tornado.web
import urllib.parse
import rootAdminName


class mainHandler(tornado.web.RequestHandler):

    def get(self):
        self.redirect('/index/1_1')

    def post(self):
        name = self.get_argument('username')
        pw = self.get_argument('password')
        verified = whetherVerified_name(name)
        if verified:  # 如果邮箱已经验证过，密码正确加cookie登录成功
            res = check(name, pw)
            if res:  # 密码正确
                userid = fetchID(name)
                self.set_cookie('hackerID', userid)
            else:  # 密码错误
                pass
        self.redirect('/')


class indexHandler(tornado.web.RequestHandler):

    def get(self, page):
        userid = self.get_cookie('hackerID')
        username = fetchName(userid)
        res = page.split('_')
        if len(res) < 2:
            self.redirect('/error')
        elif len(res) > 2:  # 12_34_hottest 最热文章,其余默认最新文章
            order = 'hottest'
            blogPage = res[0]
            askPage = res[1]
            blogs = showAllBlog(None, order)
            blogs_ask = showAllAsk(None, order)
        else:
            order = 'latest'
            blogPage, askPage = page.split('_')
            blogs = showAllBlog(None, order)
            blogs_ask = showAllAsk(None, order)
        blogs_new = []
        blogs_ask_new = []
        for i in blogs:
            i = list(i)
            i[2] = urllib.parse.unquote(i[2])
            blogs_new.append(i)
        for i in blogs_ask:
            i = list(i)
            i[2] = urllib.parse.unquote(i[2])
            blogs_ask_new.append(i)
        blogNum = len(blogs)
        askNum = len(blogs_ask)

        ustcInfo = []
        niceBlog = []
        systemLinks = getAdmin('system')
        for i in systemLinks:
            blogid = i[0].split('/')[-1]
            title = showOneBlogTitle(blogid)
            ustcInfo.append([title, blogid])
        niceLinks = getAdmin('nice')
        for i in niceLinks:
            blogid = i[0].split('/')[-1]
            title = showOneBlogTitle(blogid)
            niceBlog.append([title, blogid])
        friendLinks = showLink()

        self.render(
            'index.html', cookieName=username, blogs=blogs_new, blogs_ask=blogs_ask_new, blogNum=blogNum,
                    askNum=askNum, blogPage=blogPage, askPage=askPage, order=order, ustcInfo=ustcInfo, niceBlog=niceBlog, friendLinks=friendLinks)


class memberHandler(tornado.web.RequestHandler):

    def get(self, page):
        userid = self.get_cookie('hackerID')
        username = fetchName(userid)
        users = showMember()
        userNum = len(users)
        self.render('member.html', cookieName=username,
                    users=users, userNum=userNum, page=page)


class chatHandler(tornado.web.RequestHandler):

    def get(self, num):  # num第几页
        userid = self.get_cookie('hackerID')
        username = fetchName(userid)
        chats = showChat()
        newChats = []
        for i in chats:
            i = list(i)
            i[2] = urllib.parse.unquote(i[2])
            newChats.append(i)
        n = len(newChats)
        if n % 20 == 0:
            pages = n // 20  # pages总页数
        else:
            pages = n // 20 + 1
        self.render('chat.html', cookieName=username,
                    content=newChats, pages=pages, num=num)


class chattingHandler(tornado.web.RequestHandler):

    def get(self, num):
        userid = self.get_cookie('hackerID')
        username = fetchName(userid)
        self.render('chatting.html', cookieName=username, num=num)

    def post(self, num):
        userid = self.get_cookie('hackerID')
        if userid:
            username = fetchName(userid)
            newTopic = self.get_argument('topic')
            newTopic = urllib.parse.quote(newTopic)
            insertChat(username, newTopic)
            self.redirect('/chatting/1')
        else:
            self.redirect('/register')


class registerHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('register.html', sameName=False, sameMail=False)

    def post(self):
        mail = self.get_argument('mail')
        name = self.get_argument('username')
        pw = self.get_argument('password')
        res = check(name)
        res2 = checkMail(mail)
        if res or res2:  # 用户名已存在
            self.render('register.html', sameName=res, sameMail=res2)
        else:
            userid = insert(mail, name, pw)
            self.redirect('/sendMail?mail=' + mail)


class logoutHandler(tornado.web.RequestHandler):

    def get(self):
        self.clear_cookie('hackerID')
        self.redirect('/')


class postHandler(tornado.web.RequestHandler):

    def get(self):
        userid = self.get_cookie('hackerID')
        username = fetchName(userid)
        self.render('post.html', cookieName=username)

    def post(self):
        tag = self.get_argument('tag')
        category = self.get_argument('category')
        title = self.get_argument('title')
        title = urllib.parse.quote(title)
        blog_md = self.get_argument('blog')
        blog = urllib.parse.quote(blog_md)  # 要把"等符号都编码一下，再录入数据库
        userid = self.get_cookie('hackerID')
        name = fetchName(userid)
        idvalue = insertBlog(name, title, blog, tag, category)
        if category == 'new':
            updateScore(name, 20)  # 新发表一篇文章+20分
        elif category == 'reprint':
            updateScore(name, 5)  # 转载一篇文章+5分
        elif category == 'ask':
            updateScore(name, 5)  # 提问+5分
        self.redirect('/blog/' + str(idvalue))


class userHandler(tornado.web.RequestHandler):

    def get(self, username):  # 查看username的主页
        selfid = self.get_cookie('hackerID')
        selfname = fetchName(selfid)
        mail = fetchMail(selfid)
        blogs = showUserBlog(username)
        blogs_ask = showUserAsk(username)
        blogs_new = []
        blogs_ask_new = []
        for i in blogs:
            i = list(i)
            i[2] = urllib.parse.unquote(i[2])
            blogs_new.append(i)
        for i in blogs_ask:
            i = list(i)
            i[2] = urllib.parse.unquote(i[2])
            blogs_ask_new.append(i)
        info = showUser(username)
        level = info[3]
        sex = info[4]
        if sex == '0':
            sex = '女'
        else:
            sex = '男'
        birthday = info[5]
        city = info[6]
        intro = info[7]
        regtime = info[8]
        headpic = info[9]
        fans = showFans(username)
        fansN = len(fans)
        follows = showFollows(username)
        followsN = len(follows)
        score = getScore(username)
        rank = getRank(username, score)
        self.render('user.html', headpic=headpic,
                cookieName=selfname, user=username, blogs=blogs_new,
                blogs_ask=blogs_ask_new, mail=mail, level=level, sex=sex,
                birthday=birthday, city=city, intro=intro,
                regtime=regtime, fans=fans, follows=follows,
                fansN=fansN, followsN=followsN, rank=rank,
                score=score)


class blogHandler(tornado.web.RequestHandler):

    def get(self, idvalue):
        selfid = self.get_cookie('hackerID')
        selfname = fetchName(selfid)
        blog = showOneBlog(idvalue)
        username = blog[1]
        blogTitle = urllib.parse.unquote(blog[2])
        blogContent_md = urllib.parse.unquote(blog[3])
        blogContent = translate(blogContent_md)
        blogTime = blog[4]
        blogTag = blog[5]
        blogCategory = blog[6]
        info = showUser(username)
        city = info[6]
        intro = info[7]
        headpic = info[9]
        comments = showComment(idvalue)
        newComments = []
        for i in comments:
            i = list(i)
            i[3] = urllib.parse.unquote(i[3])
            newComments.append(i)

        ups = showUp(idvalue)
        upsN = len(ups)
        score = getScore(username)
        rank = getRank(username, score)
        fans = showFans(username)
        self.render(
            'blog.html', cookieName=selfname, username=username, blogTitle=blogTitle, blogContent=blogContent, blogTime=blogTime, blogTag=blogTag, blogCategory=blogCategory,
                    comments=newComments, ups=ups, upsN=upsN, city=city, intro=intro, headpic=headpic, user=username, score=score, rank=rank, fans=fans, idvalue=idvalue)


class commentHandler(tornado.web.RequestHandler):

    def post(self):
        selfid = self.get_cookie('hackerID')
        if selfid:
            selfname = fetchName(selfid)
            comment = self.get_argument('comment')
            refer = self.request.headers.get('referer')
            for i in range(len(refer) - 1, 0, -1):
                if refer[i] == '/':
                    break
            blogid = refer[i + 1:]
            comment = urllib.parse.quote(comment)
            addComment(blogid, selfname, comment)
            self.redirect('/blog/' + blogid)
        else:
            self.redirect('/register')


class settingHandler(tornado.web.RequestHandler):

    def get(self, para):
        selfid = self.get_cookie('hackerID')
        selfmail = fetchMail(selfid)
        selfname = fetchName(selfid)
        info = showUser(selfname)
        sex = info[4]
        birthday = info[5]
        city = info[6]
        intro = info[7]
        if para == 'info':
            self.render('setting.html', userMail=selfmail, cookieName=selfname,
                        sex=sex, birthday=birthday, city=city, intro=intro, sameMail=False)
        elif para == 'pw':
            self.render('pw.html', cookieName=selfname, sameOldPw=True)

    def post(self, para):
        selfid = self.get_cookie('hackerID')
        selfname = fetchName(selfid)
        if para == 'info':
            headpicList = self.request.files.get('headpic')
            if headpicList:
                picType = headpicList[0]['content_type']
                picType = picType.split('/')
                if picType[0] == 'image':
                    headpic = 'static/head/' + selfid + '.' + picType[-1]
                    f = open(headpic, 'wb')
                    f.write(headpicList[0]['body'])
                    f.close()
            else:
                if hasHeadPic(selfname):
                    headpic = None
                else:
                    headpic = 'static/head/default.png'
            sex = self.get_argument('sex')
            birthday = self.get_argument('birth')
            city = self.get_argument('city')
            intro = self.get_argument('intro')

            update(selfname, sex=sex, birthday=birthday,
                   city=city, intro=intro, headpic=headpic)
            self.redirect('/user/' + selfname)
        elif para == 'pw':
            oldpw = self.get_argument('oldpw')
            newpw = self.get_argument('newpw')
            newpw2 = self.get_argument('newpw2')
            res = check(selfname, oldpw)
            if not res:
                self.render('pw.html', cookieName=selfname, sameOldPw=False)
            else:
                updatePw(selfname, newpw)
                self.render('changePwDone.html', cookieName=selfname)


class followHandler(tornado.web.RequestHandler):

    def post(self, idol):
        selfid = self.get_cookie('hackerID')
        if selfid:
            selfname = fetchName(selfid)
            refer = self.request.headers.get('Referer')
            path = urllib.parse.urlparse(refer).path
            follow(selfname, idol)
            self.redirect(path)
        else:
            self.redirect('/register')


class tagHandler(tornado.web.RequestHandler):

    def get(self, tag, page):
        userid = self.get_cookie('hackerID')
        username = fetchName(userid)
        res = page.split('_')
        if len(res) > 2:  # 12_34_hottest 最热文章,其余默认最新文章
            order = 'hottest'
            blogPage = res[0]
            askPage = res[1]
            blogs = showAllBlog(tag, order)
            blogs_ask = showAllAsk(tag, order)
        else:
            order = 'latest'
            blogPage, askPage = page.split('_')
            blogs = showAllBlog(tag, order)
            blogs_ask = showAllAsk(tag, order)
        blogs_new = []
        blogs_ask_new = []
        for i in blogs:
            i = list(i)
            i[2] = urllib.parse.unquote(i[2])
            blogs_new.append(i)
        for i in blogs_ask:
            i = list(i)
            i[2] = urllib.parse.unquote(i[2])
            blogs_ask_new.append(i)
        blogNum = len(blogs)
        askNum = len(blogs_ask)

        ustcInfo = []
        niceBlog = []
        systemLinks = getAdmin('system')
        for i in systemLinks:
            blogid = i[0].split('/')[-1]
            title = showOneBlogTitle(blogid)
            ustcInfo.append([title, blogid])
        niceLinks = getAdmin('nice')
        for i in niceLinks:
            blogid = i[0].split('/')[-1]
            title = showOneBlogTitle(blogid)
            niceBlog.append([title, blogid])
        friendLinks = showLink()
        self.render(
            'index.html', cookieName=username, blogs=blogs_new, blogs_ask=blogs_ask_new, blogNum=blogNum,
                    askNum=askNum, blogPage=blogPage, askPage=askPage, order=order, ustcInfo=ustcInfo, niceBlog=niceBlog, friendLinks=friendLinks)


class folHandler(tornado.web.RequestHandler):  # 用户关注的人

    def get(self, name):
        userid = self.get_cookie('hackerID')
        username = fetchName(userid)
        follows = showFollows(name)
        followsN = len(follows)
        headpics = []
        for i in follows:
            headpics.append(getHeadPic(i))
        self.render('fol.html', cookieName=username, who=name,
                    follows=follows, followsN=followsN, headpics=headpics)


class fanHandler(tornado.web.RequestHandler):  # 用户的粉丝

    def get(self, name):
        userid = self.get_cookie('hackerID')
        username = fetchName(userid)
        fans = showFans(name)
        fansN = len(fans)
        headpics = []
        for i in fans:
            headpics.append(getHeadPic(i))
        self.render('fan.html', cookieName=username,
                    who=name, fans=fans, fansN=fansN, headpics=headpics)


class upHandler(tornado.web.RequestHandler):

    def post(self):
        selfid = self.get_cookie('hackerID')
        if selfid:
            selfname = fetchName(selfid)
            refer = self.request.headers.get('Referer')
            path = urllib.parse.urlparse(refer).path
            pathList = path.split('/')
            blogid = pathList[-1]
            addUp(blogid, selfname)
            author = showBlogAuthor(blogid)
            updateScore(author, 2)
            self.redirect(path)
        else:
            self.redirect('/register')


class messageHandler(tornado.web.RequestHandler):

    def get(self, page):
        selfid = self.get_cookie('hackerID')
        selfname = fetchName(selfid)
        if selfname:
            commentMsg, upMsg = showMessage(selfname)
            setFlagYes(selfname)
            commentLen = len(commentMsg)
            upLen = len(upMsg)
            commentPage, upPage = page.split('_')
            self.render(
                'message.html', cookieName=selfname, commentMsg=commentMsg, upMsg=upMsg,
                        commentLen=commentLen, upLen=upLen, commentPage=commentPage, upPage=upPage)
        else:
            self.redirect('/')


class aboutHandler(tornado.web.RequestHandler):

    def get(self):
        selfid = self.get_cookie('hackerID')
        selfname = fetchName(selfid)
        self.render('about.html', cookieName=selfname)


class sendMailHandler(tornado.web.RequestHandler):

    def get(self):
        mail = self.get_argument('mail')
        name = getMailName(mail)
        code = getVerifyCode(mail)
        res = whetherVerified_name(name)
        if res:
            userid = fetchID(name)
            self.set_cookie('hackerID', userid)
            self.redirect('/')
        else:
            mailTo(name, mail, code)
            self.render('sendMail.html', cookieName=None, mail=mail)


class verifyHandler(tornado.web.RequestHandler):

    def get(self):
        mail = self.get_argument('mail')
        code = self.get_argument('code')
        res = verifyMail(mail, code)
        if res:
            name = getMailName(mail)
            userid = fetchID(name)
            self.set_cookie('hackerID', userid)
            self.redirect('/setting/info')
        else:
            self.render('invalidMail.html', cookieName=None, mail=mail)


class editBlogHandler(tornado.web.RequestHandler):

    def get(self, idvalue):
        selfid = self.get_cookie('hackerID')
        selfname = fetchName(selfid)
        author = showBlogAuthor(idvalue)
        if selfname != author:
            self.redirect('/')
        else:
            data = showOneBlog(idvalue)
            title = urllib.parse.unquote(data[2])
            content_md = urllib.parse.unquote(data[3])
            tag = data[5]
            category = data[6]
            self.render('editBlog.html', cookieName=selfname, title=title,
                        content=content_md, tag=tag, category=category, idvalue=idvalue)

    def post(self, blogid):
        selfid = self.get_cookie('hackerID')
        selfname = fetchName(selfid)
        author = showBlogAuthor(blogid)
        if selfname != author:
            self.redirect('/')
        else:
            title = self.get_argument('title')
            title = urllib.parse.quote(title)
            blog_md = self.get_argument('blog')
            blog = urllib.parse.quote(blog_md)  # 要把"等符号都编码一下，再录入数据库
            tag = self.get_argument('tag')
            category = self.get_argument('category')
            updateBlog(blogid, title, blog, tag, category)
            self.redirect('/blog/' + blogid)


class blingHandler(tornado.web.RequestHandler):

    def get(self):
        selfid = self.get_cookie('hackerID')
        if selfid:
            selfname = fetchName(selfid)
            try:
                res = readNews(selfname)
            except Exception as e:
                print('Exception:', e)
                res = True
            finally:
                if res:
                    self.write('1')
                else:
                    self.write('0')
        # res True 用户读过  False 用户没读过


class uploadPicHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('uploadPic.html', picLink=None)

    def post(self):
        headpicList = self.request.files.get('pic')
        if headpicList:
            now = str(int(time.time() * 100))
            picType = headpicList[0]['content_type']
            picType = picType.split('/')
            if picType[0] == 'image':
                data = headpicList[0]['body']
                m = hashlib.md5(data)
                value = m.hexdigest()
                pic = 'static/pic/' + value + '.' + picType[-1]
                f = open(pic, 'wb')
                f.write(data)
                f.close()
            else:
                pass
        self.render('uploadPic.html', picLink=pic)


class markdownHandler(tornado.web.RequestHandler):

    def get(self):
        selfid = self.get_cookie('hackerID')
        selfname = fetchName(selfid)
        self.render('markdown.html', cookieName=selfname)


class delBlogHandler(tornado.web.RequestHandler):

    def get(self, idvalue):
        selfid = self.get_cookie('hackerID')
        selfname = fetchName(selfid)
        referer = self.request.headers.get('referer')
        if referer == 'http://www.ustchacker.com/blog/' + idvalue:
            delBlog(idvalue)
        self.redirect('/user/' + selfname)


class adminHandler(tornado.web.RequestHandler):

    def get(self):
        selfid = self.get_cookie('hackerID')
        selfname = fetchName(selfid)
        if selfname == rootAdminName.rootAdminName:  # the root admin
            self.render('admin.html', cookieName=selfname)
        else:
            self.redirect('/error')

    def post(self):
        selfid = self.get_cookie('hackerID')
        selfname = fetchName(selfid)
        if selfname == rootAdminName.rootAdminName:  # the root admin
            # systemLink--USTC Hacker资讯  niceLink--推荐文章
            systemLink = self.get_argument('system')
            niceLink = self.get_argument('nice')
            friendLinkUrl = self.get_argument('linkUrl')
            friendLinkTitle = self.get_argument('linkTitle')
            if systemLink:
                data=getAdmin('system')
                if len(data)>=3:
                    toDel=data.pop() #最旧的一个
                    delAdmin(toDel[0])
                insertAdmin(systemLink,'system')
            if niceLink:
                data=getAdmin('nice')
                if len(data)>=3:
                    toDel=data.pop() #最旧的一个
                    delAdmin(toDel[0])
                insertAdmin(niceLink,'nice')
            if friendLinkUrl and friendLinkTitle:
                addLink(friendLinkUrl, friendLinkTitle)
            self.redirect('/299792458')
        else:
            self.redirect('/error')

class errorHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('error.html')
