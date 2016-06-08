from selenium import webdriver
import mysql.connector
import threading
import time

# 继承自threading.Thread类实现多线程
class MyThread(threading.Thread):
	def __init__(self, new_url,spider):
		super(MyThread, self).__init__()
		self.new_url = new_url
		self.spider = spider
	
	def run(self):
		self.spider.craw(self.new_url)

class SpiderMain(object):

	def craw(self,new_url):
		data = self.parse(new_url)
		self.output(data)	
		print(threading.current_thread().name + ':' + new_url)

	# 解析页面，获取目标数据
	def parse(self,new_url):
		# selenium一个用于Web应用程序测试的工具
		# Phantom JS是一个服务器端的 JavaScript API 的 WebKit
		# PhantomJS 用来渲染解析JS，Selenium 用来驱动以及与 Python 的对接，Python 进行后期的处理
		data = {}
		driver = webdriver.PhantomJS(executable_path="phantomjs.exe")
		driver.get(new_url)
		data['h'] = driver.find_element_by_xpath("//div[@class='detail_content_box']/h1").text
		data['time'] = driver.find_element_by_xpath("//div[@class='detail_content_box']/h6").text
		data['text'] = driver.find_element_by_xpath("//div[@class='noticeContentDetail']").text
		data['place'] = driver.find_element_by_xpath("//div[@class='noticePublisherCourt']").text
		driver.close()
		return data

	# 通过页面获取要爬取数据的所有页面url
	def get_new_url(self,root_url):
		num = 1
		page = 1
		new_urls = []
		driver = webdriver.PhantomJS(executable_path="phantomjs.exe")
		driver.get(root_url)
		while page <= 5:
			new_url = driver.find_element_by_xpath("//div[@class='announcement_list']/div["+str(num)+"]/div/a").get_attribute("href")
			new_urls.append(new_url)
			if num % 10 == 0:
				element_page = driver.find_element_by_xpath("//div[@id='pager']/a["+str(page+3)+"]")
				element_page.click()
				page = page + 1
				num = 1
			else :
				num = num + 1
		driver.close()
		return new_urls

	# 把解析出来的数据保存到Mysql中
	def output(self,data):
		datas = [data['h'],data['time'],data['place'],data['text']]
		conn = mysql.connector.connect(user='root', password='1994323..cx', database='mydb1')
		cursor = conn.cursor()
		# cursor.execute('create table test (h varchar(25),time varchar(20),place varchar(20), text varchar(500))')
		cursor.execute('insert into test values (%s,%s,%s,%s)', datas)
		conn.commit()
		cursor.close()
		conn.close()

if __name__=="__main__":
	Start = time.clock()
	root_url = "http://www.zjsfgkw.cn/Notice/NoticeSDList"
	obj_spider = SpiderMain()

	start = time.clock()
	new_urls = obj_spider.get_new_url(root_url)
	end = time.clock()
	print("get_urls_time:%0.2f" % (end-start))

	# 为了避免线程过多网站并发量加大导致线程挂起，将url分为7组，前6组每组7个，最后一组8个
	# 以每次十个左右的线程访问
	i = 0
	for x in range(0,6):
		threadList = [MyThread(new_url,obj_spider) for new_url in new_urls[i:i+7]]
		# 启动线程
		for t in threadList:
			t.setDaemon(True)
			t.start()
		for t in threadList:
			t.join()
		i = i + 7
		time.sleep(1)

	threadList = [MyThread(new_url,obj_spider) for new_url in new_urls[42:50]]
	# 启动线程
	for t in threadList:
		t.setDaemon(True)
		t.start()
	for t in threadList:
		t.join()

	End = time.clock()
	print("total_time:%0.2f" % (End-Start))