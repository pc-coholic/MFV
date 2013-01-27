import serial
import sys

class MFV(object):
	def __init__(self, serialport = '/dev/ttyUSB0'):
		self.__ser = serial.Serial(serialport, baudrate=9600, dsrdtr=True)
		self.__DLE = '0x10'
		self.__STX = '0x02'
		self.__ETX = '0x03'
		self.__ENQ = '0x05'
		self.__ACK = '0x06'
		self.__NAK = '0x15'
		self.__EOT = '0x04'
		self.__CMD = '0x43'
		self.__POS = '0x50'
		self.__NEG = '0x4E'

	def reset(self):
		command = [self.__CMD, '0', '0']
		if self.send(command) == True:
			return self.enquire()
		else:
			return False

	def waitforinsert(self):
		command = [self.__CMD, ':', '0']
		if self.send(command) == True:
			return self.enquire()
		else:
			return False

	def enquire(self):
		return self.send([self.__ENQ])

	def send(self, command):
		if (command == [self.__ENQ]):
			command = [self.__DLE] + command
		else:
			# convert all strings to hex
			for i in range(1, len(command)):
				if type(command[i]) == type(str()):
					command[i] = str(command[i].encode("hex"))


			bcc = self.bcc(command)

			command = [self.__DLE, self.__STX] + command + [self.__DLE, self.__ETX, bcc]
	
		commandstr = ''
		for i in range(len(command)):
			command[i] = command[i][-2:]
			commandstr += chr(int("0x" + str(command[i]), 16))
		
		print("OUT: " + str(command))
		self.__ser.write(commandstr)
		return self.read()

	def read(self):
		ret = False
		exp = ""
		response = self.__ser.read(2)
		response = self.arrayify_response(response)

		if response[0] == self.__DLE:
			if response[1] == self.__ACK:
				exp = "ACK"
				ret = True
			elif response[1] == self.__STX:
				moreresponse = [0, 0]
				while moreresponse != [self.__DLE, self.__ETX]:
					moreresponse[0] = moreresponse[1]
					tmpresponse = self.arrayify_response(self.__ser.read(1))
					response += tmpresponse
					moreresponse[1] = tmpresponse[0]
				# Still need to read the bcc
				response += self.arrayify_response(self.__ser.read(1))
				
				if response[2] == self.__POS:
					ret = True
					exp = "ACK; POSITIVE; Response follows"
				elif response[2] == self.__NEG:
					ret = True
					exp = "ACK; NEGATIVE; Response follows"
				else:
					ret = False
					exp = "ACK; UNKNOWN; Response follows"
			else:
				print("Received unknown reponse-state " + str(response[1]))
		else:
			exp = "Some error occured"

		print("IN:  " + str(response) + " " + exp)
		return ret

	def bcc(self, command):
		command = command + [self.__ETX]
		
		bcc = 0
		for arg in command:
			bcc = bcc^int(arg, 16)
		
		return hex(bcc)

	def arrayify_response(self, response):
		array = []
		for i in range( 0, len(response) ):
			#array += [str("".join([str(hex(ord(x)))[2:] for x in response[i]]))]
			array += ["0x%0.2X" % ord(response[i])]
			 
		return array
