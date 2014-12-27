#!/usr/bin/python

import math
import pygame
import platform
import time
import os.path as path
import os
import Source as ds
import Data
import Settings
from Timer import UpdateChecks
from Logger import Debug, Warn, Info

def LoadImage(path):
	""" Return a surface containing the image at the given path. """
	surf = None
	Debug("Loading image at path '" + str(path) + "'")
	#path = FixPath(path)
	try:
		surf = pygame.Surface.convert_alpha(pygame.image.load(path))
	except Exception as exc:
		Warn("Unable to load image at path '" + path + "': " + str(exc))
	return surf

def FixPath(p):
	""" Return the correct path format depending on the current system. """
	if platform.system().lower() == 'windows':
		return path.abspath(p.replace('/', '\\'))
	else:
		return path.abspath(p.replace('\\', '/'))

def TileImage(surf, dest_surf=pygame.display.get_surface()):
	"""
		Return a new surface the size of the destination surface with the given
		surface tiled in both directions.  Destination surface defaults to the
		main display surface.
	"""
	if isinstance(surf, pygame.Surface):
		newsurf = pygame.Surface(dest_surf.get_size())
		widthRepeat = int(math.ceil(newsurf.get_width() / surf.get_width()))
		heightRepeat = int(math.ceil(newsurf.get_height() / surf.get_height()))
		
		(surfW, surfH) = surf.get_size()
		for h in range(0, heightRepeat + 1):
			for w in range(0, widthRepeat + 1):
				newsurf.blit(surf, (w * surfW, h * surfH))
	else:
		return TileImage(LoadImage(surf), dest_surf)
	return newsurf

class ScreenController():
	def __init__(self, width = 1280, height = 720):
		config = Settings.Config()
		if config.DisplayFullscreen is False:
			os.environ['SDL_VIDEO_CENTERED'] = '1'
			self.screen = pygame.display.set_mode((width, height))
		else:
			self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
			
		pygame.init()
		
		self.Background = TileImage("img/bg-dark.gif", self.screen)	
		self.screen.blit(self.Background, (0,0))
		pygame.mouse.set_visible(False)
		pygame.display.flip()
		
		checks = UpdateChecks()
		checks.AddTimer('page_delay', config.PageInterval)
		checks.AddTimer('source_update', config.UpdateInterval)
		checks.Update('page_delay')
		
		checks.AddState('dirty_source', True)
		checks.AddState('dirty_screen', True)
		checks.AddState('dirty_page', False)
		checks.AddState('error', False)
		
		self.DrawArrivals = True
		if config.DisplayScreen == 'departures':
			self.DrawArrivals = False
			
		self.CurrentPage = 1
		self.RowsPerPage = 10	# 12 rows minus the header
		self.FirstRow = 0		# First row to draw
		
		# FIXME: proper error handling and checking needed here.
		if config.SourceURI[-4:] == '.xml':
			self.Source = ds.JSONSource()
			Debug('XML source found.')
		else:
			self.Source = ds.XMLSource()
			Debug('JSON source found.')
			
		self.CachedList = Data.BusList()
		self.List = Data.BusList()
		self.ArrivalHeader = HeaderRow(Data.BusArrival("Company", "City", "Time", "Status"))
		self.DepartureHeader = HeaderRow(Data.BusDeparture("Company", "City", "Time", "Status", "Gate", "Bus #"))
		
		self.ErrorScreen = None
	
	def update(self):
		checks = UpdateChecks()
		config = Settings.Config()
		if checks.GetState('error') is True:
			checks.SetFalse('error')
		#self.Source.update()
		try:
			#pass
			self.Source.update()
		except Exception as e:
			Warn("Source update failed: " + str(e))
			color = (148, 14, 14)
			static = RowStatic()
			self.ErrorScreen = static.HeaderFont.render("Error: Failed to retrieve update!", True, color).convert_alpha()
			checks.SetTrue('error')
			exit()
			## This makes debugging easier
			#raise e
			
		if checks.GetState('dirty_source') is True:
			checks.SetFalse('dirty_source')
			self.List.clear()
			
			lst = self.Source.Arrivals
			if config.DisplayScreen == "departures":
				lst = self.Source.Departures
				
			for d in lst:
				self.List.append(BusRow(d))
				
			if len(self.List) <= self.RowsPerPage:
				checks.SetTrue('dirty_screen')
				self.CachedList = self.List
				Debug("Source updated with one screen of buses, scheduling screen update. (" + str(len(self.CachedList)) + ":" + str(self.RowsPerPage) + ")")
				
		if len(self.List) > self.RowsPerPage:
			if checks.TimeToUpdate('page_delay') is True:
				# It's time to paginate
				checks.Update('page_delay')
				checks.SetTrue('dirty_screen')
				self.FirstRow = self.CurrentPage * self.RowsPerPage
				self.CurrentPage += 1
				
			if len(self.CachedList) / self.RowsPerPage < self.CurrentPage:
				Debug("Updating CachedList")
				self.CurrentPage = 0
				#self.FirstRow = 0
				self.CachedList = self.List
				Debug("CurrentPage: " + str(self.CurrentPage) + "; FirstRow: " + str(self.FirstRow) + "; len(CachedList): " + str(len(self.CachedList)))
			
		if len(self.CachedList) == 0:
			Debug("CachedList is empty.  Updating.")
			self.CachedList = self.List
			self.CurrentPage = 0
			checks.SetTrue('dirty_screen')
		
		if (self.FirstRow / self.RowsPerPage > len(self.CachedList) / self.RowsPerPage):
			Debug("Past the last page.  Resetting.")
			self.FirstRow = 0
			self.CurrentPage = 0
	
	def draw(self):
		checks = UpdateChecks()
		config = Settings.Config()
		if checks.GetState('error') is True:
			self.screen.blit(self.Background, (0,0))
			self.screen.blit(self.ErrorScreen, ((self.screen.get_width() / 2) - (self.ErrorScreen.get_width()/2), (self.screen.get_height() / 2) - (self.ErrorScreen.get_height()/2)))
			return
		
		if checks.GetState('dirty_screen') is True:
			self.screen.blit(self.Background, (0,0))
			
			total_pages = len(self.CachedList) / self.RowsPerPage
			if len(self.CachedList) == self.RowsPerPage:
				total_pages = 0
			
			if config.DisplayScreen == "arrivals":
				self.ArrivalHeader.draw(self.screen, (self.FirstRow / self.RowsPerPage), total_pages)
			else:
				self.DepartureHeader.draw(self.screen, (self.FirstRow / self.RowsPerPage), total_pages)
			
			if len(self.CachedList) == 0:
				Debug("Empty Cached List! Drawing error message.")
				static = RowStatic()
				emptymsg = static.HeaderFont.render("No Buses!", True, static.HeaderFontColor)
				self.screen.blit(emptymsg, ((self.screen.get_width()/2)-(emptymsg.get_width()/2),(self.screen.get_height()/2)-(emptymsg.get_height()/2)))
			else:
				row = 2
				x = 0
				for b in self.CachedList[self.FirstRow:(self.FirstRow + self.RowsPerPage)]:
					x += 1
					b.draw(self.screen, row)
					row += 1
		
		if checks.GetState('dirty_screen') is True:
			checks.SetFalse('dirty_screen')
			pygame.display.flip()
	
