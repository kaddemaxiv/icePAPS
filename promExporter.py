from prometheus_client import start_http_server, Gauge
from IceParser import *
import time

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
			temp_gauge.append(Gauge(self.use_ip +  '_icepap_' + card, 'Temperature of the IcePAP'))
	
		return temp_gauge
	


def main():
	ex = promExporter('w-kitslab-icepap-11')
	temp_gauges = ex.setup_temperature_gauge()
	print "Here"
	#start_http_server(6122)
	while True:
		temp_list = ex.ice.getCardTemps()
		print temp_list)
		print len(temp_gauges)
		for card in ex.ice.getCardsAlive():
			temp_gauges[card].set(temp_list[card])


if __name__ == '__main__':
	main()


	
	 
