<<<<<<< HEAD
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from pdfminer.pdfparser import PDFParser, PDFDocument
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from itertools import chain
import sqlite3
import gc
import sys
from pympler import tracker
import objgraph
import logging
import os
import shutil
from datetime import datetime, timezone
import psycopg2 as pg
import time

def Test():
	chromeOptions = webdriver.ChromeOptions()
	prefs = {"download.prompt_for_download": False, "plugins.always_open_pdf_externally": True}
	chromeOptions.add_experimental_option("prefs",prefs)
	#chromeOptions.add_argument('--proxy-server='+'197.136.142.5:80')
	driver = webdriver.Chrome(chrome_options=chromeOptions)
	driver.get("file:///C:/Users/Me/Programs/collector/collect/IndeOOR.html")
	print(driver.current_window_handle)
	

def ClickDropdown(driver):
	road = 'Avenue'
	name = '1e'
	place = 'Montréal'
	specificPlace = ''
	places = []
	placeOptions = []
	dropdown = driver.find_element_by_xpath('//*[@id="ui-id-1"]')
	for option in dropdown.find_elements_by_tag_name('li'):
		words = option.text.split(' ')
		if road in words and name in words and '('+place+')' in words:
			places.append(option.text)
			placeOptions.append(option)	
			#break
	print(places)
	print(placeOptions)
	if len(specificPlace) > 0:
		if specificPlace in places:
			index = places.index(specificPlace)
			if index >= 0:
				placeOptions[index].click()
			else:
				placeOptions[0].click()
		else:
			placeOptions[0].click()
	else:
		placeOptions[0].click()


def ParseOptions(label):
	index = label.find(' - ')
	if index >= 0:
		index2 = label[index+3:].find(' ')
		n2 = label[index+3:index+3+index2]
		sRange = label[:index+3+index2]
		return (int(n2), sRange.strip())
	else:
		index2 = label.find(' ')
		n1 = label[:index2]
		return (int(n1), n1.strip())
def Ranges(name, place):
	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	c.execute("SELECT * FROM Montreal WHERE street = (%s) and place = (%s);",(name, place))
	entry = c.fetchone()
	if entry:
		street = entry[0]
		place = entry[1]
		c.execute("SELECT l_first, l_last FROM numbers WHERE street = (%s) AND place = (%s)", (street,place))
		left = c.fetchall()
		c.execute("SELECT r_first, r_last FROM numbers WHERE street = (%s) AND place = (%s)", (street,place))
		right = c.fetchall()
		#c.execute("UPDATE Montreal SET status = 'In Progress' WHERE street = (%s) AND place = (%s)", (street,place))
		#conn.commit()
		c.close()
		conn.close()
		leftRange = []
		rightRange = []
		for row in left:
			leftRange.append(tuple(map(int,row)))
		for row in right:
			rightRange.append(tuple(map(int,row)))

		leftN = list(JoinRanges(leftRange))
		rightN = list(JoinRanges(rightRange))
		if leftN[0] == (0,0):
			leftN.remove((0,0))
		if rightN[0] == (0,0):
			rightN.remove((0,0))
	
	print(leftN)
	print(rightN)
def JoinRanges(data, offset=2):
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
def SaveData(driver, number, name, road, place):
	filename = str(number) + '_' + name + '_' + road + '_' + place
	links = driver.find_elements_by_partial_link_text("Compte de taxes")
	for link in links[1:]:
		link.click()
		year = link.text[16:]
		filepath = 'C:\\Users\\Me\\Downloads'
		oldfilename = max([filepath +"\\"+ f for f in os.listdir(filepath)], key=os.path.getctime) 
		shutil.move(os.path.join(filepath,oldfilename),filename+'_'+year+'.pdf')

