#!/usr/bin/env python3
import os
import tornado.web
import tornado.ioloop
from handlers import *

requestHandlers = [
    (r'/', mainHandler),
    (r'/index/(\w+)', indexHandler),
    (r'/member/(\d+)', memberHandler),
    (r'/chatting/(\d+)', chattingHandler),
    (r'/chat/(\d+)', chatHandler),
    (r'/register', registerHandler),
    (r'/logout', logoutHandler),
    (r'/post', postHandler),
    (r'/user/(\w+)', userHandler),
    (r'/blog/(\d+)', blogHandler),
    (r'/comment', commentHandler),
    (r'/setting/(\w+)', settingHandler),
    (r'/follow/(\w+)', followHandler),
    (r'/tag/(\w+)/(\w+)', tagHandler),
    (r'/fol/(\w+)', folHandler),
    (r'/fan/(\w+)', fanHandler),
    (r'/up', upHandler),
    (r'/message/(\w+)', messageHandler),
    (r'/about', aboutHandler),
    (r'/verify', verifyHandler),
    (r'/sendMail', sendMailHandler),
    (r'/editBlog/(\w+)', editBlogHandler),
    (r'/bling', blingHandler),
    (r'/uploadPic', uploadPicHandler),
    (r'/markdown', markdownHandler),
    (r'/delBlog/(\d+)', delBlogHandler),
    (r'/299792458', adminHandler),
    (r'/error', errorHandler),
    (r'.*', errorHandler),
]
settings = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'template'),
}

app = tornado.web.Application(requestHandlers, **settings)
app.listen(9011)
print('start listening on port 9011')
tornado.ioloop.IOLoop.instance().start()
