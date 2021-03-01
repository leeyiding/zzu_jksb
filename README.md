# zzu_jksb
## 使用方法

1. 安装python3

2. 克隆仓库

   ```
   git clone https://github.com/leeyiding/zzu_jksb.git && cd zzu_jksb
   ```

3. 安装依赖

   ```
   pip3 install -r requestments.txt
   ```

4. 复制模板`config.json.sample`并修改参数

   ```
   # Windows
   copy ./config.json.sample ./config.json
   # Linux
   cp ./config.json.sample ./config.json
   ```

   参数详情

   | 参数     | 含义                                                         | 备注 |
   | -------- | ------------------------------------------------------------ | ---- |
   | username | 学号                                                         | 必填 |
   | password | 健康上报平台密码                                             | 必填 |
   | myvs_1   | 您今天是否有发热症状?（是\|否）                              | 默认 |
   | myvs_2   | 您今天是否有咳嗽症状?（是\|否）                              | 默认 |
   | myvs_3   | 您今天是否有乏力或轻微乏力症状?（是\|否）                    | 默认 |
   | myvs_4   | 您今天是否有鼻塞、流涕、咽痛或腹泻等症状?（是\|否）          | 默认 |
   | myvs_5   | 您今天是否被所在地医疗机构确定为确诊病例?（是\|否）          | 默认 |
   | myvs_6   | 您今天是否被所在地医疗机构确定为疑似病例?（是\|否）          | 默认 |
   | myvs_7   | 您今天是否被所在地政府或医疗卫生部门确定为密切接触者?（是\|否） | 默认 |
   | myvs_8   | 您今天是否被所在地医疗机构进行院内隔离观察治疗?（是\|否）    | 默认 |
   | myvs_9   | 您今天是否被要求在政府集中隔离点进行隔离观察?（是\|否）      | 默认 |
   | myvs_10  | 您今日是否被所在地政府有关部门或医院要求居家隔离观察?（是\|否） | 默认 |
   | myvs_11  | 所在小区（村）是否有确诊病例?(以当地政府公开信息为准)（是\|否） | 默认 |
   | myvs_12  | 共同居住人是否有确诊病例?（是\|否）                          | 默认 |
   | myvs_13a | 当前实际所在地省属代码（河南省41)                            | 必填 |
   | myvs_13b | 当前实际所在地市属代码（郑州市4101)                          | 必填 |
   | myvs_13c | 当前具体所在地                                               | 必填 |
   | myvs_14  | 您是否为当日返郑人员?（是\|否）                              | 必填 |
   | myvs_14b | 若是，请填写：返回前居住地和抵郑时间                         | 选填 |
   | memo22   | 地理位置获取                                                 | 默认 |
   | jingdu   | 精度                                                         | 默认 |
   | weidu    | 纬度                                                         | 默认 |
   | sckey    | server酱key                                                  | 选填 |
   | ddtoken  | 钉钉机器人token                                              | 选填 |

5. 测试代码

   ```
   python3 jksb.py
   ```

6. 测试无误后添加crontab，为防止运行失败，建议每天运行两次

   ```
   20 0,6 * * * python3 /path/to/zzu_jksb/jksb.py
   ```

## 已知问题

1. Linux客户端频繁出现SSL错误

   解决方法：

   ```
   pip3 install cryptography
   pip3 install pyOpenSSL
   pip3 install certifi
   ```

2. 频繁运行脚本会导致登陆页出现验证码

   解决方法：

   目前脚本暂无自动填充验证码功能，登陆路由器后台重新拨号或等待十分钟以上即可解除验证码限制。

## 注意事项

1. 网站会检测运行脚本设备IP，并识别IP归属地，所以不建议使用云服务器、云函数、GitHub Action等运行该程序，建议使用家中路由器、NAS、树莓派等设备运行脚本

2. 多用户在`[]`中添加更多信息即可，注意严格遵守json语法

   在线校验json格式：[https://www.bejson.com/](https://www.bejson.com/)

3. server酱申请地址：[http://sc.ftqq.com/](http://sc.ftqq.com/)

4. 钉钉通知机器人自定义机器人文档：[https://developers.dingtalk.com/document/app/custom-robot-access](https://developers.dingtalk.com/document/app/custom-robot-access)，机器人关键词填写`健康上报`

## 更新日志

1. 2021.3.1

   首次提交代码，具有重复打卡检测，消息通知等功能

## TODO

- [ ] 添加验证码识别功能（难）
- [ ] 支持选择更多消息推送渠道
- [ ] 优化代码逻辑
- [ ] .............

