from prometheus_client import start_http_server, Gauge
from IceParser import *
import time
import sys 
import random 

class promExporter:
	"""
	Creates an IceParser instance that can read data from IcePAP drivers
	at adress 'ip'
	"""
	def __init__(self, ip):
		self.ip = str(ip)
		self.icepap_temp_gauges = []
		self.supply_temp_gauges = []
		self.use_ip = self.ip.replace('-','_')
		self.ice = IceParser(self.ip)

 

	"""	
	Sets up a list of temperature gauges which will later be
	dynamically updated. The gauges represent the controllers
	/drivers at card slot 'k' in the closet with metric name 
	format:
	
	<ip>_icepap_<k>_temperature

	"""
	def setup_icepap_temperature_gauge(self):
		for card in self.ice.getCardsAlive():
			card = str(card)
			curr = Gauge(self.use_ip +  '_icepap_' + card + '_temperature' , 'Temperature of the IcePAP')
			self.icepap_temp_gauges.append(curr)
		
	"""
	Sets up a list of temperature gauges which will later be
	dynamically updated. The gauges represent the power supply
	at controller slot 'k' in the closet with metric name
	format:

	<ip>_supply_<k>_temperature

	"""
	def setup_supply_temperature_gauge(self):
		for controller in self.ice.myice.getRacksAlive():
			controller = str(controller)
			curr = Gauge(self.use_ip + '_supply_' + controller + '_temperature', 'Temperature of the power supply')
			self.supply_temp_gauges.append(curr)
		
	"""
	Requests the temperature of all IcePAPs on the ip given in the constructor
	"""
	def request_icepap_temperature(self):
		icepap_temps = []
		icepap_temps = self.ice.getCardTemps()
		for i in range(len(self.icepap_temp_gauges)):
			self.icepap_temp_gauges[i].set(icepap_temps[i])


	def request_supply_temperature(self):
		supply_temps = []
		supply_temps = self.ice.getSupplyTemps()
		for k in range(len(self.supply_temp_gauges)):	
			self.supply_temp_gauges[k].set(supply_temps[k])

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
	parsers = []
	
	alive = []
	# CREATING ICEPAP GAUGES
	for i in range(len(ips)):
		parsers.append(promExporter(ips[i]))
		#if	parsers[i].ice.isAlive():
		#	alive.append(ips[i])
		parsers[i].setup_icepap_temperature_gauge()
		parsers[i].setup_supply_temperature_gauge()
	#print alive
	start_http_server(6122)
	while True:
		try:
			for exporter in	parsers:
				exporter.request_icepap_temperature()
				exporter.request_supply_temperature()
		except KeyboardInterrupt:
			print "\nClosing"
			sys.exit(0)




if __name__ == '__main__':
	main()


	
	 
