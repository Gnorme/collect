from collect import Collector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from pyvirtualdisplay import Display
import psycopg2 as pg
import sys

def CheckStreet(driver, street, place):
	if street[0][0].isdigit():
		road = street[1]
		name = street[0]
	else:
		road = street[0]
		name = street[1]
	places = []
	element_present = EC.visibility_of_element_located((By.ID, 'noCiviq'))
	try:
		WebDriverWait(driver, 10).until(element_present)
	except TimeoutException:
		return False

	num = driver.find_element_by_id("noCiviq")
	num.clear()
	num.send_keys('1')

	st = driver.find_element_by_id("rue-tokenfield")
	st.clear()
	st.send_keys(name)

	wait = WebDriverWait(driver, 10)
	try:
		wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-menu-item")))
	except TimeoutException:
		return False

	dropdown = driver.find_element_by_xpath('//*[@id="ui-id-1"]')
	for option in dropdown.find_elements_by_tag_name('li'):
		words = option.text.split(' ')
		if road in words and name in words and '('+place+')' in words:
			places.append(option.text)

	if len(places) == 0:
		return False

def GetStreets():
	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	c.execute("SELECT street, place FROM Montreal")
	streets = c.fetchall()
	c.close()
	conn.close()
	return streets

display = Display(visible=0,size=(1080,1000))
display.start()
v = Collector()
if sys.argv[1] == 'True':
	useProxy = True
elif sys.argv[1] == 'False':
	useProxy = False
v.setup('Verifier',browser='Firefox', useProxy=useProxy)
v.Captcha(5)
streets = GetStreets()
fails = []

for entry in streets:
	try:
		street = entry[0].split(' ')
		place = entry[1]
		if CheckStreet(v.driver, street, place) == False:
			fails.append(entry)
	except:
		continue

with open('fails.txt', 'w', encoding='utf-8') as f:
	for fail in fails:
		try:
			f.write(fail[0] + ' ' + fail[1] + '\n')
		except:
			continue
	#put any number in nociviq
	#put street in rue-tokenfield
	#check dropdown if it exists
	#if no, add to list