def pdftotext():
	fp = open('example.pdf', 'rb')
	parser = PDFParser(fp)
	doc = PDFDocument()
	parser.set_document(doc)
	doc.set_parser(parser)
	doc.initialize('')
	rsrcmgr = PDFResourceManager()
	laparams = LAParams()
	device = PDFPageAggregator(rsrcmgr, laparams=laparams)
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	# Process each page contained in the document.
	with open('result.txt','w',errors='ignore') as f:
		for page in doc.get_pages():
			interpreter.process_page(page)
			layout = device.get_result()
			for lt_obj in layout:
				if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
					f.write(lt_obj.get_text())
			break
def LongTest():
	chromeOptions = webdriver.ChromeOptions()
	prefs = {"download.prompt_for_download": False, "plugins.always_open_pdf_externally": True}
	chromeOptions.add_experimental_option("prefs",prefs)
	chrome_options.add_argument('--proxy-server=%s' % '104.236.13.100:8888')
	driver = webdriver.Chrome(chrome_options=chromeOptions)
	driver.get("https://servicesenligne2.ville.montreal.qc.ca/sel/evalweb/index")

def CollectSSLProxies():
	proxies = []
	driver = webdriver.Chrome()
	driver.set_window_size(1800,1000)
	driver.get("https://www.sslproxies.org/")
	opt = Select(driver.find_element_by_xpath('//*[@id="proxylisttable_length"]/label/select'))
	opt.select_by_value('80')
	for i in range(1,81):
		https = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[7]').text
		if https == 'yes':
			ip = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[1]').text
			port = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[2]').text
			proxies.append(ip + ':' + port)
	nextP = driver.find_element_by_xpath('//*[@id="proxylisttable_paginate"]/ul/li[4]/a')
	nextP.click()
	for i in range(1,81):
		try:
			https = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[7]').text
		except NoSuchElementException:
			break
		if https == 'yes':
			ip = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[1]').text
			port = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[2]').text
			proxies.append(ip + ':' + port)

	with open('proxies.txt','w') as f:
		for proxy in proxies:
			f.write(proxy + '\n')	
def CollectUSProxies():
	proxies = []
	driver = webdriver.Chrome()
	driver.set_window_size(1800,1000)
	driver.get("https://www.us-proxy.org/")
	opt = Select(driver.find_element_by_xpath('//*[@id="proxylisttable_length"]/label/select'))
	opt.select_by_value('80')
	for i in range(1,81):
		https = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[7]').text
		if https == 'yes':
			ip = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[1]').text
			port = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[2]').text
			proxies.append(ip + ':' + port)
	nextP = driver.find_element_by_xpath('//*[@id="proxylisttable_paginate"]/ul/li[4]/a')
	nextP.click()
	for i in range(1,81):
		https = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[7]').text
		if https == 'yes':
			ip = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[1]').text
			port = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[2]').text
			proxies.append(ip + ':' + port)

	with open('proxies.txt','w') as f:
		for proxy in proxies:
			f.write(proxy + '\n')

def RemoveDupe():
	proxies = []
	with open('first.txt','r') as f:
		for line in f:
			proxies.append(line)

	filtered = list(set(proxies))

	with open('filtered.txt','w') as f:
		for line in filtered:
			f.write(line)

def SortProxies():
	proxies = []
	with open('out_filtered2.txt','r') as f:
		for line in f:
			proxies.append(line.split(':'))

	with open('sorted.txt','a') as f:
		for proxy in sorted(proxies, key=lambda proxy: int(proxy[2].strip())):
			f.write(proxy[0]+':'+proxy[1]+'\n')

def RemoveProxies():
	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	c.execute("DELETE FROM Proxies")
	conn.commit()
	c.close()
	conn.close()

def UploadProxies():
	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	with open('out_filtered2.txt','r') as f:
		for proxy in f:
			entry = proxy.split(':')
			c.execute("INSERT INTO Proxies (ip, port, response, status) VALUES (%s, %s, %s, %s);",(entry[0],entry[1],entry[2].strip(),'Working'))
	conn.commit()
	c.close()
	conn.close()

def RefreshProxyStatus():
	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	c.execute("UPDATE Proxies SET status = 'Working' WHERE status = 'In Use';")	
	conn.commit()
	c.close()
	conn.close()
