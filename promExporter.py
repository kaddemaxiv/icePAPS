from prometheus_client import start_http_server, Gauge
from IceParser import *
import time
import sys 
import random 

class promExporter:

	# Creates an IceParser object that can
	# read data from IcePAPs at adress 'ip'
	def __init__(self, ip):
		self.ip = str(ip)
		self.temp_gauges = []
		self.use_ip = self.ip.replace('-','_')
		self.ice = IceParser(self.ip)

 


	# Sets up a list of temperature gauges which will later be
	# dynamically set.
	def setup_temperature_gauge(self):
		for card in self.ice.getCardsAlive():
			card = str(card)
			self.temp_gauges.append(Gauge(self.use_ip +  '_icepap_' + card + '_temperature' , 'Temperature of the IcePAP'))
	
		
	# 
	def request_icepap_temperature(self):
		temps = []
		temps = self.ice.getCardTemps()
		for i in range(len(self.temp_gauges)):
				self.temp_gauges[i].set(temps[i])

	


def main():
	ips = [
'w-kitslab-icepap-0',
'w-kitslab-icepap-10',
'w-kitslab-icepap-19',
'w-maglab-icepap-0',
'w-v-kitslab-icepap-ec-0',
'w-kitslab-icepap-20',
'w-kitslab-icepap-16',
'w-v-kitslab-icepap-cc-0',
'w-kitslab-icepap-17',
'w-kitslab-icepap-18',
'w-kitslab-icepap-47',
'w-kitslab-icepap-11',
'w-kitslab-icepap-12',
'w-kitslab-icepap-83',
'w-icepap-pc-0',
'w-kitslab-icepap-14',
'w-kitslab-icepap-15'
	]
	exporters = []
	alive = []
	for i in range(len(ips)):
		exporters.append(promExporter(ips[i]))
		if exporters[i].ice.isAlive():
			alive.append(ips[i])
		exporters[i].setup_temperature_gauge()
	#start_http_server(6122)
	for ip in alive:
		print ip + ' is alive'
	while True:
		try:
			for exporter in exporters:
				exporter.request_icepap_temperature()
		except KeyboardInterrupt:
			print "\nClosing"
			sys.exit(0)




if __name__ == '__main__':
	main()


	
	 
