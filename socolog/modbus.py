import sys
import urllib2
import json
import ConfigParser
import time
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# =======================
# Functions
# =======================

def readChannels():
    # voltage phase 1 to neutral
    print "New measurement readings: ", int(time.time())
    listValues = list()
    for c in listChannels:
    	handle = client.read_holding_registers(c['register'],c['words'],unit=c['unit'])
    	# print c['description'], ":"
    	if c['words'] > 1:
    		decoder = BinaryPayloadDecoder.fromRegisters(handle.registers, endian=Endian.Big)
    		value = decoder.decode_32bit_int()/float(c['factor'])
    	else:
    		value = handle.registers[0]/float(c['factor'])
    	#print c['description'], ":", str(value)
    	listValues.append(value)	

    for i, channel in enumerate(listChannels):
    	# print channel['description'],":", channel['uuid'], int(time.time()*1000), listValues[i]
    	# Here fire values into VZ middleware
    	addValue(channel['uuid'], int(time.time()*1000), listValues[i])
	
# Add measurement value
def addValue(uuid, timestamp, value):
	url = strURL + "/data/" + uuid + ".json?operation=add&ts=" + str(timestamp) + "&value=" + str(value)
	# print url
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	jsonVZ = response.read()
	# print jsonVZ
	return 1

# Create group in VZ
def createGroup(title, public=1):
	url = strURL + "/group.json?operation=add&title=" + title + "&public=" + str(public)
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	jsonVZ = response.read()
	# print(jsonVZ)
	data = json.loads(jsonVZ)
	_uuid = data["entity"]["uuid"]
	return _uuid

# Add group or channel to a parent group
def addToGroup(uuidParent, uuidChild):
	url = strURL + "/group/" + uuidParent + ".json?operation=add&uuid=" + uuidChild
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	jsonVZ = response.read()
	# print "addToGroup: " + jsonVZ
	return 1

# Get group ### Here better implement function like get all children
def getGroup(uuid):
	url = strURL + "/group/" + uuid + ".json"
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	jsonVZ = response.read()
	#print "getGroup: ", jsonVZ
	return jsonVZ

# Get children of group
# Returns list with uuids of children
def getChildren(uuid):
	data = json.loads(getGroup(uuid))

	listChildren = list()
	if 'entity' in data:
		if 'children' in data['entity']:
			for x in range(0,len(data['entity']['children'])):
				listChildren.append(data['entity']['children'][x]['uuid'])
	
	return listChildren

# Get title of group
def getGroupTitle(uuid):
	data = json.loads(getGroup(uuid))

	return data['entity']['title']

# Create Channel
def createChannel(type, title):
	url = strURL + "/channel.json?operation=add&type="+ type +"&title=" + title
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	jsonVZ = response.read()
	data = json.loads(jsonVZ)
	_uuid = data["entity"]["uuid"]
	return _uuid

# Test VZ installation
def testVZ():
	req = urllib2.Request(strURL)
	print req
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError as e:
		return False

	jsonVZ = response.read()

	try:
		data = json.loads(jsonVZ)
	except ValueError, e:
		return False

	return data['version']

# =======================
# Definitions
# =======================

print("Used Python version: ")
print(sys.version)