def ChooseOpt(driver, name):
	options = driver.find_elements_by_name("index")
	if len(options) > 1:
		for option in options:
			optNumber = ParseOptions(option.find_element_by_xpath("../../.").text, name)
			print(optNumber)
	elif len(options) == 1:
		optNumber = ParseOptions(options[0].find_element_by_xpath("../../.").text, name)	
		print(optNumber)
def ParseOptions(label, name):
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
			return int(''.join(filter(lambda x: x.isdigit(), n1)))
def Rename():
	save_dir = "C:\\Users\\Me\\Programs\\collector\\collect\\files"
	os.chdir(save_dir)
	files = filter(os.path.isfile, os.listdir(save_dir))
	files = [os.path.join(save_dir, f) for f in files if f.find('.crdownload') < 0] # add path to each file
	files.sort(key=lambda x: os.path.getmtime(x))
	newest_file = files[-1]
	docName = 'test'
	os.rename(newest_file, docName+".pdf")

def ListProxies():
	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	c.execute("SELECT * FROM Proxies WHERE status = 'Working' ORDER BY response;")
	proxies = c.fetchall()
	c.close()
	conn.close()
	print(proxies)	

def ListActive():
	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	c.execute("SELECT * FROM Montreal WHERE status = 'In Progress'")
	entries = c.fetchall()
	for entry in entries:
		print(entry)
	c.close()
	conn.close()	

def TimeTest():
	timestamp = datetime.now(timezone.utc)
	time.sleep(5)
	diff = int((datetime.now(timezone.utc) - timestamp).total_seconds())
	print(diff)
	print(type(diff))

def DeleteExtras():
	approved = ['(1)','(2)','(3)', '(4)','(5)','(6)','(7)','(8)']
	for file in os.listdir('data/'):
		if any(s in file for s in approved) or ')' not in file:
			continue
		else:
			os.remove('data/' + file)

def TimeTest():

	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	c.execute("UPDATE montreal set last_modified = (%s) where street = '4e Avenue'",(datetime.now(),));
	conn.commit()
	c.execute("SELECT last_modified FROM Montreal WHERE street = '4e Avenue'")
	t = c.fetchone()
	c.close()
	conn.close()
	print(int((datetime.now() - t[0]).total_seconds()))

def Seperate():
	directory = 'files/'
	labels = ['Adresse :','Arrondissement :','Numéro de lot :','Numéro de matricule :','Utilisation prédominante :',"Numéro d'unité de voisinage :",'Numéro de dossier :','Nom :',"Statut aux fins d'imposition scolaire :",'Adresse postale :',"Date d'inscription au rôle :",'Caractéristiques','Mesure frontale :','Superficie :',"Nombre d'étages :",'Année de construction :',"Aire d'étages :",'Genre de construction :','Lien physique :','Nombre de logements :','Nombre de locaux non résidentiels :','Nombre de chambres locatives : ','Rôle courant','Rôle antérieur','Date de référence au marché :','Valeur du terrain',"Valeur de l'immeuble",'Exclusif(s) :','Valeur du bâtiment :',"Conditions particulières d'inscription :"]
	for file in os.listdir(directory):
		with open(directory+file,'r') as f:
			data = f.read()

		for label in labels:
			index = data.find(label)
			if index >= 0:
				data = data[:index]+'\n'+data[index:]
		with open(directory+file,'w') as f:
			f.write(data)