class BusRow(pygame.sprite.Sprite):
	def __init__(self, data, header=False):
		pygame.sprite.Sprite.__init__(self)
		self.Data = data
		self.Height = pygame.display.get_surface().get_height() / 12
		self.Width = pygame.display.get_surface().get_width()
		self.XOffset = 70
		
		self.image = None
		self.rect = None
		
		self.rendered_text = []
		static = RowStatic()
		self.background = static.DarkBackground
		self.fontcolor = static.FontColor_Light
		self.font = static.Font
	
	def draw(self, screen, row):
		static = RowStatic()
		
			
		if row % 2 == 0:
			self.background = static.LightBackground
			self.fontcolor = static.FontColor_Dark
			if self.Data.Status.lower() == "delayed":
				self.background = static.DelayedBackgroundLight
			elif self.Data.Status.lower() == "canceled":
				self.background = static.CanceledBackgroundLight
			elif self.Data.Status.lower() == "boarding":
				self.background = static.BoardingBackgroundLight
				
		elif self.Data.Status.lower() == "delayed":
			self.background = static.DelayedBackgroundDark
			self.fontcolor = static.FontColor_Light
		elif self.Data.Status.lower() == "canceled":
			self.background = static.CanceledBackgroundDark
			self.fontcolor = static.FontColor_Light
		elif self.Data.Status.lower() == "boarding":
			self.background = static.BoardingBackgroundDark
			self.fontcolor = static.FontColor_Light
		
		
		self.image = TileImage(self.background, pygame.Surface((self.Width, self.Height)))
		self.rect = self.image.get_rect()
		
		del self.rendered_text[:]
		if self.Data.Time.lower() != "time":
			self.Data.Time = self.Data.Time.lower()
		
		self.rendered_text.append(self.font.render(self.Data.Time, True, self.fontcolor).convert_alpha())
		self.rendered_text.append(self.font.render(self.Data.City, True, self.fontcolor).convert_alpha())
		self.rendered_text.append(self.font.render(self.Data.Company, True, self.fontcolor).convert_alpha())
		
		if self.Data.is_departure():
			self.rendered_text.append(self.font.render(self.Data.Gate, True, self.fontcolor).convert_alpha())
			self.rendered_text.append(self.font.render(self.Data.Number, True, self.fontcolor).convert_alpha())
			
		self.rendered_text.append(self.font.render(self.Data.Status, True, self.fontcolor).convert_alpha())
			
		midoffset = self.image.get_height() / 4			
		
		total_width = 0
		for t in self.rendered_text:
			total_width += t.get_width()
		offsets = self.image.get_width() / len(self.rendered_text)
		
		column = 0
		for t in self.rendered_text:
			if row < 0:
				self.image.blit(t, (column * offsets + (self.XOffset), ((midoffset * 3) - (t.get_height()/2))))
			else:
				self.image.blit(t, (column * offsets + (self.XOffset), (t.get_height()/2)))
			column += 1
		
		if row < 0:
			pass
		else:
			screen.blit(self.image, (0, (self.Height * row)))