# Add channels
listChannels = list()
listChannels.append({'description': "V1_ph2n", 'register': 51284, 'words': 1, 'unit': 0xFF, 'measurement': "voltage", 'factor': 100})
listChannels.append({'description': "V2_ph2n", 'register': 51285, 'words': 1, 'unit': 0xFF, 'measurement': "voltage", 'factor': 100})
listChannels.append({'description': "V3_ph2n", 'register': 51286, 'words': 1, 'unit': 0xFF, 'measurement': "voltage", 'factor': 100})
listChannels.append({'description': "frequency", 'register': 51287, 'words': 1, 'unit': 0xFF, 'measurement': "frequency", 'factor': 100})
listChannels.append({'description': "P", 'register': 50536, 'words': 2, 'unit': 0xFF, 'measurement': "activepower", 'factor': 0.1}) # factor of Socomec from value to kVA(r): 100; from kW->W: 1/1000; result: factor=0.1
listChannels.append({'description': "P1", 'register': 50544, 'words': 2, 'unit': 0xFF, 'measurement': "activepower", 'factor': 0.1}) # factor of Socomec from value to kVA(r): 100; from kW->W: 1/1000; result: factor=0.1
listChannels.append({'description': "P2", 'register': 50546, 'words': 2, 'unit': 0xFF, 'measurement': "activepower", 'factor': 0.1}) # factor of Socomec from value to kVA(r): 100; from kW->W: 1/1000; result: factor=0.1
listChannels.append({'description': "P3", 'register': 50548, 'words': 2, 'unit': 0xFF, 'measurement': "activepower", 'factor': 0.1}) # factor of Socomec from value to kVA(r): 100; from kW->W: 1/1000; result: factor=0.1
listChannels.append({'description': "Q", 'register': 50538, 'words': 2, 'unit': 0xFF, 'measurement': "reactivepower", 'factor': 0.1}) # factor of Socomec from value to kVA(r): 100; from kW->W: 1/1000; result: factor=0.1
listChannels.append({'description': "Q1", 'register': 50550, 'words': 2, 'unit': 0xFF, 'measurement': "reactivepower", 'factor': 0.1}) # factor of Socomec from value to kVA(r): 100; from kW->W: 1/1000; result: factor=0.1
listChannels.append({'description': "Q2", 'register': 50552, 'words': 2, 'unit': 0xFF, 'measurement': "reactivepower", 'factor': 0.1}) # factor of Socomec from value to kVA(r): 100; from kW->W: 1/1000; result: factor=0.1
listChannels.append({'description': "Q3", 'register': 50554, 'words': 2, 'unit': 0xFF, 'measurement': "reactivepower", 'factor': 0.1}) # factor of Socomec from value to kVA(r): 100; from kW->W: 1/1000; result: factor=0.1

# =======================
# Initialization
# =======================

# Load data from config.ini
config = ConfigParser.ConfigParser()
config.readfp(open(r'config.ini'))
# main group UUID
mainGrpUUID = config.get('Status', 'uuid')
# URL to VZ middleware.php
strURL = config.get('General', 'url')

_testVZ = testVZ()

if _testVZ == False:
	print "Something is wrong with VZ server or URL."
	exit()

print "Version of VZ middleware:", _testVZ

# Reading frequency in seconds
intervalTime = config.get('General', 'intervalTime')
# Load name of location or measurement title
strName = config.get('General', 'name')
# Load IP of Socomec
strIP = config.get('General', 'IPsocomec')


# Initialize Modbus client
client = ModbusTcpClient(strIP)
ret = client.connect()
if ret:
	print "Connected to Socomec."
else:
	print "Connection to Socomec failed."
	exit()

# Start the scheduler
sched = BlockingScheduler()

# Check if main group already exists. If not (at first start): create one
if mainGrpUUID == "":
	print "No main group exists. Going to create one ..."
	# create main uuid
	mainGrpUUID = createGroup(strName, 1)
	print mainGrpUUID
	config.set('Status', 'uuid', mainGrpUUID)
	with open(r'config.ini', 'wb') as configfile:
		config.write(configfile)
else:
	print "Main group UUID: ", mainGrpUUID

# Check for existing subgroups
subGroups = {}
listGroups = getChildren(mainGrpUUID)

for x in listGroups:
	key = getGroupTitle(x)
	# print key, x
	if key not in subGroups:
		subGroups[key] = x
	else:
		print "Subgroup exists twice. That shouldn't happen."
		exit(500)

# print subGroups

# Now check measurement channels and to which group they belong.
# If subgroup for measurement type does not exits yet, create it.

for c in listChannels:
	strMeasurement = c['measurement']
	_uuid = 0

	# Check if subgroup already exists
	if strMeasurement not in subGroups:
		_uuid = createGroup(strMeasurement, 0)
		subGroups[strMeasurement] = _uuid
		print "Group created:", strMeasurement, addToGroup(mainGrpUUID, _uuid)

	# Create channel and add to group
	if (c['measurement'] == "voltage"):
		# Create channel for measurement
		_uuid = createChannel("voltage",c['description'])
	elif (c['measurement'] == "frequency"):
		# Create channel for measurement
		_uuid = createChannel("frequency",c['description'])
	elif (c['measurement'] == "activepower") or (c['measurement'] == "reactivepower"):
		# Create channel for measurement
		_uuid = createChannel("powersensor",c['description'])
	else:
		print "Measurement type not known."
		exit()

	# Add channel to subgroup
	print "Added to group successully:", addToGroup(subGroups[c['measurement']], _uuid)
	# Store UUID
	c['uuid'] = _uuid

# =======================
# Main
# =======================

sched.add_job(readChannels, 'interval', seconds=int(intervalTime))
sched.start()

client.close()
