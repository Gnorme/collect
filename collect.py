from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timezone
from itertools import chain
import psycopg2 as pg
import pytesseract
import logging
import time
import cv2
import os

try:
	import Image
except ImportError:
	from PIL import Image


class Collector():
	def setup(self, threadName, browser='Firefox',useProxy=True):
		if os.name == 'nt':
			pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'
		logging.basicConfig(level=logging.INFO, filename='test.log',filemode='a')
		self.useProxy = useProxy
		self.browser = browser
		self.StartBrowser()
		self.number = 1
		self.nextNumber = 1
		self.failInfo = ''
		self.specificPlace = ''
		self.count = 0
		self.threadName = str(threadName)
	def StartBrowser(self):
		if self.browser == 'Firefox':
			profile = webdriver.FirefoxProfile()
			#profile.set_preference('webdriver.load.strategy', 'unstable')
			capabilities = {"pageLoadStrategy":"none"}
			profile.set_preference("browser.helperApps.neverAsk.saveToDisk","application/pdf")
			profile.set_preference('pdfjs.disabled',True)
			profile.set_preference("browser.download.manager.showWhenStarting", False);
			profile.set_preference("browser.download.folderList", 2)
			if os.name is not 'nt':
				profile.set_preference("browser.download.dir", '/home/gnorme/Downloads')
			profile.set_preference("browser.download.useDownloadDir", True)
			profile.set_preference("services.sync.prefs.sync.browser.download.manager.showWhenStarting", False)
			profile.set_preference('browser.link.open_newwindow', 3)
			profile.set_preference('browser.link.open_newwindow.restriction', 0)
			profile.set_preference('browser.link.open_newwindow.override.external', -1)
			if self.useProxy:
				self.GetProxy()
				#profile.set_preference('dom.popup_allowed_events', 0)
				profile.set_preference("network.proxy.type", 1)
				profile.set_preference("network.proxy.http", self.proxy[0])
				profile.set_preference("network.proxy.http_port", int(self.proxy[1]))
				profile.set_preference("network.proxy.ssl", self.proxy[0])
				profile.set_preference("network.proxy.ssl_port", int(self.proxy[1]))
			self.driver = webdriver.Firefox(profile, capabilities=capabilities,executable_path='geckodriver')
		if self.browser == 'Chrome':
			chrome_options = webdriver.ChromeOptions()
			chrome_options.add_argument("--disable-infobars")
			prefs = {"download.prompt_for_download": False, "plugins.always_open_pdf_externally": True}
			chrome_options.add_experimental_option("prefs",prefs)
			capabilities = {"pageLoadStrategy":"none"}
			chrome_options.add_argument('--silent')
			chrome_options.add_argument('--disable-logging')
			if self.useProxy:
				self.GetProxy()
				chrome_options.add_argument('--proxy-server='+self.proxy[0]+':'+self.proxy[1])
			self.driver = webdriver.Chrome(chrome_options=chrome_options,desired_capabilities=capabilities)
		self.driver.set_window_size(1080,1000)

	def Captcha(self, times):
		if self.useProxy:
			try:
				self.driver.get("https://servicesenligne2.ville.montreal.qc.ca/sel/evalweb/index")
			except WebDriverException:
				self.ChangeProxy()
				self.driver.get("https://servicesenligne2.ville.montreal.qc.ca/sel/evalweb/index")
		else:
			self.driver.get("https://servicesenligne2.ville.montreal.qc.ca/sel/evalweb/index")
		for i in range(0,times):
			try:
				element_present = EC.visibility_of_element_located((By.XPATH, '//*[@id="type_recherche"]/div[5]/div/img'))
				wait = WebDriverWait(self.driver, 15).until(element_present)
			except TimeoutException:
				self.ChangeProxy()
				self.driver.get("https://servicesenligne2.ville.montreal.qc.ca/sel/evalweb/index")
				continue
			try:
				self.driver.save_screenshot('screenshot'+self.threadName+'.png')
			except:
				time.sleep(0.5)
				self.driver.save_screenshot('screenshot'+self.threadName+'.png')

			time.sleep(0.5)
			code = self.Solve()
			self.driver.find_element_by_name("HTML_FORM_FIELD").send_keys(code)
			btn = self.driver.find_element_by_tag_name("button")
			btn.click()
			try:
				wait = WebDriverWait(self.driver, 10)
				wait.until(EC.staleness_of(btn))
			except TimeoutException:
				self.failInfo = 'Timeout on captcha'
				return False
			try:
				self.driver.find_element_by_name("HTML_FORM_FIELD")
			except NoSuchElementException:
				return True
			else:
				continue

		return False

	def Form(self, number, name, road, place):
		self.failInfo = ''
		element_present = EC.presence_of_element_located((By.ID, 'noCiviq'))
		try:
			WebDriverWait(self.driver, 10).until(element_present)
		except TimeoutException:
			return False

		num = self.driver.find_element_by_id("noCiviq")
		num.send_keys(number)

		st = self.driver.find_element_by_id("rue-tokenfield")
		st.send_keys(name)

		wait = WebDriverWait(self.driver, 10)
		try:
			wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-menu-item")))
		except TimeoutException:
			return False

		places = []
		placeOptions = []
		dropdown = self.driver.find_element_by_xpath('//*[@id="ui-id-1"]')
		for option in dropdown.find_elements_by_tag_name('li'):
			words = option.text.split(' ')
			if road in words and name in words and '('+place+')' in words:
				places.append(option.text)
				placeOptions.append(option)
				#break
		try:
			if len(self.specificPlace) > 0:
				if self.specificPlace in places:
					index = places.index(self.specificPlace)
					if index >= 0:
						placeOptions[index].click()
					else:
						placeOptions[0].click()
				else:
					placeOptions[0].click()
			else:
				placeOptions[0].click()
		except IndexError:
			self.failInfo = 'Index error'
			return False

		btn = self.driver.find_element_by_id('btnRechercher')
		btn.click()

		wait = WebDriverWait(self.driver, 10)
		try:
			wait.until(EC.staleness_of(btn))
		except TimeoutException:
			return False
		#If number is out of acceptable range, select option and update next number
		try:
			return self.ChooseOpt(number, name)
		except NoSuchElementException:
			try:
				error = self.driver.find_element_by_xpath('//*[@id="noVoie.errors"]')
				self.specificPlace = ''
			except NoSuchElementException:
				return True
			if len(places) > 1:
				for place in places[1:]:
					try:
						close = self.driver.find_element_by_xpath('//*[@id="adressForm"]/div/div[2]/div/div/a')
						close.click()
					except NoSuchElementException:
						return False
					if self.TryNextPlace(place, name):
						try:
							return self.ChooseOpt(number, name)
						except NoSuchElementException:
							return True
			#No numbers within 10 so skip ahead 8 (2 more added when Collect returns False)
			self.nextNumber += 8
			self.failInfo = "Doesn't exist"
			return False
	def ChooseOpt(self, number, name):
		options = self.driver.find_elements_by_name("index")
		btn = self.driver.find_element_by_id("btnSoumettre")
		if len(options) > 1:
			for option in options:
				optNumber = self.ParseOptions(option.find_element_by_xpath("../../.").text, name)
				if number > optNumber:
					continue
				elif number <= optNumber:
					option.click()
					btn.click()
					return True
			self.failInfo = "Doesn't exist"
			return False
		elif len(options) == 1:
			optNumber = self.ParseOptions(options[0].find_element_by_xpath("../../.").text, name)
			if number > optNumber:
				self.failInfo = "Doesn't exist"
				return False
			elif number <= optNumber:
				options[0].click()
				btn.click()
				return True
		else:
			return True
	def TryNextPlace(self, place, name):
		st = self.driver.find_element_by_id("rue-tokenfield")
		st.send_keys(name)
		try:
			wait = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "ui-menu-item")))
		except TimeoutException:
			return False

		dropdown = self.driver.find_element_by_xpath('//*[@id="ui-id-1"]')
		for option in dropdown.find_elements_by_tag_name('li'):
			if option.text == place:
				option.click()
				break

		try:
			wait = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.ID, 'btnRechercher')))
		except TimeoutException:
			return False

		btn = self.driver.find_element_by_id('btnRechercher')
		btn.click()

		try:
			wait = WebDriverWait(self.driver, 10).until(EC.staleness_of(btn))
		except TimeoutException:
			return False

		try:
			error = self.driver.find_element_by_xpath('//*[@id="noVoie.errors"]')
			return False
		except NoSuchElementException:
			self.specificPlace = place
			return True

	def NextStreet(self):
		conn = self.ConnectDB()
		c = conn.cursor()
		c.execute("SELECT * FROM Montreal WHERE status = 'In Progress' AND claimed_by = (%s);",(self.threadName,))
		entry = c.fetchone()
		if entry:
			pass
		else:
			c.execute("SELECT * FROM Montreal WHERE status IS NULL ORDER BY street")
			entry = c.fetchone()
		if entry:
			street = entry[0]
			place = entry[1]
			c.execute("SELECT l_first, l_last FROM numbers WHERE street = (%s) AND place = (%s)", (street,place))
			left = c.fetchall()
			c.execute("SELECT r_first, r_last FROM numbers WHERE street = (%s) AND place = (%s)", (street,place))
			right = c.fetchall()
			c.execute("UPDATE Montreal SET status = 'In Progress' WHERE street = (%s) AND place = (%s)", (street,place))
			c.execute("UPDATE Montreal SET claimed_by = (%s) WHERE street = (%s) AND place = (%s)", (self.threadName,street,place))
			conn.commit()
			c.close()
			conn.close()
			leftRange = []
			rightRange = []
			for row in left:
				leftRange.append(tuple(map(int,row)))
			for row in right:
				rightRange.append(tuple(map(int,row)))

			leftN = list(self.JoinRanges(leftRange))
			rightN = list(self.JoinRanges(rightRange))

			if leftN[0] == (0,0):
				leftN.remove((0,0))
			if rightN[0] == (0,0):
				rightN.remove((0,0))

			addresses = {"Street": street, "Left":leftN,"Right":rightN, "Place": place, "LastNum": entry[3], "LastSide":entry[4]}
			return addresses
		else:
			print("Encountered an error fetching next street.")

	def CollectSide(self, side, addresses, start):
		place = addresses["Place"]
		street = addresses["Street"].split(' ')
		if street[0][0].isdigit():
			road = street[1]
			name = street[0]
		else:
			road = street[0]
			name = street[1]

		self.nextNumber = int(start)
		for r in addresses[side]:
			if self.nextNumber < r[0]:
				self.nextNumber = r[0]
			while self.nextNumber <= r[1]:
				self.number = self.nextNumber
				if self.Collect(self.number, name, road, place):
					self.count += 1
					self.UpdateStreet(self.number, side, addresses["Street"], place)
					if self.count > 50:
						self.count = 0
						self.RefreshWindow()
				else:
					self.UpdateStreet(self.number, side, addresses["Street"], place)
					self.ReportFail(self.number, side, addresses["Street"], place)
					self.nextNumber += 2
		self.specificPlace = ''

	def Collect(self, number, name, road, place):
		if self.Captcha(5) == False:
			logging.info('Captcha failed 5 times')
			return False
		if self.Form(number, name, road, place) == False:
			logging.info('Form failed for %s %s %s %s', number, name, road, place)
			return False
		if self.SaveData(name) == True:
			return True
		else:
			logging.info('Save data failed for %s %s %s %s', number, name, road, place)
			return False
	def SaveData(self,name):
		element_present = EC.presence_of_element_located((By.ID, "section-1"))
		try:
			wait = WebDriverWait(self.driver, 10).until(element_present)
		except TimeoutException:
			return False
		tables = ['1','2','3','4']
		address = self.driver.find_element_by_xpath('//*[@id="section-1"]/table/tbody/tr[1]/th').text
		filename = address.replace(' - ', '-').replace(' ','_')
		#Save all text from tables to file
		try:
			with open('data/'+filename + '.txt','w') as f:
				for i in tables:
					table = self.driver.find_element_by_xpath('//*[@id="section-'+i+'"]/table')
					for tr in table.find_elements_by_tag_name("tr"):
						f.write(tr.text + '\n')
		except Exception as e:
			logging.debug(e)
			return False
		#Download .pdfs of previous years
		try:
			links = self.driver.find_elements_by_partial_link_text("Compte de taxes")
			for link in links[1:]:
				link.click()
		finally:
			if name in address:
				self.number = self.ParseOptions(address, name)
				if self.nextNumber > self.number:
					self.number = self.nextNumber
					self.nextNumber += 2
				else:
					self.nextNumber = self.number + 2
			else:
				self.number = self.nextNumber
				self.nextNumber += 2

			return True

	def Solve(self):
		img = cv2.imread('screenshot'+self.threadName+'.png',0)[734:754, 412:509]
		ret, th = cv2.threshold(img, 80, 255, cv2.THRESH_TOZERO_INV)
		ret, th2 = cv2.threshold(th, 10, 255, cv2.THRESH_BINARY_INV)
		new = Image.fromarray(th2)
		text = pytesseract.image_to_string(new, config="-psm 5 letters")
		captcha = ''

		for c in text[::-1]:
			captcha += c.strip()

		if (len(captcha)) < 6:
			captcha = pytesseract.image_to_string(new, config="-psm 6 letters")

		return captcha

	def JoinRanges(self, data, offset=2):
		LEFT, RIGHT = 1, -1
		flatten = chain.from_iterable
		data = sorted(flatten(((start, LEFT), (stop + offset, RIGHT)) for start, stop in data))
		c = 0
		for value, label in data:
			if c == 0:
				x = value
			c += label
			if c == 0:
				yield x, value - offset

	def RefreshWindow(self):
		self.Close()
		if self.useProxy:
			self.ReleaseProxy()
		self.StartBrowser()
	def ConnectDB(self):
		while True:
			try:
				conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
				return conn
			except pg.OperationalError:
				print("DB connect failed")
				logging.info("DB Connect failed")
				time.sleep(120)

	def ReportFail(self, number, side, street, place):
		conn = self.ConnectDB()
		c = conn.cursor()
		c.execute("INSERT INTO Fails (num, street, place, side, info) VALUES (%s, %s, %s, %s, %s);", (number, street, place, side, self.failInfo))
		conn.commit()
		c.close()
		conn.close()
	def GetProxy(self):
		conn = self.ConnectDB()
		c = conn.cursor()
		c.execute("SELECT ip,port FROM Proxies WHERE status = 'Working' ORDER BY response;")
		self.proxy = c.fetchone()
		c.execute("UPDATE Proxies SET status = 'In Use' WHERE ip = (%s) AND port = (%s);",(self.proxy[0],self.proxy[1]))
		conn.commit()
		c.close()
		conn.close()
	def ReleaseProxy(self):
		conn = self.ConnectDB()
		c = conn.cursor()
		c.execute("UPDATE Proxies set status = 'Working' WHERE ip = (%s) AND port = (%s);", (self.proxy[0], self.proxy[1]))
		conn.commit()
		c.close()
		conn.close()
	def ChangeProxy(self):
		self.driver.quit()
		conn = self.ConnectDB()
		c = conn.cursor()
		c.execute("UPDATE Proxies SET status = 'Stale' WHERE ip = (%s) AND port = (%s);",(self.proxy[0],self.proxy[1]))
		conn.commit()
		c.close()
		conn.close()
		self.StartBrowser()
	def UpdateStatus(self, status,street,place):
		conn = self.ConnectDB()
		c = conn.cursor()
		c.execute("UPDATE Montreal SET status = (%s) WHERE street = (%s) AND place = (%s);",(status,street,place))
		conn.commit()
		c.close()
		conn.close()
	def UpdateStreet(self, number, side, street, place):
		conn = self.ConnectDB()
		c = conn.cursor()
		c.execute("UPDATE Montreal SET last_number = (%s) WHERE street = (%s) AND place = (%s)",(number,street,place))
		c.execute("UPDATE Montreal SET last_side = (%s) WHERE street = (%s) AND place = (%s)",(side,street,place))
		c.execute("UPDATE Montreal SET last_modified = (%s) WHERE street = (%s)AND place = (%s)",(datetime.now(),street,place))
		conn.commit()
		c.close()
		conn.close()
	def ParseOptions(self, label, name):
		nameIndex = label.find(name)
		index = label[:nameIndex].find(' - ')
		if index >= 0:
			index2 = label[index+3:].find(' ')
			n2 = label[index+3:index+3+index2]
			if n2.isdigit():
				return int(n2)
			else:
				return int(''.join(filter(lambda x: x.isdigit(), n2)))
		else:
			index2 = label.find(' ')
			n1 = label[:index2]
			if n1.isdigit():
				return int(n1)
			else:
				try:
					return int(''.join(filter(lambda x: x.isdigit(), n1)))
				except ValueError:
					return 0
	def Debug(self):
		self.driver.get("http://www.google.ca")
	def Close(self):
		self.driver.close()
