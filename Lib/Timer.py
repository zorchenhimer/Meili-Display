#!/usr/bin/python

import time
from Logger import Debug, Info, Warn

class TimerEvent():
	def __init__(self, id, interval=5):
		self.ID = id
		self.LastUpdate = 0
		self.UpdateInterval = interval
		Info("New TimerEvent() with id '" + str(self.ID) + "'")
	
	def time_to_update(self):
		if time.time() - self.LastUpdate > self.UpdateInterval:
			Debug("It's time to update '" + str(self.ID) + "'")
			return True
		return False
	
	def update(self):
		Debug("Updated '" + str(self.ID) + "'")
		self.LastUpdate = time.time()

class UpdateChecks():
	class _timers():
		def __init__(self):
			self.TimerDict = {}
			self.StateDict = {}
			Debug('UpdateChecks() singleton init\'d')
		
		def AddTimer(self, id, interval=None):
			if interval is None:
				self.TimerDict[id] = TimerEvent(id)
				Debug("Adding timer '" + str(id) + "' with default interval")
			else:
				self.TimerDict[id] = TimerEvent(id, interval)
				Debug("Adding timer '" + str(id) + "' with interval " + str(interval))
		
		def AddState(self, id, initial=None):
			if initial is None:
				self.StateDict[id] = False
				Debug("Adding state '" + str(id) + "' with default value of False")
			else:
				self.StateDict[id] = initial
				Debug("Adding stat '" + str(id) + "' with value " + str(initial))
		
		def TimeToUpdate(self, id):
			if id in self.TimerDict.keys():
				return self.TimerDict[id].time_to_update()
			else:
				raise KeyError("TimeEvent with ID '" + str(id) + "' does not exist")
		
		def Update(self, id):
			if id in self.TimerDict.keys():
				self.TimerDict[id].update()
			else:
				raise KeyError("TimeEvent with ID '" + str(id) + "' does not exist")
		
		def SetUpdateInterval(self, id, interval):
			if id in self.TimerDict.keys():
				self.TimerDict[id].UpdateInterval = interval
				Debug("Updating update interval of TimerEvent '" + str(id) + "' to " + str(interval))
			else:
				raise KeyError("TimeEvent with ID '" + str(id) + "' does not exist")
		
		def GetState(self, id):
			if id in self.StateDict.keys():
				return self.StateDict[id]
			else:
				raise KeyError("State with ID '" + str(id) + "' does not exist")
		
		def SetTrue(self, id):
			if id in self.StateDict.keys():
				self.StateDict[id] = True
				Debug("Setting state with ID '" + str(id) + "' to True")
			else:
				raise KeyError("State with ID '" + str(id) + "' does not exist")
			
		def SetFalse(self, id):
			if id in self.StateDict.keys():
				self.StateDict[id] = False
				Debug("Setting state with ID '" + str(id) + "' to False")
			else:
				raise KeyError("State with ID '" + str(id) + "' does not exist")
		
		def _dump_timers(self):
			print "== Dumping registered TimerEvent() objects =="
			for t in self.TimerDict.keys():
				print '[' + t + '] ' + str(self.TimerDict[t].ID) + '; LastUpdate: ' + str(self.TimerDict[t].LastUpdate) + '; UpdateInterval: ' + str(self.TimerDict[t].UpdateInterval)
			print "== End =="
	
	__instance = None
	
	def __init__(self):
		if UpdateChecks.__instance == None:
			UpdateChecks.__instance = UpdateChecks._timers()
		
		self.__dict__['_Singleton_instance'] = UpdateChecks.__instance
		
	def __getattr__(self, attr):
		return getattr(self.__instance, attr)
	
	def __setattr__(self, attr, value):
		if attr is "ScreenSize" or attr is "Bounds":
			raise NotImplementedError
		return setattr(self.__instance, attr, value)
