#!/usr/bin/python

import pygame
import os
from Lib import Settings as st
from Lib import Screen as bs
from Lib import Logger as bl
from Lib.Timer import UpdateChecks

class MainWindow():
	def __init__(self):
		config = st.Config()
		self.Screen = bs.ScreenController()
		bl.SetLogLevel(config.LogLevel)
		bl.SetPrintLevel(config.PrintLevel)
		
		if os.path.exists('cache') is False:
			os.mkdir('cache')
	
	def run(self):
		running = True
		clock = pygame.time.Clock()
		config = st.Config()
		checks = UpdateChecks()
		
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				if event.type == pygame.KEYDOWN:
					if event.key is pygame.K_ESCAPE:
						running = False
					if event.key is pygame.K_TAB:
						if config.DisplayScreen == "departures":
							config.DisplayScreen = "arrivals"
						else:
							config.DisplayScreen = "departures"
						checks.SetTrue('dirty_screen')
						checks.SetTrue('dirty_source')
						
			
			self.Screen.update()
			bl.logger_update_loop()
			
			self.Screen.draw()
			#Log.Debug("<<TICK>>")
			clock.tick(30)
				
		pygame.quit()
		exit()
		
if __name__ == "__main__":
	config = st.Config()
	config.load_config("config.yaml")

	window = MainWindow()
	window.run()
