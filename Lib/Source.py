#!/usr/bin/python

import random ## Testing only
import time
import re
import os
import urllib
import xml.etree.ElementTree as ET
import json
import Data
import Settings
from Timer import UpdateChecks
from Logger import Debug, Info, Warn

class BaseSource():
	def __init__(self):
		self.last_update = 0
		self.UpdateFrequency = 30
		self.Arrivals = Data.BusList()
		self.Departures = Data.BusList()
		checks = UpdateChecks()
		config = Settings.Config()
		
		self.LocalSource = 'cache/' + os.path.basename(config.SourceURI)		## Path to the downloaded file.
		self.RemoteSource = config.SourceURI
	
	def update(self):
		checks = UpdateChecks()
		if checks.TimeToUpdate('source_update'):
			Debug('Updating source')
			
			dlfile = urllib.URLopener()
			try:
				dlfile.retrieve(self.RemoteSource, self.LocalSource)
			except Exception as e:
				Warn("DL of '" + self.RemoteSource + "' failed: " + str(e))
				
			self.ParseSource()
			
			## This is just because I'm lazy...
			#json_string = json.dumps( {"arrivals": self.Arrivals.get_dict(), "departures": self.Departures.get_dict()} )
			#print "json > " + json_string + " <"
			#exit(1)
			
			checks.Update('source_update')
			checks.SetTrue('dirty_source')
	
	def DownloadRemote(self):
		dlfile = urllib.URLopener()
		try:
			dlfile.retrieve(self.RemoteSource, self.LocalSource)
		except Exception as ex:
			Warn("DL of '"+self.RemoteSource+"' failed: "+str(e))

	def ParseSource(self):
		raise NotImplementedError

class JSONSource(BaseSource):
	def __init__(self):
		BaseSource.__init__(self)
		Debug('JSONSource init\'d')

	def ParseSource(self):
		Debug('Entering JSONSource.ParseSource()')
		jfile = open(self.LocalSource, 'r')
		try:
			Debug('Attempting to load jfile...')
			json_dict = json.load(jfile)
		except Exception as ex:
			Error("Unable to load jfile.\n" + str(jfile))
			exit()
		jfile.close()
		
		self.Arrivals.clear()
		self.Departures.clear()
		
		for arrival in json_dict['arrivals']:
			self.Arrivals.append(
				Data.BusArrival( arrival['company'],
								 arrival['city'],
								 arrival['time'],
								 arrival['status']
								 )
			)
		
		for departure in json_dict['departures']:
			self.Departures.append(
				Data.BusDeparture( departure['company'],
								   departure['city'],
								   departure['time'],
								   departure['status'],
								   departure['gate'],
								   departure['busnum']
								   )
			)
		
class XMLSource(BaseSource):
#	def __init__(self):
#		BaseSource.__init__(self)
		
	def ParseSource(self):
		data = ET.parse(self.LocalSource)
		root = data.getroot()
		
		self.Arrivals.clear()
		self.Departures.clear()
		dep = root.get('departures')
		arv = root.get('arrivals')
		
		for type in root:
			for bus in type:
				busdata = None
				list = None
				if type.tag == 'departures':
					busdata = Data.BusDeparture()
					list = self.Departures
				else:
					busdata = Data.BusArrival()
					list = self.Arrivals
				for cell in bus:
					if cell.tag == "company":
						busdata.Company = cell.text.title()
					elif cell.tag == "city":
						busdata.City = cell.text.title()
					elif cell.tag == "time":
						busdata.Time = cell.text.strip()
					elif cell.tag == "status":
						busdata.Status = cell.text.title()
					elif cell.tag == "gate":
						busdata.Gate = cell.text
					elif cell.tag == "busnum":
						busdata.Number = cell.text
					else:
						Warn("Found unexpected element in XML: " + cell.tag)
				list.append(busdata)
	
class DummySource(BaseSource):
	def SourceUpdate(self):
		del self.Arrivals[:]
		del self.Departures[:]
		
		derp = "a b c d e f g h i j k l m n o p q r s t u v w x y z".upper().split(" ")
		
		arrivals = Data.BusList()
		departures = Data.BusList()
		
		for i in range(10):
			arrivals.append_bus(Data.BusArrival("Company " + derp[i], "City " + derp[:i], str(i) + ":00pm", random.randint(1, 4)))
		
		for i in range(10):
			departures.append_bus(Data.BusDeparture("Company " + derp[i], "City " + derp[:i], str(i) + ":00pm", random.randint(1, 4), random.randint(1, 12), random.randint(1, 9999)))
	
