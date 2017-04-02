# -*- coding: utf-8 -*-

from Tkinter import *
from ScrolledText import ScrolledText
import requests, re, threading


def replite(ID):
    varl.set('正在获取第%d页内容' % (ID / 25 + 1))
    html = 'https://movie.douban.com/top250?start=' + str(ID)
    response = requests.get(html).text
    # response = unicode(response, 'GBK').encode('UTF-8')
    response = response.encode('utf-8   ')
    # print  response
    # reg = r'<span class="title">(.*?)</span>.*?"v:average">(.*?)</span>'
    regTitle = r'<span class="title">(.[^&]*?)</span>'
    regStars = r'.*?"v:average">(.*?)</span>'
    regTitle = re.compile(regTitle)
    regStars = re.compile(regStars)
    titles = re.findall(regTitle, response)
    stars = re.findall(regStars, response)
    info = list(zip(titles, stars))
    return info


def write():
    varl.set('开始爬取内容')
    ID = 0
    nums = 1
    while ID < 250:
        res = replite(ID)
        ID += 25
        for each in res:
            text.insert(END, 'No.%d\t%-30s%s分\n' % (nums, each[0], each[1]))
            nums += 1
    varl.set('获取内容成功')


def start():
    t1 = threading.Thread(target=write)
    t1.start()


def save():
    content = text.get("0.0", "end").encode('GBK')
    textfile = open(u'E:\\豆瓣电影排行250.txt', 'w')
    textfile.write(content)
    textfile.close()


root = Tk()

root.title('豆瓣电影top250')
root.geometry('820x500+400+200')

text = ScrolledText(root, font=('楷体', 15), width=80, height=20)
text.grid()

frame = Frame(root)
frame.grid()

# 启动爬虫功能
startButton = Button(frame, text='开始', font=('楷体', 18), command=start)
startButton.grid()
startButton.pack(side=LEFT)
# 保存爬取信息
saveButton = Button(frame, text='保存文件', font=('楷体', 18), command=save)
saveButton.grid()
saveButton.pack(side=LEFT)
# 退出程序
exitButton = Button(frame, text='退出', font=('楷体', 18), command=frame.quit)
exitButton.grid()
exitButton.pack(side=LEFT)

varl = StringVar()

info_label = Label(root, fg='red', textvariable=varl)
info_label.grid()

varl.set('准备中....')

root.mainloop()
