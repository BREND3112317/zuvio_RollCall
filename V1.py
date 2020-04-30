import os
import sys
import time
import random
import threading
import json
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

_Url = "https://irs.zuvio.com.tw/student5/irs/index"
_Opts = Options()
_Opts.add_argument("--headless")  # 使用背景執行
_Driver = webdriver.Chrome(executable_path="chromedrive\\chromedriver.exe", chrome_options=_Opts)
_SleepTime = [2, 4, 8, 16, 32]
_Threads = []
_Day = 0

def jsonPrepare(path):
	with open(path, encoding="utf-8") as reader:
		jf = json.loads(reader.read())
	return jf;

def Login(account, password):
	_Driver.get(_Url)
	if (_Driver.title == "Zuvio 即時反饋系統"):
		print("正在登入")
		_Driver.find_element_by_id('myform').find_element_by_id('email').send_keys(account)
		_Driver.find_element_by_id('myform').find_element_by_id('password').send_keys(password)
		_Driver.find_element_by_name("myform").submit()
	if (_Driver.title == "Zuvio 即時反饋系統"):
		return False
	print("以登入")
	return True

def goRollCall(irsNumber, day):
	while day == _Day:
		try:
			#進入課程點名畫面
			_Driver.execute_script("irs_currentRollcall(" + str(irsNumber) + ")")
			_Driver.refresh()
			className = _Driver.find_element_by_xpath("//div[@class='back-button-title']").text
			wiatTime = 28+random.choice(_SleepTime)
			if len(_Driver.find_elements_by_xpath("//div[@class='no-active']"))>0:
				print(str(irsNumber) + " - " + className +"\n\t尚未開放登入，等待" + str(wiatTime) + "秒後繼續")
			else:
				_Driver.execute_script("makeRollcall(" + rollcall_id +")")
				print(str(irsNumber) + " - " + className +"\n\t簽到id: " + rollcall_id + "已簽到，" + str(wiatTime) + "秒後繼續")
			time.sleep(wiatTime)
		except:
			print("RollCall Error")
	return

def main(Json_path):
	json_Course = jsonPrepare(Json_path)
	if Login(json_Course['account'], json_Course['password']) == False:
		print("登入錯誤")
		return
	global _Day
	while True:
		_Threads = []
		if _Day != (time.localtime().tm_wday+1):
			_Day = time.localtime().tm_wday+1
			print("星期 " + str(_Day))
			print("準備開始簽到")
			for course in json_Course['course']:
				t = threading.Thread(target=goRollCall, args=(course['id'], course['week']))
				t.start()
				_Threads.append(t)
				time.sleep(1)
				
			for thread in _Threads:
				thread.join()
		time.sleep(30)

if __name__ == "__main__":
	#argv[1]: jsonPath
	print("run: " + sys.argv[0])
	main(sys.argv[1])
	os.system('pause')
	_Driver.quit()