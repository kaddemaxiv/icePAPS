from elasticsearch import Elasticsearch
import MySQLdb as db
import socket
import time
import sys
from IceParser import *
from datetime import datetime, timedelta

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

		icepap_info/_doc/<hostname>_<cardNbr>
		
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
			json_body.update({'alarm':alarm_list[i],'status':status_list[i], 'card':cards[i], 'warning':warning_list[i],'update':timestampStr, 'hostname':self.ip})
			server.index(index='icepap_info', id=self.ip + '_' + str(cards[i]), body=json_body)
		

	
	def update_status(self, server):
		"""
		Updates the status, alarm status and warnings of all 
		cards in a locker at adress 'ip'. Changes are made 
		to the Elasticsearch doc at

		icepap_info/_doc/<hostname>_<cardNbr>

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
			json_body = {'alarm':alarm_list[i], 'status':status_list[i], 'warning':warning_list[i], 'update':timestampStr, 'hostname':self.ip}
			server.update(index='icepap_info', id=self.ip + '_' + str(cards[i]), body={"doc":json_body})


def get_icepapcms_host(cabledb):
	"""
	Returns a list of all IcePAP hostnames in the network
	"""
	connector = db.connect(cabledb,  "icepapcms","icepapcms", "icepapcms", port=3306)
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


def restart_index(ips, server):
	"""
	Used to initiate, but mostly restart the index after a
	given time period
	"""
	icepaps = []

#CREATING ICEPAP PARSERS FOR EVERY ADRESS IN ips
	for ip in ips:
		icepaps.append(ElasticClient(ip))
	
	for icepap in icepaps:
		icepap.setup_cards(server)

	print "- - - - - " + datetime.now().strftime("%d-%b-%Y (%H:%M:%S)") + " - - - - -"
	return icepaps


def main():
	cabledb = sys.argv[1]

	ips = get_icepapcms_host(cabledb)
	server = Elasticsearch(['localhost:9200'])
	icepaps = restart_index(ips, server)


	#Runs script indefinetly
	update_time = datetime.now() + timedelta(minutes=15)

	while True:
		try:
			time.sleep(10)
			for icepap in icepaps:
				icepap.update_status(server)

			if update_time < datetime.now():
				ips = get_icepapcms_host(cabledb)
				server.indices.delete(index='icepap_info', ignore=[400, 404])
				icepaps = restart_index(ips,server)
				update_time = datetime.now() + timedelta(minutes=15)
		except KeyboardInterrupt:
			print '\nClosing'
			sys.exit(0)
	

if __name__=='__main__':
	main()





