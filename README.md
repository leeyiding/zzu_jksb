# zzu_jksb
## 使用方法

1. 安装python3和git

2. 克隆仓库

   ```
   git clone https://github.com/leeyiding/zzu_jksb.git && cd zzu_jksb
   ```

3. 安装依赖

   ```
   pip3 install pip -U
   pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
   pip3 install -r requestments.txt
   ```

4. 复制模板`config.sample.json`并修改参数

   ```
   # Linux
   cp ./config.sample.json ./config.json
   ```
   
   参数详情

   ```json
   {
       "CleanLogDay": 7,						//自动清理几天前日志
       "Email": {								//配置SMTP邮箱
           "host": "",							//SMTP服务器
           "port": 465,						//SMTP服务器端口号(SSL)
           "user": "",							//SMTP账号
           "password": "",						//SMTP密码
           "sender": ""						//发件人邮箱 
       },
       "Users": [								//配置用户个人信息
           {									//用户1
               "uid": "",						//学号
               "upw": "",						//健康上报平台密码
               "data1": {						//默认
                   "day6": "b",
                   "did": "1",
                   "door": "",
                   "men6": "a"
               },
               "data2": {				
                   "myvs_1": "否",				//您今天是否有发热症状?(是|否)
                   "myvs_2": "否",				//您今天是否有咳嗽症状?(是|否)
                   "myvs_3": "否",				//您今天是否有乏力或轻微乏力症状?(是|否)
                   "myvs_4": "否",				//您今天是否有鼻塞、流涕、咽痛或腹泻等症状?(是|否)
                   "myvs_5": "否",				//您今天是否被所在地医疗机构确定为确诊病例?(是|否)
                   "myvs_6": "否",				//您今天是否被所在地医疗机构确定为疑似病例?(是|否)
                   "myvs_7": "否",				//您今天是否被所在地政府或医疗卫生部门确定为密切接触者?(是|否)
                   "myvs_8": "否",				//您今天是否被所在地医疗机构进行院内隔离观察治疗?(是|否)
                   "myvs_9": "否",				//您今天是否被要求在政府集中隔离点进行隔离观察?(是|否)
                   "myvs_10": "否",				//您今日是否被所在地政府有关部门或医院要求居家隔离观察?(是|否)
                   "myvs_11": "否",				//所在小区（村）是否有确诊病例?(以当地政府公开信息为准)(是|否)
                   "myvs_12": "否",				//共同居住人是否有确诊病例?(是|否)
                   "myvs_13a": "41",			//当前实际所在地省属代码，运行getCode.py查询
                   "myvs_13b": "4101",			//当前实际所在地市属代码，运行getCode.py查询
                   "myvs_13c": "",				//当前具体所在地
                   "myvs_14": "否",				//您是否为当日返郑人员?(是|否)
                   "myvs_14b": "",				//若是，请填写：返回前居住地和抵郑时间
                   "memo22": "不支持地理定位",	//地理位置获取(不支持地理定位|成功获取|用户拒绝|无法获取|请求超时|未知错误)
                   "did": "2",
                   "door": "",
                   "day6": "b",
                   "men6": "a",
                   "sheng6": "",
                   "shi6": "",
                   "fun3": "",
                   "jingdu": "0.000000",		//经度
                   "weidu": "0.000000"			//纬度
               },
               "notify": {
                   "email": "",				//收件人邮箱
                   "sckey": "",				//Server酱Key
                   "sctkey": "",				//Server酱Turbo SendKey
                   "ddtoken": ""				//钉钉机器人Token
               }
           }
       ]
   }
   ```
   
5. 运行代码测试

   ```
   python3 ./jksb.py
   ```

6. 测试无误后添加crontab，为防止运行失败，建议每天运行两次

   ```
   20 0,6 * * * /usr/bin/env python3 /path/to/zzu_jksb/jksb.py
   ```

## 已知问题

频繁运行脚本会导致登陆页出现验证码

解决方法：目前脚本暂无自动填充验证码功能，登陆路由器后台重新拨号或等待十分钟以上即可解除验证码限制。

## 注意事项

1. 所在地省市执行`pyhon3 getCode.py`查询

2. 若想提交上报时的地理位置，请将配置文件中`memo22`值改为”成功获取“，`jingdu`和`weidu`值分别填入经纬度。拾取坐标系统：[http://api.map.baidu.com/lbsapi/getpoint/index.html](http://api.map.baidu.com/lbsapi/getpoint/index.html)

3. 网站会检测运行脚本设备IP，并识别IP归属地，管理员后台可以看到，所以不建议使用云服务器、云函数、GitHub Action等运行该程序，建议使用家中路由器、NAS、树莓派等设备运行脚本

4. 多用户在配置文件`users`中添加多人信息即可，注意严格遵守json语法

   在线校验json格式：[https://www.bejson.com/](https://www.bejson.com/)

## 消息通知

1. Server酱申请地址：[http://sc.ftqq.com/](http://sc.ftqq.com/)

   **Server酱旧版将于四月下线，请更换Server酱Turbo使用**

2. Server酱Turbo申请地址：[https://sct.ftqq.com/](https://sct.ftqq.com/)

3. 钉钉通知机器人自定义机器人文档：[https://developers.dingtalk.com/document/app/custom-robot-access](https://developers.dingtalk.com/document/app/custom-robot-access)，机器人关键词填写`健康上报`

## 更新日志

1. 2021.3.1

   首次提交代码，具有重复打卡检测，消息通知等功能
   
2. 2021.3.3

   优化代码逻辑，修复文件路径问题。
   
3. 2021.3.3

   添加Server酱Turbo推送渠道
   
4. 2021.3.5

   添加省市代码查询功能
   
   添加自动清理日志功能
   
5. 2021.3.6

   添加邮箱通知功能

## TODO

- [ ] 添加验证码识别功能（难）
- [ ] 支持选择更多消息推送渠道
- [ ] 优化代码逻辑
- [ ] .............