class HeaderRow(BusRow):
	def __init__(self, data):
		BusRow.__init__(self, data)
		self.Height *= 2
		self.Data = data
		
		static = RowStatic()
		self.font = static.HeaderFont
		self.fontcolor = static.HeaderFontColor
		self.background = static.HeaderBackground
		self.timefont = static.TimeFont
	
	def draw(self, screen, current_page, total_pages):
		#print "page " + str(current_page + 1) + " of " + str(total_pages + 1)
		titletext = "Arrivals"
		if self.Data.is_departure() is True:
			titletext = "Departures"
		
		timestruct = time.localtime()
		months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
		days = "Sun Mon Tues Wed Thurs Fri Sat".split(" ")
		ampm = 'am'
		hour_12 = timestruct.tm_hour
		if hour_12 > 12:
			ampm = 'pm'
			hour_12 -= 12
		elif hour_12 == 0:
			hour_12 = 12
		
		minute = timestruct.tm_min
		if minute < 10:
			minute = '0' + str(minute)
		
		Debug("{Header} current_page: " + str(current_page) + "; total_pages: " + str(total_pages))
		pagestring = "Page " + str(current_page + 1) + " of " + str(total_pages + 1)
		
		timestring = days[timestruct.tm_wday] + ", " + months[timestruct.tm_mon-1] + " " + str(timestruct.tm_mday) + ", " + str(hour_12) + ':' + str(minute) + ampm
		
		static = RowStatic()
		
		BusRow.draw(self, self.image, -1)		
		midoffset = self.image.get_height() / 4
		
		rendered_title = self.font.render(titletext, True, self.fontcolor).convert_alpha()
		rendered_time = self.timefont.render(timestring, True, self.fontcolor).convert_alpha()
		rendered_page = self.timefont.render(pagestring, True, self.fontcolor).convert_alpha()
		screen.blit(self.image, (screen.get_width()/2 - self.image.get_width()/2, 0))
		screen.blit(rendered_title, ((self.image.get_width()/2) - (rendered_title.get_width()/2), (midoffset - rendered_title.get_height()/2)))
		screen.blit(rendered_time, (20, (midoffset - rendered_time.get_height()/2)))
		screen.blit(rendered_page, (screen.get_width() - rendered_page.get_width() - 20, (midoffset - rendered_time.get_height()/2)))
		
		
class RowStatic():
	"""
		All the static data that's needed by the individual rows.  This makes
		sure each resource is only loaded into memory once.
	"""
	class _static:
		def __init__(self):
			## Warning: these should probably be absolute paths.
			self.Font = pygame.font.Font('Lib/profont.ttf', 20)#30)
			self.HeaderFont = pygame.font.Font('Lib/profont.ttf', 30)#45)
			self.TimeFont = pygame.font.Font('Lib/profont.ttf', 25)# 33)
			self.FontColor_Dark = (0, 0, 0)
			self.FontColor_Light = (200, 200, 200)
			self.HeaderFontColor = (255, 255, 255)
			self.LightBackground = LoadImage('img/bg-light.gif')
			self.DarkBackground = LoadImage('img/bg-dark.gif')
			self.HeaderBackground = LoadImage('img/bg-header.gif')
			self.DelayedBackgroundDark = LoadImage('img/bg-delayed-dark.gif')
			self.DelayedBackgroundLight = LoadImage('img/bg-delayed-light.gif')
			self.CanceledBackgroundDark = LoadImage('img/bg-canceled-dark.gif')
			self.CanceledBackgroundLight = LoadImage('img/bg-canceled-light.gif')
			self.BoardingBackgroundDark = LoadImage('img/bg-boarding-dark.gif')
			self.BoardingBackgroundLight = LoadImage('img/bg-boarding-light.gif')
	
	__instance = None
	
	def __init__(self):
		if RowStatic.__instance == None:
			RowStatic.__instance = RowStatic._static()
		
		self.__dict__['_Singleton_instance'] = RowStatic.__instance
		
	def __getattr__(self, attr):
		return getattr(self.__instance, attr)
	
	def __setattr__(self, attr, value):
		if attr is "ScreenSize" or attr is "Bounds":
			raise NotImplementedError
		return setattr(self.__instance, attr, value)
