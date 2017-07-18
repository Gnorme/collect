from selenium import webdriver
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



ListActive()
#Collect proxies
#append to file
