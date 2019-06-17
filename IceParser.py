from pyIcePAP import *
import time
import re

# This program contains a class which can be called to extract
# different series of data from IcePAP drivers and controllers
# for a given rack in the white system.
class IceParser:

	# Creates an object which will read data from the IcePAPs
	# At the DNS _____________TBA__________________
	# NOTE that connecting to the icePAP takes time, thus a 
	# time.sleep()-call is added in the initiation.
	def __init__(self, DNS):
		self.myice = EthIcePAP(DNS, 5000)
		self.totaldrivers = 0
		time.sleep(1)
		
	

	# Returns a list of ints representing the current temperature
	# of all cards in the rack. To see which driver corresponds 
	#to which temperature use getCardsAlive().
	def getCardTemps(self):
		drivertemp = []
		for driver in self.myice.getDriversAlive():
			input = int(self.myice.getMeas(driver,'T'))
			drivertemp.append(input)	
		for i in self.myice.getRacksAlive():
			input = int(self.myice.getMeas(i*10, 'T'))
			drivertemp.append(input)

		return drivertemp


	# Returns a list of ints representingthe temperature of the 
	# power supplies in the varius controllers in the rack	
	def getSupplyTemps(self):
		supplytemp = []
		for controller in self.myice.getRacksAlive():
			input = str(controller*10)
			string = self.myice.sendWriteReadCommand(input + ':?MEAS RT')
			split = string.split(' ')
			ret_int = int(split[1])
			ssupplytemp.append(ret_int)
		return supplytemp	


	# Returns a dict representing the current versions
	# of all cards in the rack.The versions of interest
	# are :
	#
	# 'CONTROLLER'
	# 'DRIVERS'
	# 'MCPU0'
	# 'MCPU1'
	# 'MCPU2'
	#
	def getVersions(self): 
		return self.myice.getVersionInfoDict(0)			

	# Returns a list containing all the drivers and controllers
	# which are currently alive
	def getCardsAlive(self):
		alive_drivers = []
		for driver in self.myice.getDriversAlive():
			alive_drivers.append(driver)

		for controller in self.myice.getRacksAlive():
			alive_drivers.append(controller*10)
		
		return alive_drivers

	# Returns a list containing the status of the
	# IcePAPs on the rack. If there is no driver in
	# a certain card slot the status is represented
	# with the value 'EMPTY'.
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


	# Returns a list containing the alarm status of the
	# IcePAPs on the rack. If there is no driver in
	# a certain card slot the status is represented
	# with the value 'EMPTY'.	
	def getAlarmStatus(self):
		alarmstatus = []

		curr_pos = 0;
		for driver in self.myice.getDriversAlive():
			while driver > curr_pos:
				alarmstatus.append('EMPTY')
				curr_pos += 1
			input = str(driver)
			#print type(self.status)
			#print input + ':?MODE'
			#print type(self.myice.sendWriteReadCommand(input + ':?MODE'))
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

		
	

def main():
	ice = IceParser('w-kitslab-icepap-11')
	drivertemps = ice.getCardTemps()
	versions = ice.getVersions()
	status = ice.getStatus()
	alarmstatus = ice.getAlarmStatus()
	supplytemp = ice.getSupplyTemps()
	drivers = ice.getCardsAlive()

	print drivers
	print drivertemps
	print supplytemp
	print drivers



if __name__ == "__main__":
	main()