def InsertData():
	directory = 'files/'
	conn = sqlite3.connect("Data.db")
	c = conn.cursor()
	for file in os.listdir(directory):
		with open(directory+file,'r',encoding='utf-8') as f:
			data = f.readlines()
		address = ''
		for line in data:
			info = line.split(' : ')
			try:
				if 'Adresse :' in line:
					address = info[1].strip()
					c.execute('INSERT INTO Present (address) VALUES (?);',(info[1].strip(),))
					conn.commit()
				elif 'Arrondissement :' in line:
					c.execute("UPDATE Present SET borough = (?) WHERE address = (?);",(info[1].strip(), address))
				elif 'Numéro de lot :' in line:
					c.execute("UPDATE Present SET lot_number = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Numéro de matricule :' in line:
					c.execute("UPDATE Present SET registry_number = (?) WHERE address = (?);",( info[1].strip(),address))
				elif 'Utilisation prédominante :' in line:
					c.execute("UPDATE Present SET use = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif "Numéro d'unité de voisinage :" in line:
					c.execute("UPDATE Present SET unit_number = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Numéro de dossier :' in line:
					c.execute("UPDATE Present SET file_number = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Nom :' in line:
					c.execute("SELECT name FROM Present WHERE address = (?);", (address,))
					name = c.fetchone()
					if name[0] is not None:
						c.execute("UPDATE Present SET name = (?) WHERE address = (?);",(name[0]+','+info[1].strip() ,address))
					else:
						c.execute("UPDATE Present SET name = (?) WHERE address = (?);",(info[1].strip() ,address))
						conn.commit()
				elif 'Statut aux fins' in line:
					c.execute("UPDATE Present SET status = (?) WHERE address = (?);",( info[1].strip(),address))
				elif "Date d'inscription" in line:
					c.execute("UPDATE Present SET date_of_entry = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif "Conditions particulières d'inscription :" in line:
					c.execute("UPDATE Present SET special_conditions = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Exclusif(s) :' in line:
					c.execute("UPDATE Present SET lot_number = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Commun(s) :' in line:
					c.execute("UPDATE Present SET lot_number = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Mesure frontale :' in line:
					unit = info[1].find(' m')
					c.execute("UPDATE Present SET front_measure = (?) WHERE address = (?);",(info[1][:unit].strip(),address))
				elif 'Superficie :' in line:
					unit = info[1].find('m2')
					c.execute("UPDATE Present SET land_area = (?) WHERE address = (?);",(info[1][:unit].strip() ,address))
				elif "Aire d'" in line:
					c.execute("UPDATE Present SET floor_area = (?) WHERE address = (?);",(info[1].strip() ,address))
				if "Année de construction :" in line:
					c.execute("UPDATE Present SET construction_year = (?) WHERE address = (?);",( info[2].strip(),address))
				if "Nombre d'étages :" in line:
					c.execute("UPDATE Present SET floors = (?) WHERE address = (?);",(info[2].strip() ,address))
				elif 'Genre de construction :' in line:
					c.execute("UPDATE Present SET construction_type = (?) WHERE address = (?);",( info[1].strip(),address))
				elif 'Lien physique :' in line:
					c.execute("UPDATE Present SET physical_link = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Nombre de locaux non résidentiels :' in line:
					c.execute("UPDATE Present SET nonresidential_premises = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Nombre de logements :' in line:
					c.execute("UPDATE Present SET accomodations = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Nombre de chambres locatives :' in line:
					c.execute("UPDATE Present SET rental_rooms = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Valeur du terrain :' in line:
					unit = info[1].find('$')
					c.execute("UPDATE Present SET land_value = (?) WHERE address = (?);",(info[1][:unit].strip() ,address))
				if "Valeur de l'immeuble au" in line:
					c.execute("UPDATE Present SET prev_property_value = (?) WHERE address = (?);",(info[2].strip() ,address))
				elif "Valeur de l'immeuble :" in line:
					c.execute("UPDATE Present SET property_value = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Valeur du bâtiment :' in line:
					c.execute("UPDATE Present SET building_value = (?) WHERE address = (?);",(info[1].strip(),address))
			except IndexError:
				continue
		conn.commit()
	conn.close()

def UpdateProxyList():
	data = ''
	proxies = []
	with open('python-proxy-checker/output/out_filtered2.txt','r') as f:
		data = f.readlines()
	for line in data:
		ip,port,response = line.split(':')
		proxies.append(ip+':'+port)
	with open('python-proxy-checker/input/first.txt', 'w') as f:
		for proxy in proxies:
			f.write(proxy + '\n')

ListActive()
#Collect proxies
#append to file
=======
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from pdfminer.pdfparser import PDFParser, PDFDocument
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from itertools import chain
import sqlite3
import gc
import sys
from pympler import tracker
import objgraph
import logging
import os
import shutil
from datetime import datetime, timezone
import psycopg2 as pg
import time

def Test():
	chromeOptions = webdriver.ChromeOptions()
	prefs = {"download.prompt_for_download": False, "plugins.always_open_pdf_externally": True}
	chromeOptions.add_experimental_option("prefs",prefs)
	#chromeOptions.add_argument('--proxy-server='+'197.136.142.5:80')
	driver = webdriver.Chrome(chrome_options=chromeOptions)
	driver.get("file:///C:/Users/Me/Programs/collector/collect/IndeOOR.html")
	print(driver.current_window_handle)
	

def ClickDropdown(driver):
	road = 'Avenue'
	name = '1e'
	place = 'Montréal'
	specificPlace = ''
	places = []
	placeOptions = []
	dropdown = driver.find_element_by_xpath('//*[@id="ui-id-1"]')
	for option in dropdown.find_elements_by_tag_name('li'):
		words = option.text.split(' ')
		if road in words and name in words and '('+place+')' in words:
			places.append(option.text)
			placeOptions.append(option)	
			#break
	print(places)
	print(placeOptions)
	if len(specificPlace) > 0:
		if specificPlace in places:
			index = places.index(specificPlace)
			if index >= 0:
				placeOptions[index].click()
			else:
				placeOptions[0].click()
		else:
			placeOptions[0].click()
	else:
		placeOptions[0].click()


def ParseOptions(label):
	index = label.find(' - ')
	if index >= 0:
		index2 = label[index+3:].find(' ')
		n2 = label[index+3:index+3+index2]
		sRange = label[:index+3+index2]
		return (int(n2), sRange.strip())
	else:
		index2 = label.find(' ')
		n1 = label[:index2]
		return (int(n1), n1.strip())
def Ranges(name, place):
	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	c.execute("SELECT * FROM Montreal WHERE street = (%s) and place = (%s);",(name, place))
	entry = c.fetchone()
	if entry:
		street = entry[0]
		place = entry[1]
		c.execute("SELECT l_first, l_last FROM numbers WHERE street = (%s) AND place = (%s)", (street,place))
		left = c.fetchall()
		c.execute("SELECT r_first, r_last FROM numbers WHERE street = (%s) AND place = (%s)", (street,place))
		right = c.fetchall()
		#c.execute("UPDATE Montreal SET status = 'In Progress' WHERE street = (%s) AND place = (%s)", (street,place))
		#conn.commit()
		c.close()
		conn.close()
		leftRange = []
		rightRange = []
		for row in left:
			leftRange.append(tuple(map(int,row)))
		for row in right:
			rightRange.append(tuple(map(int,row)))

		leftN = list(JoinRanges(leftRange))
		rightN = list(JoinRanges(rightRange))
		if leftN[0] == (0,0):
			leftN.remove((0,0))
		if rightN[0] == (0,0):
			rightN.remove((0,0))
	
	print(leftN)
	print(rightN)
def JoinRanges(data, offset=2):
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
def SaveData(driver, number, name, road, place):
	filename = str(number) + '_' + name + '_' + road + '_' + place
	links = driver.find_elements_by_partial_link_text("Compte de taxes")
	for link in links[1:]:
		link.click()
		year = link.text[16:]
		filepath = 'C:\\Users\\Me\\Downloads'
		oldfilename = max([filepath +"\\"+ f for f in os.listdir(filepath)], key=os.path.getctime) 
		shutil.move(os.path.join(filepath,oldfilename),filename+'_'+year+'.pdf')

def pdftotext():
	fp = open('example.pdf', 'rb')
	parser = PDFParser(fp)
	doc = PDFDocument()
	parser.set_document(doc)
	doc.set_parser(parser)
	doc.initialize('')
	rsrcmgr = PDFResourceManager()
	laparams = LAParams()
	device = PDFPageAggregator(rsrcmgr, laparams=laparams)
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	# Process each page contained in the document.
	with open('result.txt','w',errors='ignore') as f:
		for page in doc.get_pages():
			interpreter.process_page(page)
			layout = device.get_result()
			for lt_obj in layout:
				if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
					f.write(lt_obj.get_text())
			break
def LongTest():
	chromeOptions = webdriver.ChromeOptions()
	prefs = {"download.prompt_for_download": False, "plugins.always_open_pdf_externally": True}
	chromeOptions.add_experimental_option("prefs",prefs)
	chrome_options.add_argument('--proxy-server=%s' % '104.236.13.100:8888')
	driver = webdriver.Chrome(chrome_options=chromeOptions)
	driver.get("https://servicesenligne2.ville.montreal.qc.ca/sel/evalweb/index")

def CollectSSLProxies():
	proxies = []
	driver = webdriver.Chrome()
	driver.set_window_size(1800,1000)
	driver.get("https://www.sslproxies.org/")
	opt = Select(driver.find_element_by_xpath('//*[@id="proxylisttable_length"]/label/select'))
	opt.select_by_value('80')
	for i in range(1,81):
		https = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[7]').text
		if https == 'yes':
			ip = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[1]').text
			port = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[2]').text
			proxies.append(ip + ':' + port)
	nextP = driver.find_element_by_xpath('//*[@id="proxylisttable_paginate"]/ul/li[4]/a')
	nextP.click()
	for i in range(1,81):
		try:
			https = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[7]').text
		except NoSuchElementException:
			break
		if https == 'yes':
			ip = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[1]').text
			port = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[2]').text
			proxies.append(ip + ':' + port)

	with open('proxies.txt','w') as f:
		for proxy in proxies:
			f.write(proxy + '\n')	
def CollectUSProxies():
	proxies = []
	driver = webdriver.Chrome()
	driver.set_window_size(1800,1000)
	driver.get("https://www.us-proxy.org/")
	opt = Select(driver.find_element_by_xpath('//*[@id="proxylisttable_length"]/label/select'))
	opt.select_by_value('80')
	for i in range(1,81):
		https = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[7]').text
		if https == 'yes':
			ip = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[1]').text
			port = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[2]').text
			proxies.append(ip + ':' + port)
	nextP = driver.find_element_by_xpath('//*[@id="proxylisttable_paginate"]/ul/li[4]/a')
	nextP.click()
	for i in range(1,81):
		https = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[7]').text
		if https == 'yes':
			ip = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[1]').text
			port = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody/tr['+str(i)+']/td[2]').text
			proxies.append(ip + ':' + port)

	with open('proxies.txt','w') as f:
		for proxy in proxies:
			f.write(proxy + '\n')

def RemoveDupe():
	proxies = []
	with open('first.txt','r') as f:
		for line in f:
			proxies.append(line)

	filtered = list(set(proxies))

	with open('filtered.txt','w') as f:
		for line in filtered:
			f.write(line)

def SortProxies():
	proxies = []
	with open('out_filtered2.txt','r') as f:
		for line in f:
			proxies.append(line.split(':'))

	with open('sorted.txt','a') as f:
		for proxy in sorted(proxies, key=lambda proxy: int(proxy[2].strip())):
			f.write(proxy[0]+':'+proxy[1]+'\n')

def RemoveProxies():
	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	c.execute("DELETE FROM Proxies")
	conn.commit()
	c.close()
	conn.close()

def UploadProxies():
	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	with open('out_filtered2.txt','r') as f:
		for proxy in f:
			entry = proxy.split(':')
			c.execute("INSERT INTO Proxies (ip, port, response, status) VALUES (%s, %s, %s, %s);",(entry[0],entry[1],entry[2].strip(),'Working'))
	conn.commit()
	c.close()
	conn.close()

def RefreshProxyStatus():
	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	c.execute("UPDATE Proxies SET status = 'Working' WHERE status = 'In Use';")	
	conn.commit()
	c.close()
	conn.close()
def ChooseOpt(driver, name):
	options = driver.find_elements_by_name("index")
	if len(options) > 1:
		for option in options:
			optNumber = ParseOptions(option.find_element_by_xpath("../../.").text, name)
			print(optNumber)
	elif len(options) == 1:
		optNumber = ParseOptions(options[0].find_element_by_xpath("../../.").text, name)	
		print(optNumber)
def ParseOptions(label, name):
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
			return int(''.join(filter(lambda x: x.isdigit(), n1)))
def Rename():
	save_dir = "C:\\Users\\Me\\Programs\\collector\\collect\\files"
	os.chdir(save_dir)
	files = filter(os.path.isfile, os.listdir(save_dir))
	files = [os.path.join(save_dir, f) for f in files if f.find('.crdownload') < 0] # add path to each file
	files.sort(key=lambda x: os.path.getmtime(x))
	newest_file = files[-1]
	docName = 'test'
	os.rename(newest_file, docName+".pdf")

def ListProxies():
	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	c.execute("SELECT * FROM Proxies WHERE status = 'Working' ORDER BY response;")
	proxies = c.fetchall()
	c.close()
	conn.close()
	print(proxies)	

def ListActive():
	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	c.execute("SELECT * FROM Montreal WHERE status = 'In Progress'")
	entries = c.fetchall()
	for entry in entries:
		print(entry)
	c.close()
	conn.close()	

def TimeTest():
	timestamp = datetime.now(timezone.utc)
	time.sleep(5)
	diff = int((datetime.now(timezone.utc) - timestamp).total_seconds())
	print(diff)
	print(type(diff))

def DeleteExtras():
	approved = ['(1)','(2)','(3)', '(4)','(5)','(6)','(7)','(8)']
	for file in os.listdir('data/'):
		if any(s in file for s in approved) or ')' not in file:
			continue
		else:
			os.remove('data/' + file)

def TimeTest():

	conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
	c = conn.cursor()
	c.execute("UPDATE montreal set last_modified = (%s) where street = '4e Avenue'",(datetime.now(),));
	conn.commit()
	c.execute("SELECT last_modified FROM Montreal WHERE street = '4e Avenue'")
	t = c.fetchone()
	c.close()
	conn.close()
	print(int((datetime.now() - t[0]).total_seconds()))

def Seperate():
	directory = 'files/'
	labels = ['Adresse :','Arrondissement :','Numéro de lot :','Numéro de matricule :','Utilisation prédominante :',"Numéro d'unité de voisinage :",'Numéro de dossier :','Nom :',"Statut aux fins d'imposition scolaire :",'Adresse postale :',"Date d'inscription au rôle :",'Caractéristiques','Mesure frontale :','Superficie :',"Nombre d'étages :",'Année de construction :',"Aire d'étages :",'Genre de construction :','Lien physique :','Nombre de logements :','Nombre de locaux non résidentiels :','Nombre de chambres locatives : ','Rôle courant','Rôle antérieur','Date de référence au marché :','Valeur du terrain',"Valeur de l'immeuble",'Exclusif(s) :','Valeur du bâtiment :',"Conditions particulières d'inscription :"]
	for file in os.listdir(directory):
		with open(directory+file,'r') as f:
			data = f.read()

		for label in labels:
			index = data.find(label)
			if index >= 0:
				data = data[:index]+'\n'+data[index:]
		with open(directory+file,'w') as f:
			f.write(data)


def InsertData():
	directory = 'files/'
	conn = sqlite3.connect("Data.db")
	c = conn.cursor()
	for file in os.listdir(directory):
		with open(directory+file,'r',encoding='utf-8') as f:
			data = f.readlines()
		address = ''
		for line in data:
			info = line.split(' : ')
			try:
				if 'Adresse :' in line:
					address = info[1].strip()
					c.execute('INSERT INTO Present (address) VALUES (?);',(info[1].strip(),))
					conn.commit()
				elif 'Arrondissement :' in line:
					c.execute("UPDATE Present SET borough = (?) WHERE address = (?);",(info[1].strip(), address))
				elif 'Numéro de lot :' in line:
					c.execute("UPDATE Present SET lot_number = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Numéro de matricule :' in line:
					c.execute("UPDATE Present SET registry_number = (?) WHERE address = (?);",( info[1].strip(),address))
				elif 'Utilisation prédominante :' in line:
					c.execute("UPDATE Present SET use = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif "Numéro d'unité de voisinage :" in line:
					c.execute("UPDATE Present SET unit_number = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Numéro de dossier :' in line:
					c.execute("UPDATE Present SET file_number = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Nom :' in line:
					c.execute("SELECT name FROM Present WHERE address = (?);", (address,))
					name = c.fetchone()
					if name[0] is not None:
						c.execute("UPDATE Present SET name = (?) WHERE address = (?);",(name[0]+','+info[1].strip() ,address))
					else:
						c.execute("UPDATE Present SET name = (?) WHERE address = (?);",(info[1].strip() ,address))
						conn.commit()
				elif 'Statut aux fins' in line:
					c.execute("UPDATE Present SET status = (?) WHERE address = (?);",( info[1].strip(),address))
				elif "Date d'inscription" in line:
					c.execute("UPDATE Present SET date_of_entry = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif "Conditions particulières d'inscription :" in line:
					c.execute("UPDATE Present SET special_conditions = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Exclusif(s) :' in line:
					c.execute("UPDATE Present SET lot_number = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Commun(s) :' in line:
					c.execute("UPDATE Present SET lot_number = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Mesure frontale :' in line:
					unit = info[1].find(' m')
					c.execute("UPDATE Present SET front_measure = (?) WHERE address = (?);",(info[1][:unit].strip(),address))
				elif 'Superficie :' in line:
					unit = info[1].find('m2')
					c.execute("UPDATE Present SET land_area = (?) WHERE address = (?);",(info[1][:unit].strip() ,address))
				elif "Aire d'" in line:
					c.execute("UPDATE Present SET floor_area = (?) WHERE address = (?);",(info[1].strip() ,address))
				if "Année de construction :" in line:
					c.execute("UPDATE Present SET construction_year = (?) WHERE address = (?);",( info[2].strip(),address))
				if "Nombre d'étages :" in line:
					c.execute("UPDATE Present SET floors = (?) WHERE address = (?);",(info[2].strip() ,address))
				elif 'Genre de construction :' in line:
					c.execute("UPDATE Present SET construction_type = (?) WHERE address = (?);",( info[1].strip(),address))
				elif 'Lien physique :' in line:
					c.execute("UPDATE Present SET physical_link = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Nombre de locaux non résidentiels :' in line:
					c.execute("UPDATE Present SET nonresidential_premises = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Nombre de logements :' in line:
					c.execute("UPDATE Present SET accomodations = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Nombre de chambres locatives :' in line:
					c.execute("UPDATE Present SET rental_rooms = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Valeur du terrain :' in line:
					unit = info[1].find('$')
					c.execute("UPDATE Present SET land_value = (?) WHERE address = (?);",(info[1][:unit].strip() ,address))
				if "Valeur de l'immeuble au" in line:
					c.execute("UPDATE Present SET prev_property_value = (?) WHERE address = (?);",(info[2].strip() ,address))
				elif "Valeur de l'immeuble :" in line:
					c.execute("UPDATE Present SET property_value = (?) WHERE address = (?);",(info[1].strip() ,address))
				elif 'Valeur du bâtiment :' in line:
					c.execute("UPDATE Present SET building_value = (?) WHERE address = (?);",(info[1].strip(),address))
			except IndexError:
				continue
		conn.commit()
	conn.close()

def UpdateProxyList():
	data = ''
	proxies = []
	with open('python-proxy-checker/output/out_filtered2.txt','r') as f:
		data = f.readlines()
	for line in data:
		ip,port,response = line.split(':')
		proxies.append(ip+':'+port)
	with open('python-proxy-checker/input/first.txt', 'w') as f:
		for proxy in proxies:
			f.write(proxy + '\n')

ListActive()
#Collect proxies
#append to file
>>>>>>> eed5e0215f7721bfb7fe0d5ec5ae90105c9b2f4b
