
# encoding: utf-8
# 文件名：smtp_test.py
# 基于python 3.4 发送邮件测试示例，本代码文件使用UTF-8格式
# TODO：隐藏账户信息

import os
import base64

import smtplib
import email.utils
from email.mime.text import MIMEText

# 接收邮件地址
def send_email(to_list, sub, content):
    to_email = 'sqiu@ion.ac.cn'
    smtpserver = 'smtp.qq.com'
    snd_email = '196989054@qq.com'
    username = snd_email
    password = 'rpcugidmjypmcbch'
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = sub
    msg['From'] = snd_email
    msg['To'] = to_list
    #msg['Date'] = formatdate(localtime=True)
    try:
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver)
        smtp.login(username, password)
        #smtp.login(username, password)
        smtp.sendmail(snd_email, to_list, msg.as_string())
        smtp.quit()
        return 0
    except Exception as e:
        print(str(e))
        return -1

# main...
if __name__ == '__main__':  
    if send_email(to_email, "hello", "hello world, this is a python email test") == 0:  
        print("send %s ok" % to_email)
    else:  
        print("send failed")
