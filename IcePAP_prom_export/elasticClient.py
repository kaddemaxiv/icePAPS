from elasticsearch import Elasticsearch
import time
from IceParser import *

class elasticClient:


	"""
	Creates a connection to an Elasticsearch server located
	at localhost:9200. We will later collect data from this
	port and pass it to a monitoring UI.
	"""
	__init__(self, ip):
		self.ip = str(ip)
		self.ice = IceParser(adress)


	"""
	Updates all information of all cards in the locker at
	adress 'ip' stores it on the Elasticsearch server at:
	<ip>/_doc/<icepap_nr>

	"""
	def update_cards(self):
		self.ice.




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

	#es = Elasticsearch(['localhost:9200'])
	
if __name__=='__main__':
	main()





