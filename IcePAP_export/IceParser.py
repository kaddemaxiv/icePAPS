from pyIcePAP import *
import time
import re


"""
This program contains a class which can be called to extract
different series of data from IcePAP drivers and controllers
at a given ip in the white system.
"""
class IceParser:
	"""
	Creates an object which will read data from the IcePAPs
	at the adress 'ip'
	NOTE that connecting to the icePAP takes time, thus a 
	time.sleep()-call is added in the initiation.
	"""
	def __init__(self, ip):
		self.myice = EthIcePAP(ip, 5000)
		time.sleep(0.01)
		# self.totaldrivers = 0	
	"""
	Returns a list of ints representing the current temperature
	of all cards in the closet. To see which driver corresponds 
	to which temperature use getCardsAlive().
	"""
	def getCardTemps(self):
		drivertemp = []
		for driver in self.myice.getDriversAlive():
			input = int(self.myice.getMeas(driver,'T'))
			drivertemp.append(input)	
		for i in self.myice.getRacksAlive():
			input = int(self.myice.getMeas(i*10, 'T'))
			drivertemp.append(input)

		return drivertemp

	"""
	Returns a list of ints representingcthe temperature of the 
	power supplies in the various controllers in the closet	
	"""
	def getSupplyTemps(self):
		supplytemp = []
		for controller in self.myice.getRacksAlive():
			input = str(controller*10)
			string = self.myice.sendWriteReadCommand(input + ':?MEAS RT')
			split = string.split(' ')
			ret_int = int(split[1])
			supplytemp.append(ret_int)
		return supplytemp	


	"""
	Returns a dict representing the current versions
	of all cards in the closet.The versions of interest
	are:

	'CONTROLLER'
	'DRIVERS'
	'MCPU0'
	'MCPU1'
	'MCPU2'

	"""
	def getVersions(self): 
		return self.myice.getVersionInfoDict(0)			
	

	"""
	Returns a list containing all the drivers and controllers
	which are currently alive
	"""
	def getCardsAlive(self):
		alive_drivers = []
		for driver in self.myice.getDriversAlive():
			alive_drivers.append(driver)

		for controller in self.myice.getRacksAlive():
			alive_drivers.append(controller*10)
		
		return alive_drivers

	
	"""	
	Returns a list containing the status of the
	IcePAPs in the closet. If there is no driver in
	a certain card slot the status is represented
	with the value 'EMPTY'.
	"""
	def getStatus(self):
		status = []
		curr_pos = 0;

		for driver in self.myice.getDriversAlive():
			while driver > curr_pos:
				status.append('EMPTY')
				curr_pos += 1
			input = str(driver)
			
			string = self.myice.sendWriteReadCommand(input + ':?MODE')
			split = string.split(' ')
			status.append(split[1])
			curr_pos += 1
				
		for i in self.myice.getRacksAlive():
			input = str(i*10) # CHANGED
			string = self.myice.sendWriteReadCommand(input + ':?MODE')
			split = string.split(' ')
			status[i*10] = split[1]

		return status


	"""
	Returns a list containing the alarm status of the
	IcePAPs in the closet. If there is no driver in
	a certain card slot the status is represented
	with the value 'EMPTY'.	
	"""
	def getAlarmStatus(self):
		alarmstatus = []

		curr_pos = 0;
		for driver in self.myice.getDriversAlive():
			while driver > curr_pos:
				alarmstatus.append('EMPTY')
				curr_pos += 1
			input = str(driver)
			string = self.myice.sendWriteReadCommand(input + ':?ALARM')
			split = string.split(' ')
			alarmstatus.append(split[1])
			curr_pos += 1
				
		for i in self.myice.getRacksAlive():
			input = str(i)
			string = self.myice.sendWriteReadCommand(input + ':?ALARM')
			split = string.split(' ')
			alarmstatus[i*10] = split[1]

		return alarmstatus

	"""
	Checks if there are any racks alive on the adress
	"""	
	def isAlive(self):
		return len(self.myice.getRacksAlive()) > 0

		
	

def main():
	ice1 = IceParser('w-kitslab-icepap-10')
	ice2 = IceParser('w-kitslab-icepap-11')
	ice3 = IceParser('w-kitslab-icepap-12')
	time.sleep(0.01)
	print ice1.getSupplyTemps()
	print ice2.getSupplyTemps()
	print ice3.getSupplyTemps()
	


if __name__ == "__main__":
	main()
