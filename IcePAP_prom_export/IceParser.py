from pyIcePAP import *
import time
import re


"""
This program contains a class which can be called to extract
different series of data from IcePAP drivers and controllers
at a given ip in the white system.
"""
class IceParser:
	
	def __init__(self, ip):
		"""
		Creates an object which will read data from the IcePAPs
		at the adress 'ip'
		NOTE that connecting to the icePAP takes time, thus a 
		time.sleep()-call is added in the initiation.
		"""
		self.myice = EthIcePAP(ip, 5000)
		time.sleep(0.01)
		# self.totaldrivers = 0	
	

	def getCardTemps(self):
		"""
		Returns a list of ints representing the current temperature
		of all cards in the closet. To see which driver corresponds 
		to which temperature use getCardsAlive().
		"""
		drivertemp = []
		for driver in self.myice.getDriversAlive():
			input = int(self.myice.getMeas(driver,'T'))
			drivertemp.append(input)	
		for i in self.myice.getRacksAlive():
			input = int(self.myice.getMeas(i*10, 'T'))
			drivertemp.append(input)

		return drivertemp


	
	def getSupplyTemps(self):
		"""
		Returns a list of ints representingcthe temperature of the 
		power supplies in the various controllers in the closet	
		"""
		supplytemp = []
		for controller in self.myice.getRacksAlive():
			input = str(controller*10)
			string = self.myice.sendWriteReadCommand(input + ':?MEAS RT')
			split = string.split(' ')
			ret_int = int(split[1])
			supplytemp.append(ret_int)
		return supplytemp	


	
	def getVersionsList(self): 
		"""
		Returns a list of dicts representing the current versions
		of all cards in the closet.The versions of interest
		are:

		'CONTROLLER'
		'DRIVERS'
		'DPS'
		'FPGA'
		'MCPU0' |
		'MCPU1' | <-- Only for masters
		'MCPU2' |

		"""
		version_list = []
		for card in self.getCardsAlive():
			version_list.append(self.myice.getVersionInfoDict(card))
		return version_list

	
	def getCardsAlive(self):
		"""
		Returns a list containing all the drivers and controllers
		which are currently alive on the format:
			
			[1, 2, 3, 4, ..., 27, 0, 10, 20]
			^all active drivers^  	^ all active controllers 

		"""
		alive_drivers = []
		for driver in self.myice.getDriversAlive():
			alive_drivers.append(driver)

		for controller in self.myice.getRacksAlive():
			alive_drivers.append(controller*10)
		
		return alive_drivers

	
	
	def getStatus(self):
		"""	
		Returns a list containing the status of the
		IcePAPs in the closet. If there is no driver in
		a certain card slot the status is represented
		with the value 'EMPTY'.
		"""
		status_list = []

		for card in self.getCardsAlive():
			input = str(card)
			string = self.myice.sendWriteReadCommand(input + ':?MODE')
			split = string.split(' ')
			status_list.append(split[1])
		return status_list



	
	def getAlarmStatus(self):
		"""
		Returns a list containing the alarm status of the
		IcePAPs in the closet. If there is no driver in
		a certain card slot the status is represented
		with the value 'EMPTY'.	
		"""
		alarmstatus_list = []

		for card in self.getCardsAlive():
			input = str(card)
			string = self.myice.sendWriteReadCommand(input + ':?ALARM')
			split = string.split(' ')
			alarmstatus_list.append(split[1])
		return alarmstatus_list

	
	def isAlive(self):
		"""
		Checks if there are any racks alive on the adress
		"""	
		return len(self.myice.getRacksAlive()) > 0

		
	

def main():
	paps = [
	IceParser('w-kitslab-icepap-10'),
	IceParser('w-kitslab-icepap-11'),
	IceParser('w-kitslab-icepap-12')
	]
	
	status_list = paps[0].getStatus()

	time.sleep(0.01)
	for pap in paps:
		cards_alive = pap.getCardsAlive()
		status_list = pap.getStatus()
		print(cards_alive)
		print(status_list)



if __name__ == "__main__":
	main()
