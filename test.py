from selenium import webdriver
import time

def LongTest():
	chrome_options = webdriver.ChromeOptions()
	prefs = {"download.prompt_for_download": False, "plugins.always_open_pdf_externally": True}
	chrome_options.add_experimental_option("prefs",prefs)
	chrome_options.add_argument('--proxy-server=%s' % '107.182.236.129:80')
	driver = webdriver.Chrome(chrome_options=chrome_options)
	driver.get("https://servicesenligne2.ville.montreal.qc.ca/sel/evalweb/index")
	time.sleep(360)

def CloseTest():
	driver = webdriver.Firefox()
	driver.switch_to_window('8')
	for handle in driver.window_handles:
		print(handle)



LongTest()
#driver = webdriver.Firefox()
#print(driver.current_window_handle)
#time.sleep(100)