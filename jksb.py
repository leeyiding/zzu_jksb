# -*- coding: utf-8 -*-
# @Time    : 2021/2/15 06:00
# @Author  : leeyiding
# @Email   : admin@lyd.im

import requests
import re
import logging
import json
from bs4 import BeautifulSoup

class ZZUjksb(object):
    # 初始化
    def __init__(self,user):
        self.username = user['username']
        self.password = user['password']
        self.data1 = user['data1']
        self.data2 = user['data2']
        self.notify = user['notify']
        self.baseUrl = "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll"

    # 登陆
    def login(self):
        loginUrl = self.baseUrl + "/login"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": 'gzip, deflate, br',
            "Accept-Language": "zh",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Length": "139",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "jksb.v.zzu.edu.cn",
            "Origin": "https://jksb.v.zzu.edu.cn",
            "Referer": "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/first0",
            "Sec-Fetch-Dest": "iframe",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
        data = {
            "uid": self.username,
            "upw": self.password,
            "smbtn": "进入健康状况上报平台",
            "hh28": "540"
        }
        try:
            r = requests.post(url=loginUrl,data=data,headers=headers,timeout=300)
        except Exception as e:
            self.logger.error("登陆失败，请检查网络后重试")
            self.logger.error(e)
            return False
        else:
            r.encoding = "utf-8"
            bs = BeautifulSoup(r.text,"html.parser")
            errmsg = bs.find('div',style="width:296px;height:100%;font-size:14px;color:#333;line-height:26px;float:left;")
            if errmsg:
                self.logger.error(errmsg.text)
                return False
            else:
                self.logger.info("登陆成功")
                self.ptopid = re.findall(r"[a-zA-Z0-9]{33}",r.text)[0]
                self.sid = re.findall(r"[0-9]{18}",r.text)[0]
                self.data1["ptopid"] = self.ptopid
                self.data1['sid'] = self.sid
                self.data2["ptopid"] = self.ptopid
                self.data2['sid'] = self.sid
                return True

    # 检查打卡状态
    def checkStatus(self):
        checkUrl = self.baseUrl + "/jksb"
        paramas = {
            "ptopid": self.ptopid,
            "sid": self.sid
        }
        try:
            r = requests.get(url=checkUrl,params=paramas)
        except:
            self.logger.error("检查打卡状态失败")
        else:
            r.encoding = "utf-8"
            result = re.findall(r"\u4eca\u65e5\u60a8\u5df2\u7ecf\u586b\u62a5\u8fc7\u4e86",r.text)
            if result:
                self.logger.info(result[0])
                return True
            else:
                self.logger.info("检测到今日未打卡，开始打卡")
                return False
     
    # 发送消息通知
    def sendMsg(self,notify,msg):
        if notify['sckey']:
            serverUrl = "https://sc.ftqq.com/{}.send".format(notify['sckey'])
            data = {
                "text": "健康上报打卡完成",
                "desp": msg
            }
            r = requests.post(url=serverUrl,data=data)
            r.encoding = "utf-8"
            r = json.loads(r.text)
            if r['errno'] == 0 :
                self.logger.info("Server酱通发送知信息成功！")
            else:
                self.logger.error("Server酱通发送知信息失败！")
        if notify['ddtoken']:
            webhook = "https://oapi.dingtalk.com/robot/send?access_token={}".format(notify['ddtoken'])
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "健康上报打卡完成",
                    "text": msg
                }
            }
            r = requests.post(url=webhook,json=data)
            r.encoding = "utf-8"
            r = json.loads(r.text)
            if r['errcode'] == 0:
                self.logger.info("钉钉通发送知信息成功！")
            elif r['errcode'] == 310000:
                self.logger.error("钉钉通发送知信息失败!请为钉钉机器人添加关键词'健康上报'")
            else:
                self.logger.error("钉钉通发送知信息失败!")

    # 签到
    def checkin(self):
        checkinUrl = self.baseUrl + "/jksb"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": 'gzip, deflate, br',
            "Accept-Language": "zh",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Length": "482",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "jksb.v.zzu.edu.cn",
            "Origin": "https://jksb.v.zzu.edu.cn",
            "Referer": "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb",
            "Sec-Fetch-Dest": "iframe",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
        session = requests.session()
        session.post(url=checkinUrl,data=self.data1,headers=headers)
        r = session.post(url=checkinUrl,data=self.data2,headers=headers)
        r.encoding = "utf-8"
        bs = BeautifulSoup(r.text,"html.parser")
        msg = bs.find('div',style="width:296px;height:100%;font-size:14px;color:#333;line-height:26px;float:left;")
        self.logger.info(msg.text)
        self.sendMsg(self.notify,msg.text)
        
    def main(self):
        # 日志输出控制台
        logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        # 日志输入文件
        fh = logging.FileHandler('./log.txt', mode='a', encoding='utf-8')
        fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(fh)

        for i in range(1,5):
            if i < 4:
                self.logger.info("正在第{}次模拟登陆健康上报系统".format(i))
                if self.login():
                    if self.checkStatus():
                        self.logger.info("无需重复打卡，程序执行完成！")
                        break
                    else:
                        self.checkin()
            else:
                self.logger.error("已连续尝试模拟登陆三次失败，请检查网络后重试！")

def readJson():
    #读取用户配置信息
    with open('./config.json',encoding='UTF-8') as fp:
        users = json.load(fp)
        return users

if __name__ == '__main__':
    users = readJson()
    for count in range(len(users)):
        user = ZZUjksb(users[count])
        user.main()
        