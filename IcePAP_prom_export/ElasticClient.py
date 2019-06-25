from elasticsearch import Elasticsearch
import time
import sys
from IceParser import *

class ElasticClient:


	"""
	Creates a connection to a IcePAP locker with adress 'ip'
	"""
	def __init__(self, ip):
		self.ip = str(ip)
		self.ice = IceParser(self.ip)
		self.versions_list = []
		self.alarm_list = []
		self.status_list = []

	"""
	Sets up all information of all cards in the locker at
	adress 'ip' and stores it on the Elasticsearch server at:

	<ip>/_doc/<icepap_nr>
	
	Takes a fair bit of time, and should thus only be run
	at start up and on very special occasions.
	"""
	def setup_cards(self, server):
		versions_list = self.ice.getVersionsList()
		alarm_list = self.ice.getAlarmStatus()
		status_list = self.ice.getStatus()
		cards = self.ice.getCardsAlive()
		for i in range(len(versions_list)):
			json_body = versions_list[i]
			json_body.update({'alarm':alarm_list[i],'status':status_list[i], 'card':cards[i]})
			server.index(index=self.ip, id=cards[i], body=json_body)
		

	"""
	Updates the status and alarm status of all cards in a
	locker at adress 'ip'. Changes are made to the doc at

	<ip>/_doc/icepap_nr

	This method is much faster than setup_cards() since we
	don't have to extract the version data. 

	"""
	def update_status(self, server):
		# The ip is the index of the different 
		cards = self.ice.getCardsAlive()
		alarm_list = self.ice.getAlarmStatus()
		status_list = self.ice.getStatus()
	
		for i in range(len(cards)):
			json_body = {'alarm':alarm_list[i], 'status':status_list[i]}
			server.update(index=self.ip, id=cards[i], body={"doc":json_body})



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

#CREATING ICEPAP PARSERS FOR EVERY ADRESS IN ips
	for ip in ips:
		parsers.append(ElasticClient(ip))
	
	# Actually works!!!
	
	server = Elasticsearch(['localhost:9200'])
	for parser in parsers:
		parser.setup_cards(server)
		print parser.ip + " done"
	"""
	parsers[11].setup_cards(server)
	print server.get(index='w-kitslab-icepap-11', id=0)['_source']
	"""
	#Start connection to server:
	#es = Elasticsearch(['localhost:9200'])

	#Runs script indefinetly
	print "Done"
	while True:
		try:
			
			#for parser in parsers:
			#	parser.update_status(server)
			#	print parser.ip + ' done'
			res = server.search(index='w-kitslab-icepap-12', body={"query":{"match_all":{}}})
			print res
			print "All done"
			time.sleep(150)
		except KeyboardInterrupt:
			server.delete()
			print '\nClosing'
			sys.exit(0)



if __name__=='__main__':
	main()





