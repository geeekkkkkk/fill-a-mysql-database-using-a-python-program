from typing import Dict
from bs4 import BeautifulSoup
import mysql.connector
mydb = mysql.connector.connect(host="localhost", username="root", password="", database="airplaneinfo")
mycursor = mydb.cursor(buffered=True)
fileName = input("Enter the file name: ")
with open(fileName, 'r') as f:
	data = f.read()

Bs_data = BeautifulSoup(data, "xml")

def findtags(tagname, attr):
	return Bs_data.find_all(tagname, {'name' : attr})

b_locationid = findtags('SimpleData', 'locationid')
b_boxid = findtags('SimpleData', 'boxid')
coords = Bs_data.find_all('coordinates')
b_classid = findtags('SimpleData', 'classid')
b_date = findtags('SimpleData', 'date')
b_airportname = findtags('SimpleData', 'airport_name')
b_confidence = findtags('SimpleData', 'confidence')

def convert(somevar):
	return str(somevar.encode('utf-8'), 'utf-8') #converts binary variable to unicode

mylocationid = []
myboxid = []
b_latitude = []
b_longitude = []
myclass = set()
mydate = []
myairportname = set()
myconfidence = []

x = range(len(b_locationid))
flag = 0
for n in x:
	mylocationid.append(convert(b_locationid[n].string))
	myboxid.append(convert(b_boxid[n].string))
	mystr = coords[n].string
	comma_split = mystr.split(',')
	b_latitude.append(float(comma_split[1]))
	b_longitude.append(float(comma_split[0]))
	myclass.add(convert(b_classid[n].string))
	mydate.append(convert(b_date[n].string))
	myairportname.add(convert(b_airportname[n].string))
	myconfidence.append(float(convert(b_confidence[n].string)))
	try:
		mycursor.execute("INSERT INTO trying (locationid, boxid, latitude, longitude, classname, airportname, confidence, mydates) VALUES (%s, %s, %s, %s, %s, %s, %s)", (myboxid, b_latitude, b_longitude, myclass, myairportname, myconfidence, mydate))
	except:
		continue
classcursor = mydb.cursor(buffered=True)
classcursor.execute("SELECT DISTINCT classname FROM trying")
mylist = []
i = 1
for x in classcursor:
	if(x[0] == "NULL"):
		continue
	else:
		try:
			mycursor.execute("INSERT INTO airplaneclass (classid, classname) VALUES (%s, %s)", (i, x[0]))
		except:
			continue
	i += 1
aptcursor = mydb.cursor(buffered=True)
i = 1
aptcursor.execute("SELECT DISTINCT airportname FROM trying")	
for y in aptcursor:
	if(y[0] == "NULL"):
		continue
	else:
		try:
			mycursor.execute("INSERT INTO airport (airportid, airportname) VALUES (%s, %s)", (i, y[0]))
		except:
			continue
	i += 1
boxcursor = mydb.cursor(buffered=True)
i = 1
boxcursor.execute("SELECT DISTINCT boxid FROM trying")
for z in boxcursor:
	if (z[0] == 0):
		continue
	else:
		classidcursor = mydb.cursor(buffered = True)
		myexecute = "SELECT DISTINCT classid, confidence FROM airplaneclass, trying WHERE airplaneclass.classname = trying.classname AND trying.boxid = %s"
		classidcursor.execute(myexecute, (z[0], ))
		for myvars in classidcursor:
			try:
				mycursor.execute("INSERT INTO finalinfo (boxid, classid, confidence) VALUES (%s, %s, %s)", (z[0], myvars[0], myvars[1]))
			except:
				break
loccursor = mydb.cursor(buffered=True)
loccursor.execute("SELECT locationid, boxid, airportid, latitude, longitude, mydates FROM trying, airport WHERE trying.airportname = airport.airportname")
for locitems in loccursor:
	if(locitems[1] != 0):
		try:
			mycursor.execute("INSERT INTO locations (locationid, boxid, airportid, latitude, longitude, capturedate) VALUES (%s, %s, %s, %s, %s, %s)", (locitems[0], locitems[1], locitems[2], locitems[3],locitems[4],locitems[5]))
		except:
			continue
	else:
		nullvalue = None
		try:
			mycursor.execute("INSERT INTO locations (locationid, boxid, airportid, latitude, longitude, capturedate) VALUES (%s, %s, %s, %s, %s, %s)", (locitems[0], locitems[1], locitems[2], nullvalue, nullvalue, locitems[5]))
		except:
			continue
vartable = {"locationid": "locations", "boxid" : ("locations", "finalinfo"), "airplanename" : ("airplaneclass", "finalinfo"), "airportname" : ("airport", "locations")}





