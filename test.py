import MFV

reader = MFV.MFV('/dev/ttyUSB3')

print(reader.reset())
