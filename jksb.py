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
import smtplib
from email.mime.text import MIMEText
from email.header import Header

class ZZUjksb(object):
    # 初始化
    def __init__(self,user,email,logger):
        self.uid = user['uid']
        self.upw = user['upw']
        self.data1 = user['data1']
        self.data2 = user['data2']
        self.notify = user['notify']
        self.baseUrl = "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll"
        self.email = email
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
            "uid": self.uid,
            "upw": self.upw,
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
    # 获取姓名
    def getUsername(self):
        infoUrl = "{}/viewdata?ptopid={}&fun2=h&mt2=&ws2=&us2=b&dw5=&nj5=&ids={}&sid={}".format(self.baseUrl,self.ptopid,self.uid,self.sid)
        headers = {
            "Host": "jksb.v.zzu.edu.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
        try:
            r = requests.get(url=infoUrl,headers=headers,timeout=300)
        except Exception as e:
            self.logger.error(e)
            self.logger.error("获取用户名失败，请检查网络后重试")
            self.username = self.uid
        else:
            r.encoding = "utf-8"
            bs = BeautifulSoup(r.text,"html.parser")
            self.username = bs.find_all("span",style="color:#00c")[1].text
            
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
            checkinResult = re.findall(r"今日您已经填报过了",r.text)
            if checkinResult:
                self.healthCodeMsg = ""
                self.logger.info(checkinResult[0])
                return True
            else:
                healthCodeResult = re.findall("还没有上传",r.text)
                if healthCodeResult:
                    self.healthCodeMsg = "请注意：你还没有上传国家政务平台健康码截图。"
                    self.logger.warning(self.healthCodeMsg)
                else:
                    self.healthCodeMsg = "恭喜你，本周已上传过国家政务平台健康码截图。"
                    self.logger.info(self.healthCodeMsg)
                self.logger.info("检测到今日未打卡，开始打卡")
                return False
     
    # 发送消息通知
    def sendMsg(self,title,msg):
        msg += "\n" + self.healthCodeMsg
        if self.email["host"] and self.email["port"] and self.email["user"] and self.email["password"] and self.email["sender"] and self.notify['email']:
            content = msg
            message = MIMEText(content, 'plain', 'utf-8')
            message['From'] = Header("admin", 'utf-8')  
            message['To'] =  Header(self.username, 'utf-8')
            subject = title
            message['Subject'] = Header(subject, 'utf-8') 
            try:
                smtpObj = smtplib.SMTP_SSL(self.email["host"], self.email["port"]) 
                smtpObj.login(self.email["user"],self.email["password"])  
                smtpObj.sendmail(self.email["sender"], self.notify['email'], message.as_string())
                smtpObj.quit()
                self.logger.info('邮件发送成功')
            except smtplib.SMTPException as e:
                self.logger.error('邮件发送失败')
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
                        self.sendMsg("健康上报打卡完成",msg.text.replace("　",""))
                        return True
                    else:
                        return False
        
    def main(self):
        # self.login()
        # self.getUsername()
        # self.checkStatus()
        # self.checkin()
        for i in range(1,4):
            self.logger.info("正在第{}次模拟登陆健康上报系统".format(i))
            # 判断登录状态
            if self.login():
                self.getUsername()
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
            config = json.load(fp)
            return config
    else:
        logger.error("未检测到配置文件config.json存在，请按照README.md说明创建配置文件")
        logger.info("*"*10 + "程序运行结束" + "*"*10)
        sys.exit(0)

def cleanLog(logDir,day):
    logger.info("开始清理日志")
    cleanNum = 0
    files = os.listdir(logDir)
    for file in files:
        today = time.mktime(time.strptime(time.strftime("%Y-%m-%d", time.localtime()),"%Y-%m-%d"))
        logDate = time.mktime(time.strptime(file.split(".")[0],"%Y-%m-%d"))
        dayNum = int((int(today) - int(logDate)) / (24 * 60 * 60))
        if dayNum > day:
            os.remove("{}/{}".format(logDir,file))
            cleanNum += 1
            logger.info("已删除{}天前日志{}".format(dayNum,file))
    if cleanNum == 0:
        logger.info("未检测到过期日志，无需清理！")

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
    config = readJson(configPath)
    users = config['Users']
    for count in range(len(users)):
        logger.info("开始为用户{}：{}执行健康上报".format(count+1,users[count]['uid']))
        user = ZZUjksb(users[count],config['Email'],logger)
        user.main()
    cleanLog(logDir,config['CleanLogDay'])
    logger.info("*"*10 + "程序运行结束" + "*"*10)
    with open(logPath,'a') as f:
        f.write("\n\n")
        