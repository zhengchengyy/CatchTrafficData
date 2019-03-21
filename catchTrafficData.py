import re
import json
import time
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

#地点和对应编号
city_dic = {'北碚': 2358, '璧山': 2359, '长寿': 2360, '城口': 2361, '大足': 2362, '垫江': 2363, '丰都': 2364, '奉节': 2365, '涪陵': 2366, '合川': 2367, '江北': 2368, '江津': 2369, '开县': 2370, '梁平': 2371, '南川': 2372, '彭水': 2374, '綦江': 2375, '黔江': 2376, '荣昌': 2377, '石柱': 2378, '铜梁': 2379, '潼南': 2380, '万州': 2381, '巫山': 2382, '巫溪': 2383, '武隆': 2384, '秀山': 2385, '永川': 2386, '酉阳': 2387, '忠县': 2388, '重庆': 2389}

#点击全部，获得所有数据页
def click_all():
    try:
        #由于刷新太快得不到数据，放慢2秒
        time.sleep(2)
        all = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#allMonth"))
        )
        all.click()
    except TimeoutException:
        return click_all()

#翻页
def next_page():
    try:
        next = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mypagination1 > ul > li:nth-child(9) > a"))
        )
        next.click()
    except TimeoutException:
        return next_page()

#查看更多
def get_more(offset):
    try:
        string = "#xzHdContent > table > tbody > tr:nth-child("+str(offset)+") > td:nth-child(9) > button"
        more = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, string))
        )
        more.click()
    except TimeoutException:
        return get_more(offset)


#获取交通违法记录
def get_record():
    #从主页面到子页面，句柄还停留在主页面，所以无法定位到子页面的元素，
    #switch_to_window这个方法不稳定，有时候才能用，不过没找到更好的
    browser.switch_to_window(browser.window_handles[1])
    #测试当前网页地址
    #url = browser.current_url
    #print(url)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                 '#detailContent')))
    html = browser.page_source

    #试过pquery，发现麻烦，使用正则表达式解析
    record = re.compile('<th>车辆号牌种类</th>.*?<td>(.*?)</td>.*?'
                              '<th>事故事实</th>.*?<td.*?>(.*?)</td>.*?'
                              '<th>事故认定部门</th>.*?<td.*?>(.*?)</td>.*?'
                              , re.S)
    items = re.findall(record, html)
    #可以用来测试是否提取到数据，与产生的字典比较
    print(items)
    for item in items:
        #item是元祖（tuple）类型，不能修改！！！
        #item[3] = time_trip(item[3])错！！！
        time_new = time_parse(item[1])
        # location_new = location_parse(item[2])
        location_new = location_parse_detail(item[1])
        event_new = event_parse(item[1])
        #得到的时间格式为2017-08-25 07:05:00，需要进行切片
        time_trip = time_new[0:10]
        #wea = get_weather(location_new[0:2],time_trip)
        yield {
            'type': item[0],
            'impact': event_new,
            'location': location_new,
            'time': time_new,
            #'weather':wea
        }

    browser.close()
    browser.switch_to_window(browser.window_handles[0])

#解析时间
def time_parse(event):
    timeArray = re.findall(r"于(\d.*?)驾驶",event)
    if(len(timeArray)):
        return timeArray[0]
    else:
        return "--"


#解析地点
#杨思远于2017-05-03 06:12:00驾驶鲁D53593大型汽车车辆
#在重庆市内环快速路南岸区段南岸上5km+600m发生事故,至1人死亡,0人受伤,100直接财产损失,承担同等责任
#重庆市公安局交通巡逻警察总队城市快速道路支队
def location_parse(location):
    #注意location返回的是列表
    #酉阳土家族苗族，秀山土家族苗族
    location = re.findall(r"重?庆?市?公?安?局?(.*?)自?治?新?[县区]",location)
    #万一没解析到，就会报错，加个判断条件
    if(len(location)):
        return location[0]
    else:
        return "--"

#解析详细地点
def location_parse_detail(event):
    location = re.findall(r"在+(.*?)发生事故+",event)
    if(len(location)):
        return location[0]
    else:
        return "--"

#解析事故影响
def event_parse(event):
    impact = re.findall(r"(至\d.*?损失)", event)
    if(len(impact)):
        return impact[0]
    else:
        return "--"

#获取天气
def get_weather(location,time):
    if(location=="--")or(time=="--"):
        return "--"
    city_id = str(get_id(location))
    weaurl = "http://v.juhe.cn/historyWeather/weather?city_id="\
             +city_id+"&weather_date="+time+"&key=366ac9280204fb8250077ea58c74508e"
    content = requests.get(weaurl).text
    pattern = re.compile('day_weather":"(.*?)","night_weather',re.S)
    results = re.findall(pattern,content)
    if(len(results)):
        return results[0]
    else:
        return "--"

# 写入文件
def write_to_file(content):
    with open('result.txt', 'a', encoding='utf-8') as f:
            f.write(json.dumps(content, ensure_ascii=False) + '\n')
            f.close()

#获取城市id
def get_id(location):
    #字典用[]取数据
    #python3已经不用has_key来判断是否存在key了,用key in dict
    if(location in city_dic):
        city_id = city_dic[location]
    else:
        city_id = 2389
    #找不到直接用重庆的天气，重庆id=2389
    return city_id


if __name__ == '__main__':
    # 自动唤起chrome
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10)
    browser.get('http://cq.122.gov.cn/views/swfzpub.html')  #死亡事故
    # browser.get('https://cq.122.gov.cn/views/viopub.html')  #重点车辆违法行为

    page = 31
    total = 20
    click_all()
    for j in range(1, page + 1):
        for i in range(1, total + 1):
            get_more(i)
            for item in get_record():
                print(item)
                write_to_file(item)
        next_page()

    browser.quit()