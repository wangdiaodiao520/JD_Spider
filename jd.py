from lxml import etree
import requests
import json
import re
import threading
from queue import Queue


#创建jd爬虫类，并初始化code为唯一输入
class JD():
    def __init__(self,code):
        self.code = code
        self.head = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"}

    #请求主页，获取必须参数cat和商品name
    def get_page(self):
        url = "https://item.jd.com/"+self.code+".html"
        try:
            rep = requests.get(url,headers=self.head)
            if rep.status_code == 200:
                cat = ''.join(re.findall('cat:.*?(\d+,\d+,\d+).*?,',rep.text,re.S))#接口必须参数
                rep = etree.HTML(rep.text)
                name = ''.join(rep.xpath('//div[@class="sku-name"]/text()')).replace(',','').replace('\n','').strip()#商品name
                address = ["1_2801_2827_0","2_78_51978_0","19_1601_3633_0","22_1930_50944_52191","17_1381_3079_50763","8_560_50825_50829","27_2376_50235_56679","13_1060_3542_51370"]#地址列表
                price,price_plus,plus_limit = self.get_price(cat,address[0])#调用价格接口，获取价格、plus价格和plus限制
                cx = self.get_cx(cat,address[0])#调用促销接口，获取促销信息
                #检查地址列表中各地址是否有货
                '''
                p = []
                for i in address:
                    is_g = self.is_g(cat,i)
                    p.append(is_g)
                '''
                q = Queue()#容器
                #8地区检测是否有货线程
                for i in range(8):
                    t = threading.Thread(target=self.is_g,args=(cat,address[i],q))
                    t.start()
                    t.join()
                #去除检测结果
                p = []
                for _ in range(8):
                    p.append(q.get())
                #采集结果格式化
                result = self.code + ','+ name +','+ price +','+ price_plus +','+','.join(p) +','+ plus_limit+cx.replace("&nbsp;<a href='javascript:login();'>请登录</a>&nbsp;","")
                if type(result.split(',')).__name__ == "list":
                    return result.split(',')
                else:
                    pass
            elif rep.status_code == 403:
                pass
            else:
                self.get_page()
        except:
            self.get_page()

            
            
    #检测是否有货
    def is_g(self,cat,i,q):
        url = "https://c0.3.cn/stock?skuId="+self.code+"&cat="+cat+"&area="+i
        rep = requests.get(url,headers=self.head)
        if rep.status_code == 200:
            if "有货" in rep.text:
                rep = json.loads(rep.text)
                is_g = rep["stock"]["stockDesc"].replace('<strong>','').replace('</strong>','').replace('</span>','').replace('<span>','').replace('，','|')
            else:
                is_g = "无货"
            q.put(is_g)
            #return is_g
        elif rep.status_code == 403:
            #return '403'
            q.put('403')
        else:
            self.is_g(cat,i,q)
            

    #价格接口
    def get_price(self,cat,i):
        url = "https://c0.3.cn/stock?skuId="+self.code+"&cat="+cat+"&area="+i
        rep = requests.get(url,headers=self.head)
        if rep.status_code == 200:
            try:
                rep = json.loads(rep.text)
                price = rep["stock"]["jdPrice"]["p"]
            except:
                self.get_price(cat,i)
            try:
                price_plus = rep["stock"]["jdPrice"]["tpp"]
            except:
                price_plus = 'None'
            try:
                plus_limit = rep["stock"]["jdPrice"]["ext"]
            except:
                plus_limit = 'None'
            plus_limit = ''.join(re.findall('confine_text":"(.*?)",',plus_limit,re.S))
            return price,price_plus,plus_limit
        elif rep.status_code == 403:
                return '403','403','403',
        else:
            self.get_price(cat,i)


    #促销接口
    def get_cx(self,cat,i):
        cat = cat.replace(',','%2C')
        url = "https://cd.jd.com/promotion/v2?&skuId="+self.code+"&area="+i+"&cat="+cat
        rep = requests.get(url,headers=self.head)
        if rep.status_code == 200:
            cx = ''.join(re.findall('content":"(.*?)",',rep.text,re.S)).replace('，','|')
            if 'quan' in rep.text:
                rep = json.loads(rep.text)
                try:
                    q = rep['quan']['title'].replace('，','|')
                    cx = cx +'|' + q
                except:
                    cx = cx
            return cx
        elif rep.status_code == 403:
            return '403'
        else:
            self.get_cx(cat,i)

jd =JD('6037314')
jd.get_page()
