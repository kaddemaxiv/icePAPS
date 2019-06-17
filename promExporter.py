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
		self.use_ip = self.ip.replace('-','_')
		print 'ip: ' + self.ip
		print 'use_ip: ' + self.use_ip
		self.ice = IceParser(self.ip)
 


	# Processes the temperature of the IcePAPs on the rack
	# with adress 'ip'. 
	def setup_temperature_gauge(self):
 		temp_gauge = []

		for card in self.ice.getCardsAlive():
			card = str(card)
			print self.use_ip +  '_icepap_' + card
			temp_gauge.append(Gauge(self.use_ip +  '_icepap_' + card + '_temperature' , 'Temperature of the IcePAP'))
	
		return temp_gauge

	def request_icepap_temperature(self, temp_guages):
		temps = []
		temps = self.ice.getCardTemps()
		for i in range(len(temp_guages)):
				temp_guages[i].set(temps[i])

	


def main():
	ex = promExporter('w-kitslab-icepap-11')
	temp_gauges = ex.setup_temperature_gauge()
	start_http_server(6122)
	while True:
		try:
			ex.request_icepap_temperature(temp_gauges)
		except KeyboardInterrupt:
			print "\nClosing"
			sys.exit(0)



if __name__ == '__main__':
	main()


	
	 
