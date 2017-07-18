import psycopg2 as pg
from pyvirtualdisplay import Display
from datetime import datetime, timezone
from collect import Collector
import multiprocessing
import time
import sys


class Processor(multiprocessing.Process):
	def __init__(self, name, counter, useProxy):
		multiprocessing.Process.__init__(self)
		self.running = False
		self.processID = counter
		self.name = str(name)
		self.test = False
		self.c = Collector()
		self.c.setup(name, useProxy=useProxy)
	def run(self):
		self.running = True
		while self.running:
			addresses = self.c.NextStreet()
			if addresses["LastNum"] is not None:
				if addresses["LastSide"] == "Left":
					self.c.CollectSide("Left", addresses, int(addresses["LastNum"]) + 2)
					if len(addresses["Right"]) > 0:
						self.c.CollectSide("Right", addresses, addresses["Right"][0][0])
				if addresses["LastSide"] == "Right":
					self.c.CollectSide("Right", addresses, int(addresses["LastNum"]) + 2)
			else:
				if len(addresses["Left"]) > 0:
					self.c.CollectSide("Left", addresses, addresses["Left"][0][0])
				if len(addresses["Right"]) > 0:
					self.c.CollectSide("Right", addresses, addresses["Right"][0][0])
			self.c.UpdateStatus("Done", addresses["Street"], addresses["Place"])

		print ("Exiting %s - Last address was %s %s %s %s" % (self.name, number, name, road, place))
		self.c.Close()

def TimeSinceActive(process):
	connected = False
	while not connected:
		try:
			conn = pg.connect(dbname='Addresses', host='east-post1.cb9zvudjieab.us-east-2.rds.amazonaws.com', port=5432, user='gnorme', password='superhairydick1')
			connected = True
		except pg.OperationalError:
			print("DB connect failed")
			logging.info("DB Connect failed")
			time.sleep(120)
	c = conn.cursor()
	c.execute("SELECT * FROM Montreal WHERE status = 'In Progress' AND claimed_by = (%s);",(str(process),))
	entry = c.fetchone()
	if entry:
		if entry[5] is not None:
			timestamp = entry[5]
		else:
			return 0
		diff = int((datetime.now() - timestamp).total_seconds())
		return diff
	else:
		return 0	

if __name__ == '__main__':
	display = Display(visible=0,size=(1080,1000))
	display.start()
	names = []
	instances = int(sys.argv[2])
	if sys.argv[1] == 'True':
		useProxy = True
	elif sys.argv[1] == 'False':
		useProxy = False
	for n in range(3,instances+3):
		names.append(sys.argv[n])
	processes = {}
	for i in range(0, instances):
		try:
			process = Processor(names[i], len(processes) +1,useProxy)
			processes[i] = process
			processes[i].start()
		except Exception as e:
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
	while True:
		time.sleep(300)
		for i in range(0, instances):
			if TimeSinceActive(processes[i].name) > 600:
				process = Processor(names[i], len(processes) +1,useProxy)
				processes[i] = process
				processes[i].start()			


#List of thread names
#Check db for streets claimed by thread and not done
#If time since last_modified is > x, restart thread

#get proxy
#start thread
#get 10 tax assess
#repeat
