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
#_Opts.add_argument("--headless")  # 使用背景執行
_Opts.add_argument("--incognito")  # 使用無痕模式
_Driver = webdriver.Chrome(executable_path="chromedrive\\chromedriver.exe", chrome_options=_Opts)
_Course = []
_Threads = []


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

def goRollCall(irsNumber, irsName):
	while true:
		try:
			#進入課程點名畫面
			_Driver.execute_script("irs_currentRollcall(" + str(irsNumber) + ")")
			wiatTime = 60+random.randint(-30,30)
			make = _Driver.find_elements_by_xpath("//div[@id='submit-make-rollcall']")
			if len(make)>0 & make[0].test=="我到了":
				_Driver.execute_script("makeRollcall(rollcall_id)")
				print(str(irsNumber) + " - " + irsName +"\n\t已簽到，" + str(wiatTime) + "秒後繼續")
			else:
				print(str(irsNumber) + " - " + irsName +"\n\t尚未開放登入，等待" + str(wiatTime) + "秒後繼續")
			time.sleep(wiatTime)
		except:
			print("RollCall Error.\n\t irsNumber: " + str(irsNumber))
			time.sleep(5)
	return
	
def getCourse():
	GetUrl(_Url)
	print("\t所有課程")
	Course = []
	htmlCourses = _Driver.find_elements_by_xpath("//div[@class='i-m-p-c-a-c-l-course-box']")
	for hc in htmlCourses:
		hcValue = [hc.get_attribute('data-course-id'), hc.text.split("\n")[0]]
		print(hcValue[0] + " - " + hcValue[1])
		Course.append(hcValue)

	return Course
	

def main(Account, Password):
	while True:
		if Login(Account, Password) == False:
			return
		_Course = getCourse()
		_Threads = []
		print("準備開始簽到")
		for course in _Course:
			t = threading.Thread(target=goRollCall, args=(course[0], course[1]))
			t.start()
			_Threads.append(t)
			time.sleep(random.randint(0,5))
			
		for thread in _Threads:
			thread.join()
		


if __name__ == "__main__":
	#argv[1]: account
	#argv[2]: password
	print("run: " + sys.argv[0])
	main(sys.argv[1], sys.argv[2])
	os.system('pause')
	_Driver.quit()