import tkinter as tk
from tkinter.filedialog import askopenfilename
import csv
import xlrd
from jd import *
import threading
from queue import Queue
import time



#gui类
class APP():
    def __init__(self,window):
        self.init_window = window

    def set_init_window(self):
        self.init_window.title('JD_spider by 王钢蛋')#基本设置
        self.init_window.geometry('500x120')

        self.line = tk.Label(self.init_window,text='进度',).place(x=50,y=20)#进度条设置
        self.canvas = tk.Canvas(self.init_window,width=350,height=18,bg='white')
        self.canvas.place(x=80,y=20)

        self.text = tk.Text(self.init_window,width=44,height=1)#输出框
        self.text.place(x=120,y=56)

        self.button = tk.Button(self.init_window,text='选择文件',command=self.select)#选择文件按钮
        self.button.place(x=50,y=50)

        self.start = tk.Button(self.init_window,text='开始',command=lambda:self.thread_it(self.jd))#开始按钮
        self.start.place(x=240,y=90)

    #选择文件方法
    def select(self):
        #重置进度条
        self.text.delete(0.0,999.999)
        fill_line = self.canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="white")
        self.canvas.coords(fill_line,(0,0,350,60))
        file =askopenfilename()#选择文件
        self.text.insert(0.0,file)#输出到输出框

    #采集方法
    def jd(self):
        #重置进度条
        fill_line = self.canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="white")
        self.canvas.coords(fill_line,(0,0,350,60))
        file = self.text.get(0.0,999.999).replace('\n','').replace('采集完成','')
        #初始化文件
        info_sheet = xlrd.open_workbook(file).sheet_by_index(0)
        info_max = info_sheet.nrows
        #进度条设置
        n = 350/(info_max-1)
        k = 0
        fill_line = self.canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="green")
        #存储文件路径
        path = 'result_' + str(time.strftime('%Y{y}%m{m}%d{d}%H{h}%M{f}%S{s}').format(y='年',m='月',d='日',h='时',f='分',s='秒')) + '.csv'
        with open(path,'a',newline='',encoding='gbk') as f:#写入字段头
            write = csv.writer(f,dialect='excel')
            write.writerow(['商品编码','名称','价格','plus价格','北京','上海','广州','成都','武汉','沈阳','西安','德州','促销'])
        for i in range(info_max-1):#逐条采集
            code = str(int(info_sheet.cell(i+1,0).value))#编码字符串化
            #输出采集状态到输出框
            self.text.delete(0.0,999.999)
            self.text.insert(0.0,'采集'+code)
            jd = JD(code)#实例化采集类
            result = jd.get_page()
            with open(path,'a',newline='',encoding='gbk') as f:#写入采集结果
                write = csv.writer(f,dialect='excel')
                try:
                    write.writerow(result)
                except:
                    pass
            #更新进度条
            k += 1
            c = k*n
            self.canvas.coords(fill_line,(0,0,c,60))
            self.init_window.update()
        self.text.delete(0.0,999.999)
        self.text.insert(0.0,'采集完成'+file)

    #方法线程，防止gui界面卡死
    @staticmethod
    def thread_it(func):
        t = threading.Thread(target=func) 
        t.setDaemon(True)   
        t.start()       
        #t.join()  
                            
        

def start():
    window = tk.Tk()
    JD = APP(window)
    JD.set_init_window()
    window.mainloop()

start()
