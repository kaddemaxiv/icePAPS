from prometheus_client import start_http_server, Gauge
from IceParser import *
import MySQLdb as db
import socket
import time
import sys
import random

class newExp:


	def __init__(self, ip, temp_gauge, version_gauge, status_gauge):
		"""
		Creates an IceParser instance that can read data from IcePAP drivers
		at adress 'ip'
		"""
		self.ip = str(ip)
		self.ice = IceParser(self.ip)
		self.temp_gauge = temp_gauge
		self.version_gauge = version_gauge
		self.status_gauge = status_gauge



	def request_icepap_temperature(self):
		"""
		Requests the temperature of all IcePAPs and their power
		supplies on the ip given in the constructor by updating
		the gauge to the current temperarue of all the cards
		"""
		icepap_temps = self.ice.getCardTemps()
		icepaps_alive = self.ice.getCardsAlive()
		for card_temp, card in zip(icepap_temps, icepaps_alive):
			self.temp_gauge.labels(self.ip, card).set(card_temp)

		supply_temps = self.ice.getSupplyTemps()
		racks_alive = self.ice.myice.getRacksAlive()
		for supply_temp, rack in zip(supply_temps, racks_alive):
			self.temp_gauge.labels(self.ip, 'supply_' + str(rack)).set(supply_temp)

	def request_icepap_status(self):

		alarm_list = self.ice.getAlarmStatus()
		status_list = self.ice.getStatus()
		cards = self.ice.getCardsAlive()

		for i in range(len(status_list)):
			self.status_gauge.labels(self.ip, cards[i], status_list[i], alarm_list[i]).set(0)

	
	def request_icepap_versions(self):
		versions_list = self.ice.getVersionsList()
		


def get_icepapcms_host():
	"""
	Returns a list of all IcePAP hostnames in the network
	"""
	connector = db.connect("w-v-kitslab-csdb-0",  "icepapcms","icepapcms", "icepapcms", port=3306)
	cursor = connector.cursor()
	sql_query = "SELECT host FROM icepapsystem;"
	size = cursor.execute(sql_query)
	output = cursor.fetchall()
	ips = []
	for ip in [a[0] for a in output]:
		try:
			ips.append(socket.gethostbyaddr(ip)[0].split(".")[0])
		except socket.herror:
			print("Fail to resolve dns name {}".format(ip))
		except socket.gaierror:
			print("Fail to resolve dns name {}".format(ip))
	return ips


def main():
	ips = get_icepapcms_host()

	print "Create exporters"

	temp_gauge = Gauge('icepap_temperature', 'Temperature of the IcePAP', ('host', 'card'))

	version_gauge = Gauge('loops_since_last_version_update', 'The number of loops since a ' + 
		'version update query was last executed',
		('host', 'card','CONTROLLER','DRIVER','DSP','FPGA','MCPU0', 'MCPU1','MCPU2'))

	status_gauge = Gauge('loops_since_last_status_update','The number of loops since a ' + 
		'status update query was last executed', ('host', 'card','STATUS','ALARM'))
	
	exporters = []

	test_gauge = Gauge('test_gauge', 'testing visibility',('host', 'card', 'message'))

	for ip in ips:
		exporters.append(newExp(ip, temp_gauge, version_gauge, status_gauge))

	print "Start serving"
	start_http_server(6122)
	count = 0
	while True:
		try:
			if count < 5:
				test_gauge.labels('someip', 'card0', 'none').set(count)
			else:
				test_gauge.labels('someip', 'card0', 'some message').set(9)
			print "Requesting IcePAP temperatures"
			for exporter in exporters:
				exporter.request_icepap_temperature()
			time.sleep(10)
			count += 1
			


		except KeyboardInterrupt:
			print "\nClosing"
			sys.exit(0)
	

if __name__=="__main__":
	main()


