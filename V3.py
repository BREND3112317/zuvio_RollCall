import os
import sys
import time
import random
import threading
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

_Url = "https://irs.zuvio.com.tw/student5/irs/index"
_Opts = Options()
_Opts.add_argument("--headless")  # 使用背景執行
_Opts.add_argument("--incognito")  # 使用無痕模式
_Driver = webdriver.Chrome(executable_path="chromedrive\\chromedriver.exe")
_Course = []
_Threads = []
_Day = 0


def GetUrl(url):
	if _Driver.current_url != url:
		_Driver.get(url)

def Login(account, password):
	GetUrl(_Url)
	if (_Driver.title == "Zuvio 即時反饋系統"):
		print("正在登入 - ")
		_Driver.find_element_by_id('myform').find_element_by_id('email').send_keys(account)
		_Driver.find_element_by_id('myform').find_element_by_id('password').send_keys(password)
		_Driver.find_element_by_name("myform").submit()
	if (_Driver.title == "Zuvio 即時反饋系統"):
		print("\t登入失敗")
		return False
	print("\t登入成功")
	return True
	
def goRollCall(Driver, account, password, irsNumber, irsName, day):
	Driver.get(_Url)
	if (Driver.title == "Zuvio 即時反饋系統"):
		print("正在登入 - ")
		Driver.find_element_by_id('myform').find_element_by_id('email').send_keys(account)
		Driver.find_element_by_id('myform').find_element_by_id('password').send_keys(password)
		Driver.find_element_by_name("myform").submit()
	if (Driver.title == "Zuvio 即時反饋系統"):
		print("\t登入失敗")
		return
	print("\t登入成功")
	while day == _Day:
		try:
			#進入課程點名畫面
			Driver.execute_script("irs_currentRollcall(" + str(irsNumber) + ")")
			wiatTime = 60+random.randint(-30,30)
			if len(Driver.find_elements_by_xpath("//div[@class='no-active']"))>0:
				print(str(irsNumber) + " - " + irsName +"\n\t尚未開放登入，等待" + str(wiatTime) + "秒後繼續")
			else:
				Driver.execute_script("makeRollcall(rollcall_id)")
				print(str(irsNumber) + " - " + irsName +"\n\t已簽到，" + str(wiatTime) + "秒後繼續")
			time.sleep(wiatTime)
		except:
			print("RollCall Error.\n\t irsNumber: " + str(irsNumber))
			time.sleep(5)
	Driver.quit()
	return
	
def getCourse():
	GetUrl(_Url)
	print("\t所有課程")
	Course = []
	Courses = _Driver.find_elements_by_xpath("//div[@class='i-m-p-c-a-c-l-course-box']")
	for hc in Courses:
		hcValue = [hc.get_attribute('data-course-id'), hc.text.split("\n")[0]]
		print(hcValue[0] + " - " + hcValue[1])
		Course.append(hcValue)

	return Course
	

def main(Account, Password):
	Login(Account, Password)
	global _Day
	_Course = getCourse()
	while True:
		_Threads = []
		if _Day != (time.localtime().tm_wday+1):
			_Day = time.localtime().tm_wday+1
			print("準備開始簽到")
			for course in _Course:
				driver = webdriver.Chrome(executable_path="chromedrive\\chromedriver.exe", chrome_options=_Opts)
				t = threading.Thread(target=goRollCall, args=(driver, Account, Password, course[0], course[1], int(_Day)))
				t.start()
				_Threads.append(t)
				time.sleep(random.randint(0,5))
				
			for thread in _Threads:
				thread.join()
		time.sleep(30)


if __name__ == "__main__":
	#argv[1]: account
	#argv[2]: password
	print("run: " + sys.argv[0])
	main(sys.argv[1], sys.argv[2])
	os.system('pause')
	_Driver.quit()