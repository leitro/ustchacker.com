import smtplib
import email.mime.multipart
import email.mime.text
from mailPassword import *  # 这里存放的是我的邮箱密码

def mailTo(name, mail, verifyCode):
    sourceMail = 'ustchacker@aliyun.com'
    msg = email.mime.multipart.MIMEMultipart()
    msg['from'] = sourceMail
    msg['to'] = mail
    msg['subject'] = 'USTC Hacker确认邮箱'
    content = '亲爱的' + name + '：' + '''

		欢迎加入USTC Hacker！

		请点击下面的链接完成注册：

		'''
    link = 'http://www.ustchacker.com/verify?mail=' + \
        mail + '&code=' + verifyCode
    content += link
    content += '''

	如果以上链接无法点击，请将上面的地址复制到你的浏览器(如chrome)的地址栏进入USTC Hacker。

	----USTC Hacker----

	(这是一封自动产生的email，请勿回复。)

	'''

    txt = email.mime.text.MIMEText(content)
    msg.attach(txt)

    smtp = smtplib.SMTP()
    smtp.connect('smtp.mail.aliyun.com', '25')
    smtp.login(sourceMail, MAILPASSWORD)
    smtp.sendmail(sourceMail, mail, str(msg))
    smtp.quit()
