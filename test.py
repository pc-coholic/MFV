import MFV
import time

reader = MFV.MFV('/dev/ttyUSB3')

print(reader.reset())
print(reader.waitforinsert())
time.sleep(5)
print(reader.reset())
