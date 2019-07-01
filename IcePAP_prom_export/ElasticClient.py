from elasticsearch import Elasticsearch
import MySQLdb as db
import socket
import time
import sys
from IceParser import *
from datetime import datetime

class ElasticClient:


	def __init__(self, ip):
		"""
		Creates a connection to a IcePAP locker with adress 'ip'
		"""
		self.ip = str(ip)
		self.ice = IceParser(self.ip)
		self.versions_list = []
		self.alarm_list = []
		self.status_list = []


	def setup_cards(self, server):
		"""
		Sets up all information of all cards in the locker at
		adress 'ip' and stores it on the Elasticsearch server at:

		<ip>/_doc/<icepap_nr>
		
		Takes a fair bit of time, and should thus only be run
		at start up and on very special occasions.
		"""
		versions_list = self.ice.getVersionsList()
		alarm_list = self.ice.getAlarmStatus()
		status_list = self.ice.getStatus()
		warning_list = self.ice.getWarnings()

		dateTimeObj = datetime.now()
		timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
		cards = self.ice.getCardsAlive()
		for i in range(len(versions_list)):
			json_body = versions_list[i]
			
			json_body.update({'alarm':alarm_list[i],'status':status_list[i], 'card':cards[i], 'warning':warning_list[i],'update':timestampStr})
			server.index(index=self.ip, id=cards[i], body=json_body)
		

	
	def update_status(self, server):
		"""
		Updates the status and alarm status of all cards in a
		locker at adress 'ip'. Changes are made to the doc at

		<ip>/_doc/icepap_nr

		This method is much faster than setup_cards() since we
		don't have to extract the version data. 

		"""
		cards = self.ice.getCardsAlive()
		alarm_list = self.ice.getAlarmStatus()
		status_list = self.ice.getStatus()
		warning_list = self.ice.getWarnings()

		dateTimeObj = datetime.now()
		timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
		for i in range(len(cards)):
			json_body = {'alarm':alarm_list[i], 'status':status_list[i], 'warning':warning_list[i], 'update':timestampStr}
			server.update(index=self.ip, id=cards[i], body={"doc":json_body})


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
	"""[
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
		]"""

	icepaps = []

#CREATING ICEPAP PARSERS FOR EVERY ADRESS IN ips
	for ip in ips:
		icepaps.append(ElasticClient(ip))
	
	# Actually works!!!
	
	server = Elasticsearch(['localhost:9200'])
	for icepap in icepaps:
		icepap.setup_cards(server)
		print icepap.ip + " done"

	server.index(index='test', id=21, body={"change":1})
	"""
	parsers[11].setup_cards(server)
	print server.get(index='w-kitslab-icepap-11', id=0)['_source']
	"""
	#Start connection to server:
	#es = Elasticsearch(['localhost:9200'])

	#Runs script indefinetly
	print "All done"
	while True:
		try:
			time.sleep(5)
			count = 1
			for icepap in icepaps:
				icepap.update_status(server)
				print icepap.ip + ' updated'
				count += 1
				server.index(index='test', id=21, body={"change":count})
		except KeyboardInterrupt:
			print '\nClosing'
			sys.exit(0)



if __name__=='__main__':
	main()





