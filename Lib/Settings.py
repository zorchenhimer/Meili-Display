#!/usr/bin/python

import os
import yaml
from Logger import Debug, Warn, Info

class Config():
	class _config():
		def __init__(self):
			self.__source_uri = "http://127.0.0.1/schedule.xml"
			self.__display_screen = "departures"
			self.__display_fullscreen = False
			self.__update_interval = 30
			self.__page_interval = 15
			self.__log_level = "debug"
			self.__print_level = "debug"
			self.__1080p = False
		
		@property
		def SourceURI(self):
			return self.__source_uri
		
		@property
		def SeparateSources(self):
			return self.__separate_sources
		
		@property
		def DisplayScreen(self):
			return self.__display_screen
		
		@DisplayScreen.setter
		def DisplayScreen(self, val):
			if val == "departures" or val == "arrivals":
				self.__display_screen = val
			else:
				raise ValueError("DisplayScreen needs to be 'departures' or 'arrivals', got '" + str(val) + "' instead")
		
		@property
		def DisplayFullscreen(self):
			return self.__display_fullscreen
		
		@property
		def UpdateInterval(self):
			return self.__update_interval
		
		@property
		def PageInterval(self):
			return self.__page_interval
		
		@property
		def LogLevel(self):
			return self.__log_level
		
		@property
		def PrintLevel(self):
			return self.__print_level
		
		def write_default_config(self):
			yamltext = """
# Sources for the bus schedule.
source_uri: """ + self.__source_uri + """

# Display arrivals or departures?
display_screen: """ + self.__display_screen + """

# Run program in fullscreen mode?
display_fullscreen: !!bool \"""" + str(self.__display_fullscreen) + """\"

# These are both in seconds
update_interval: """ + str(self.__update_interval) + """
page_interval: """ + str(self.__update_interval) + """

# Choices are debug, warn, info, and silent.  Silent will not produce any
# output and will not rotate log files.
log_level: """ + self.__log_level + """
print_level: """ + self.__print_level + """
"""
			try:
				with open("config.yaml", 'w') as configfile:
					configfile.write(yamltext)
			except Exception as e:
				Warn("Unable to write default configuration file!" + str(e))
		
		def load_config(self, file):
			if os.path.isfile(file) is False:
				Warn("Cannot open configuration file; it doesn't exist! Attempting to write the default configuration file.")
				self.write_default_config()
		
			rawyaml = ''	
			with open(file) as infile:
				rawyaml = infile.read()
			
			data = yaml.load(rawyaml)
			for k in data.keys():
				if k == "source_uri":
					self.__source_uri = data[k]
				elif k == "display_screen":
					if data[k] == "departures" or data[k] == "arrivals":
						self.__display_screen = data[k]
					else:
						Warn("Configuration item 'display_screen' is an unexpected value.  Using default value of '" + self.__display_screen + "'")
				elif k == "display_fullscreen":
					if type(data[k]) == type(True):
						self.__display_fullscreen = data[k]
					else:
						Warn("Configuration item 'display_fullscreen' is wrong type.  Using default value of '" + str(self.__separate_sources) + "'")
				elif k == "update_interval":
					if type(data[k]) == float or type(data[k]) == int:
						if type(data[k]) == float:
							Warn("Configuration item 'update_interval' expected to be int, got float instead.  Casting to int.")
						self.__update_interval = int(data[k])
					else:
						Warn("Configuration item 'update_interval' is wrong type.  Using default value of '" + str(self.__update_interval) + "'")
				elif k == "page_interval":
					if type(data[k]) == float or type(data[k]) == int:
						if type(data[k]) == float:
							Warn("Configuration item 'page_interval' expected to be int, got float instead.  Casting to int.")
						self.__page_interval = int(data[k])
					else:
						Warn("Configuration item 'page_interval' is wrong type.  Using default value of '" + str(self.__page_interval) + "'")
				elif k == "log_level":
					levels = "debug warn info silent".split(" ")
					if data[k] in levels:
						self.__log_level = data[k]
					else:
						Warn("Configuration item 'log_leel' is an unexpected value.  Using default value of '" + self.__log_level + "'")
				elif k == "print_level":
					levels = "debug warn info silent".split(" ")
					if data[k] in levels:
						self.__print_level = data[k]
					else:
						Warn("Configuration item 'print_leel' is an unexpected value.  Using default value of '" + self.__print_level + "'")
				else:
					Warn("Found unexpected key: '" + str(k) + "'; ignoring")
	
	__instance = None
	
	def __init__(self):
		if Config.__instance == None:
			Config.__instance = Config._config()
		
		self.__dict__['_Singleton_instance'] = Config.__instance
		
	def __getattr__(self, attr):
		return getattr(self.__instance, attr)
	
	def __setattr__(self, attr, value):
		if attr is "ScreenSize" or attr is "Bounds":
			raise NotImplementedError
		return setattr(self.__instance, attr, value)
