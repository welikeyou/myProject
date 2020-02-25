'''
Created on 2019年7月5日

@author: dell
'''
# 动态获取网址
# 导入MySQLdb需要的安装的包是pip install mysqlclient
import MySQLdb
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
import utils.parse_text_re as MyRe
import threading
import queue as Queue
from datetime import datetime
import time

# 获取页面招标信息，并调用MyRe来解析，content_class表示包含所有招标信息的容器的class名称（要包含招标标题）
# content_value表示招标内容中包含的文字，主要用于判断文字是否被加载出来
# 通过多线程来解析
def crawl_page_data(url,content_class):
    try:

        browser.get(url)
        soup = BeautifulSoup(browser.page_source, "lxml")
        print(url)
        # 爬取网页信息
        # 需要等待信息全部加载后再读取
        # wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, "SnF_partSeqLength legend"), u"Length:  51 bp"))
        info_text = soup.find(class_=content_class).get_text()
        info_text.encode('utf-8')
        print(info_text)
        # parseData = MyRe.parse_local_data(info_text)
        # 将数据插入数据库
        # cur.execute(
        #     'INSERT INTO spider_data (jia_name,jia_contact_way,jia_linkman,yi_name,yi_contact_way,yi_linkman,web_url,has_agency,address,content,money,amount,times) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        #     (parseData.jia_name, parseData.jia_contact_way, parseData.jia_linkman, parseData.yi_name,
        #      parseData.yi_contact_way, parseData.yi_linkman, parseData.web_url, parseData.has_agency, parseData.address,
        #      parseData.content, parseData.money, parseData.amount, parseData.time))
    except Exception as e:
        print(e)

def get_page_info():
    try:
        browser.get("http://parts.igem.org/wiki/index.php/Part:BBa_K314110")  # 起始地址
        input = browser.find_element_by_class('mediawiki ltr sitedir-ltr ns-0 ns-subject page-Part_BBa_K314110 skin-igem action-view')  # 找到id为kw的元素
        input.send_keys("医院 中标公告")  # 敲入要搜索的关键字
        input.send_keys(Keys.ENTER)  # 敲入回车
        wait = WebDriverWait(browser, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'c_swrap')))  # 等待某个元素加载出来
        browser.switch_to.window(browser.window_handles[1])  # 切换到跳转后的标签页
        # myWait.until(EC.presence_of_element_located((By.CLASS_NAME, 'sd_page')))  # 等待某个元素加载出来
        wait.until(EC.text_to_be_present_in_element((By.ID, "resultpage"), u"下一页"))  # 因为下一页按钮是动态加载的，所以不能直接等待class加载。
        # 得到总页数
        totalPage = browser.find_element_by_css_selector('#resultpage > a:nth-last-child(2)').text
        print(totalPage)
        i = 0
        while i < int(totalPage):
            i = i + 1
            wait.until(EC.text_to_be_present_in_element((By.ID, "resultpage"), u"下一页"))
            html = browser.page_source
            # pq模块解析网页源代码
            doc = pq(html)
            pageUrlInfos = doc(".artitem").items()
            for pageUrlInfo in pageUrlInfos:
                # 定位到url
                pageNum = pageUrlInfo("h2 a").attr("href")
                pageTime = pageUrlInfo(".afoot > span:last-child").text()
                # 组合得到可访问的url
                theUrl = "https://show.job592.com/zb/"
                # 在这里调用解析详情的函数
                crawl_page_data(theUrl, "c_swrap", "中标")
                print(theUrl)
            # 获取到下一页的按钮
            nextPage = browser.find_element_by_css_selector('#resultpage > a:last-child')
            nextPage.click()

    finally:
        print("hahaha")

if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # 不加载图片,加快访问速度
    options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
    chromedriver_path = "C:\Program Files (x86)\Google\Chrome\Application/chromedriver.exe"  # 改成你的chromedriver的完整路径地址
    browser = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    wait = WebDriverWait(browser, 10)  # 超时时长为10s
    pageUrlList = []  # 用于保存爬取到的网址
    try:
        # 连接数据库，改成自己数据的名称和密码
        # conn = MySQLdb.connect(host="localhost", user="root", passwd="123456", db="spider_data", charset='utf8')
        # # 创建游标
        # cur = conn.cursor()
        # 调用解析函数
        url="http://parts.igem.org/wiki/index.php/Part:BBa_K398326"
        content_class="SnF_partSeqLength legend"
        crawl_page_data(url,content_class)

    finally:
        pass
        # 解析函数调用结束后关闭数据库,确保数据库被关闭
        # cur.close()
        # conn.commit()
        # conn.close()
