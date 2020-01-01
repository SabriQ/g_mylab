# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 00:03:48 2019

@author: Sabri
"""

import requests
import json
class DingTalk_Base:
    def __init__(self):
        self.__headers = {'Content-Type': 'application/json;charset=utf-8'}
        self.url = ''
    def send_msg(self,text):
        json_text = {
            "msgtype": "text",
            "text": {
                "content": text
            },
            "at": {
                "atMobiles": [
                    "17621583611"
                ],
                "isAtAll": False
            }
        }
        return requests.post(self.url, json.dumps(json_text), headers=self.__headers).content
class DingTalk_Disaster(DingTalk_Base):
    def __init__(self):
        super().__init__()
        # 填写机器人的url
        self.url = 'https://oapi.dingtalk.com/robot/send?access_token=3e2726fdeb64d1b27dc0be37498fb6ad4484b01dcb4d30055742752be404b08e'
if __name__ == '__main__':
    ding = DingTalk_Disaster()
    ding.send_msg('ninghao')