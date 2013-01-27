import serial

class MFV(object):
	def __init__(self, serialport = '/dev/ttyUSB0'):
		self.__ser = serial.Serial(serialport, baudrate=9600, dsrdtr=True)
		self.__DLE = 10
		self.__STX = 2
		self.__ETX = 3
		self.__ENQ = 5
		self.__ACK = 6
		self.__NAK = 15
		self.__EOT = 4
		self.__CMD = 43

	def reset(self):
		command = [self.__CMD, "0", "0"]
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
			for i in range(len(command)):
				if type(command[i]) == type(str()):
					command[i] = int(command[i].encode("hex"))
	
			bcc = self.bcc(command)
			
			command = [self.__DLE, self.__STX] + command + [self.__DLE, self.__ETX, bcc]

		commandstr = ''
		for arg in command:
			commandstr += chr(int("0x" + str(arg), 16))
			

		print("OUT: " + str(command))
		self.__ser.write(commandstr)
		return self.read()

	def read(self):
		ret = False
		exp = ""
		response = self.__ser.read(2)
		response = self.arrayify_response(response)
		
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
			ret = True
			exp = "ACK; Response follows"
		else:
			print("Received unknown reponse-state " + str(response[1]))

		print("IN:  " + str(response) + " " + exp)
		return ret

	def bcc(self, command):
		command = command + [self.__ETX]
		
		bcc = 0
		for arg in command:
			bcc = bcc^arg
		
		return bcc

	def arrayify_response(self, response):
		array = []
		for i in range( 0, len(response) ):
			array += [int("".join([str(hex(ord(x)))[2:] for x in response[i]]))]

		return array
