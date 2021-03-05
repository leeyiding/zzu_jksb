# -*- coding: utf-8 -*-
# @Time    : 2021/2/15 06:00
# @Author  : leeyiding
# @Email   : admin@lyd.im

import os
import time
import sys
import requests
import re
import logging
import json
from bs4 import BeautifulSoup

class ZZUjksb(object):
    # 初始化
    def __init__(self,user,logger):
        self.username = user['username']
        self.password = user['password']
        self.data1 = user['data1']
        self.data2 = user['data2']
        self.notify = user['notify']
        self.baseUrl = "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll"
        self.logger = logger
    # 登陆
    def login(self):
        loginUrl = self.baseUrl + "/login"
        headers = {
            "Host": "jksb.v.zzu.edu.cn",
            "Origin": "https://jksb.v.zzu.edu.cn",
            "Referer": "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/first0",
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
            self.logger.error(e)
            self.logger.error("登陆失败，请检查网络后重试")
            return False
        else:
            r.encoding = "utf-8"
            bs = BeautifulSoup(r.text,"html.parser")
            errmsg = bs.find('div',style="width:296px;height:100%;font-size:14px;color:#333;line-height:26px;float:left;")
            if errmsg:
                self.logger.error(errmsg.text.strip())
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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
        try:
            r = requests.get(url=checkUrl,params=paramas,headers=headers,timeout=300)
        except Exception as e:
            self.logger.error(e)
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
    def sendMsg(self,title,msg):
        if self.notify['sckey']:
            notifyUrl = "https://sc.ftqq.com/{}.send".format(self.notify['sckey'])
            data = {
                "text": title,
                "desp": msg
            }
            try:
                r = requests.post(url=notifyUrl,data=data,timeout=60)
            except Exception as e:
                self.logger.error(e)
                self.logger.error("Server发送酱通知信息失败！请检查网络后重试！")
            else:
                r.encoding = "utf-8"
                r = json.loads(r.text)
                if r['errno'] == 0 :
                    self.logger.info("Server酱发送通知信息成功！")
                else:
                    if r['errmsg'] == "bad pushtoken":
                        self.logger.error("Server酱发送通知信息失败！请检查sckey后重试！")
                    elif r['errmsg'] == "不要重复发送同样的内容":
                        self.logger.error("Server酱发送通知信息失败！短时间内不要重复发送同样的内容！")
                    else:
                        self.logger.error("Server酱发送通知信息失败！原因未知")
        if self.notify['sctkey']:
            notifyUrl = "https://sctapi.ftqq.com/{}.send".format(self.notify['sctkey'])
            data = {
                "text": title,
                "desp": msg
            }
            try:
                r = requests.post(url=notifyUrl,data=data,timeout=60)
            except Exception as e:
                self.logger.error(e)
                self.logger.error("Server酱Turbo发送通知信息失败！请检查网络后重试！")
            else:
                r.encoding = "utf-8"
                r = json.loads(r.text)
                if r["code"] == 0 :
                    self.logger.info("Server酱Turbo发送通知信息成功！")
                else:
                    if r["message"] == "[AUTH]用户不存在或者权限不足":
                        self.logger.error("Server酱Turbo发送通知信息失败！请检查sctkey后重试！")
                    elif r["message"] == "[AUTH]超过分钟的发送次数限制[5]，请稍后再试":
                        self.logger.error("Server酱Turbo发送通知信息失败！短时间内不要重复发送同样的内容！")
                    else:
                        self.logger.error("Server酱Turbo发送通知信息失败！原因未知")
        if self.notify['ddtoken']:
            notifyUrl = "https://oapi.dingtalk.com/robot/send?access_token={}".format(self.notify['ddtoken'])
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": msg
                }
            }
            try:
                r = requests.post(url=notifyUrl,json=data,timeout=60)
            except Exception as e:
                self.logger.error(e)
                self.logger.error("钉钉发送通知信息失败！请检查网络后重试！")
            else:
                r.encoding = "utf-8"
                r = json.loads(r.text)
                if r['errcode'] == 0:
                    self.logger.info("钉钉发送通知信息成功！")
                elif r['errcode'] == 310000:
                    self.logger.error("钉钉发送通知信息失败!请为钉钉机器人添加关键词'健康上报'")
                else:
                    self.logger.error("钉钉发送通知信息失败!")

    # 签到
    def checkin(self):
        checkinUrl = self.baseUrl + "/jksb"
        headers = {
            "Origin": "https://jksb.v.zzu.edu.cn",
            "Referer": "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
        session = requests.session()
        try:
            session.post(url=checkinUrl,data=self.data1,headers=headers,timeout=300)
        except Exception as e:
            self.logger.error(e)
            self.logger.error("打卡失败，请检查网络后重试")
            return False
        else:
            try:
                r = session.post(url=checkinUrl,data=self.data2,headers=headers,timeout=300)
            except Exception as e:
                self.logger.error(e)
                self.logger.error("打卡失败，请检查网络后重试")
                return False
            else:
                r.encoding = "utf-8"
                bs = BeautifulSoup(r.text,"html.parser")
                errmsg = re.findall('提交失败',r.text)
                if errmsg:
                    msg = bs.find('div',style="width:296px;height:100%;font-size:12px;color:#333;line-height:20px;float:left;")
                    self.logger.error(msg.text)
                    self.sendMsg("健康上报打卡失败",msg.text)
                    return True
                else:
                    msg = bs.find('div',style="width:296px;height:100%;font-size:14px;color:#333;line-height:26px;float:left;")
                    if msg:
                        self.logger.info(msg.text.replace("　",""))
                        self.sendMsg("健康上报打卡完成",msg.text)
                        return True
                    else:
                        return False
        
    def main(self):
        # self.login()
        # self.checkin()
        for i in range(1,4):
            self.logger.info("正在第{}次模拟登陆健康上报系统".format(i))
            # 判断登录状态
            if self.login():
                # 判断打卡状态
                if self.checkStatus():
                    self.logger.info("无需重复打卡，程序执行完成！")
                    break
                else:
                    # 判断签到状态
                    if self.checkin():
                        break
            if i == 3:
                self.logger.error("已连续尝试模拟登陆三次失败，请检查网络或报错信息后重试！")

def readJson(configPath):
    if os.path.exists(configPath):
        #读取用户配置信息
        with open(configPath,encoding='UTF-8') as fp:
            users = json.load(fp)
            return users
    else:
        logger.error("未检测到配置文件config.json存在，请按照README.md说明创建配置文件")
        logger.info("*"*10 + "程序运行结束" + "*"*10)
        sys.exit(0)

if __name__ == '__main__':
    # 定义环境变量
    rootDir = os.path.dirname(os.path.abspath(__file__))
    configPath = rootDir + "/config.json"
    logDir = rootDir + "/logs"

    # 日志输出控制台
    logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    # 日志输入文件
    date = time.strftime("%Y-%m-%d", time.localtime()) 
    logPath = '{}/{}.log'.format(logDir,date)
    if not os.path.exists(logDir):
        logger.warning("未检测到日志目录存在，开始创建logs目录")
        os.mkdir(logDir)
    fh = logging.FileHandler(logPath, mode='a', encoding='utf-8')
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)

    # 运行主程序
    logger.info("*"*10 + "程序运行开始" + "*"*10)
    users = readJson(configPath)
    for count in range(len(users)):
        logger.info("开始为用户{}：{}执行健康上报".format(count+1,users[count]['username']))
        user = ZZUjksb(users[count],logger)
        user.main()
    logger.info("*"*10 + "程序运行结束" + "*"*10)
    with open(logPath,'a') as f:
        f.write("\n\n")
        