# -*- coding: utf-8 -*-
import requests

provinces = {'11': '北京市', '12': '天津市', '13': '河北省', '14': '山西省', '15': '内蒙古自治区', '21': '辽宁省', '22': '吉林省', '23': '黑龙江省', '31': '上海市', '32': '江苏省', '33': '浙江省', '34': '安徽省', '35': '福建省', '36': '江西省', '37': '山东省', '41': '河南省', '42': '湖北省', '43': '湖南省', '44': '广东省', '45': '广西壮族自治区', '46': '海南省', '50': '重庆市', '51': '四川省', '52': '贵州省', '53': '云南省', '54': '西藏自治区', '61': '陕西省', '62': '甘肃省', '63': '青海省', '64': '宁夏回族自治区', '65': '新疆维吾尔自治区', '71': '台湾省', '81': '香港特别行政区', '82': '澳门特别行政区', '99': '国外'}

text = ""
for province in provinces:
    text += province + provinces[province] + ";"
print(text)

provinceCode = input("请输入当前所在省两位数代码：")
while True:
    if provinceCode in provinces.keys():
        url = "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/getstr56?ty5=sheng2&by2=y&ids=" + provinceCode
        try:
            r =requests.get(url)
        except:
            print("请联网查询")
            break
        else:
            r.encoding = "utf-8"
            print(r.text)
            break
    else:
        provinceCode = input("输入错误，请重新输入:")
