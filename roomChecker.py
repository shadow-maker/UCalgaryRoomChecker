try:
	from selenium import webdriver
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	from selenium.common.exceptions import NoSuchElementException
	from selenium.webdriver.common.by import By
	from selenium.common.exceptions import TimeoutException
except ModuleNotFoundError:
	print("Required library 'selenium' not found")
	print("Please run the 'pip install selenium' command")

from datetime import datetime
from math import log10
import json
import os
import platform
import requests
import sys
import time

#
# UCALGARY ROOM CHECKER
#

class RoomChecker():

	lastCheck = []

	#
	# URLS
	#

	loginURL = "https://cas.ucalgary.ca/cas/?service=https%3a%2f%2fucalgary.starrezhousing.com%2fStarRezPortalX%2fRedirectLogin%2fStarNet.StarRez.AuthProviders.CasSso"
	errorPage = "https://ucalgary.starrezhousing.com/StarRezPortalX/Page/GetFirstPageWithReturnUrl?processID=22&returnUrl=%2FStarRezPortalX%2F3013DBBA%2F12%2F47%2FHome-Your_Resident_Portal%3FUrlToken%3D7A860693&isPageForContact=False&clearProcessContext=True&hash=003276C2"
	iftttPostURL = "https://maker.ifttt.com/trigger/room_available/with/key/"

	#
	# BOOLS
	#

	logToCSV = True
	logToJson = True
	saveSnapshot = True
	iftttPost = True
	postIfNoChange = False
	notifyMac = True

	#
	# FILE NAMES
	#

	csvFileName = "log.csv"
	jsonFileName = "log.json"
	snapshotDir = "snapshots"

	#
	# TIME VARS
	#

	timeout = 30
	sleepInterval = 300

	#
	# Init
	#

	def __init__(self, user, pssw, iftttKey="", checkPeriodically=False):
		self.br = webdriver.safari.webdriver.WebDriver()
		self.user = user
		self.pssw = pssw
		self.iftttKey = iftttKey
		self.checkPeriodically = checkPeriodically

	#
	# LOG
	#

	def logCSV(self, dtChecked, roomsAvailable):
		if self.logToCSV:
			with open(self.csvFileName, "a") as file:
				file.write(f"\n{dtChecked.strftime('%Y-%m-%d')},{dtChecked.strftime('%H:%M')},{roomsAvailable}")
	

	def logJSON(self, dtChecked, roomsData):
		if self.logToJson:
			with open(self.jsonFileName, "r") as file:
				log = json.load(file)

				dt = dtChecked.strftime("%Y,%m,%d,%H,%M").split(",")
				data = {dt[0]: {dt[1]: {dt[2]: {dt[3]: {dt[4]: roomsData}}}}}

				if dt[0] not in log:
					log[dt[0]] = data[dt[0]]
				elif dt[1] not in log[dt[0]]:
					log[dt[0]][dt[1]] = data[dt[0]][dt[1]] 
				elif dt[2] not in log[dt[0]][dt[1]]:
					log[dt[0]][dt[1]][dt[2]] = data[dt[0]][dt[1]][dt[2]]
				elif dt[3] not in log[dt[0]][dt[1]][dt[2]]:
					log[dt[0]][dt[1]][dt[2]][dt[3]] = data[dt[0]][dt[1]][dt[2]][dt[3]]
				else:
					log[dt[0]][dt[1]][dt[2]][dt[3]][dt[4]] = roomsData

			with open(self.jsonFileName, "w") as file:
				file.write(json.dumps(log))


	def snapshot(self, dtChecked, html):
		if self.saveSnapshot:
			snapDir = f"{self.snapshotDir}/{dtChecked.strftime('%Y-%m-%d')}/{dtChecked.strftime('%H')}"
		
		if not os.path.exists(snapDir):
			os.makedirs(snapDir)

		with open(snapDir + f"/{dtChecked.strftime('%M')}.html", "w") as file:
			file.write(html)
	

	def postIFTTT(self, dtChecked, roomsData, uniqueHalls):
		if self.iftttPost and self.iftttKey != "" and (self.lastCheck != roomsData or self.postIfNoChange):
			requests.post(self.iftttPostURL + self.iftttKey,
				{
					"value1": len(roomsData),
					"value2": ", ".join(uniqueHalls),
					"value3": dtChecked.strftime("%Y-%m-%d %H:%M")
				}
			)
	
	def postNotification(self, dtChecked, roomsData, uniqueHalls):
		if self.notifyMac and platform.system() == "Darwin" and (self.lastCheck != roomsData or self.postIfNoChange):
			os.system(f"""osascript -e 'display notification "{len(roomsData)} room(s) available for residence in {", ".join(uniqueHalls)}\nChecked: {dtChecked.strftime("%Y-%m-%d %H:%M")}" with title "ROOM AVAILABLE"'""")
	
	#
	# MAIN FUNCS
	#

	def sleep(self): # Sleep until next room check
		width = os.get_terminal_size().columns - 6 # Width of progress bar
		timePerChar = self.sleepInterval / width
		loadStates = ["\\", "|", "/", "-"]

		for i in range(width): # Loop width of progress bar
			for s in range(len(loadStates)): # Loop loading chars
				timeLeft = (self.sleepInterval - (timePerChar * (i + ((s + 1) / len(loadStates))))) + 0.01

				# Formar timeLeft so that its always 3 chars long
				timeDigs = int(log10(timeLeft)) + 1
				timeFormat = str(round(timeLeft, 1) if timeDigs < 2 else (round(timeLeft) if timeDigs < 4 else 999)).zfill(3)[:3]

				# Output progress bar
				sys.stdout.write(f"\r[{('-' * i)}{loadStates[s]}{' ' * (width - i - 1)}]{timeFormat}s")
				sys.stdout.flush()

				# Sleep time per state per char in progress bar
				time.sleep(timePerChar / len(loadStates))

		sys.stdout.write("\r" + (" " * os.get_terminal_size().columns)) # Clean


	def logIn(self): # Log-in with user's credentials
		sys.stdout.write("\r" + (" " * os.get_terminal_size().columns))
		sys.stdout.write("\r>LOGGING IN...")
		sys.stdout.flush()
		self.br.get(self.loginURL) # Navigate to page, will redirect if already logged in
		if self.br.current_url == self.loginURL: # If login is required, login
			self.br.find_element_by_id("eidtext").send_keys(self.user)
			self.br.find_element_by_id("passwordtext").send_keys(self.pssw)

			parentWindow  = self.br.window_handles[0]

			self.br.find_element_by_id("signinbutton").click()

			# Close pop-up

			WebDriverWait(self.br, 20).until(EC.number_of_windows_to_be(2))
			mainWin = [x for x in self.br.window_handles if x != parentWindow][0]
			self.br.switch_to.window(mainWin)
			self.br.close()
			self.br.switch_to.window(self.br.window_handles[0])
		
		try: # Wait for page to finish loading
			element_present = EC.presence_of_element_located(
				(By.LINK_TEXT, "Room Change")
			)
			WebDriverWait(self.br, self.timeout).until(element_present)
		except TimeoutException:
			print(">Loading took too much time!")


	def navigateToPage(self): # Navigate to room change page
		#preURL = self.br.current_url
		#self.br.refresh()
		
		link = self.br.find_element_by_link_text("Room Change")
		self.br.get(link.get_attribute("href"))

		button = self.br.find_element_by_tag_name("button")
		self.br.execute_script("arguments[0].click();", button)
		
		dtChecked = datetime.now()

		try: # Wait for page to finish loading
			element_present = EC.presence_of_element_located(
				(By.CLASS_NAME, "px_initialfilterstep_page")
			)
			WebDriverWait(self.br, self.timeout).until(element_present)
		except TimeoutException:
			print(">Loading took too much time!")
		
		return dtChecked


	def checkForRooms(self): # Check for available rooms
		sys.stdout.write("\r" + (" " * os.get_terminal_size().columns))
		sys.stdout.write("\r>CHECKING FOR ROOMS...")
		sys.stdout.flush()
		dtChecked = self.navigateToPage() # navigate to change rooms page and return dt checked
		html = self.br.page_source

		sys.stdout.write("\r" + (" " * os.get_terminal_size().columns))
		
		try: # IF Rooms are available
			hallsContainer = self.br.find_element_by_class_name("responsive-flow")
			hallsList = hallsContainer.find_elements_by_xpath("./*")
			roomsAvailable = True
		except NoSuchElementException: # Rooms are not available
			roomsAvailable = False
			sys.stdout.write(
				f"\r{dtChecked.strftime('%Y-%m-%d %H:%M')} - No rooms available yet\n"
			)
			sys.stdout.flush()
		
		roomsCount = 0
		if roomsAvailable:
			uniqueHalls = []
			roomsData = []

			for h in range(len(hallsList)): # Get info of each room available
				hallsContainer = self.br.find_element_by_class_name("responsive-flow")
				hall = hallsContainer.find_elements_by_xpath("./*")[h]
				hallName = hall.find_element_by_class_name("title").text
				uniqueHalls.append(hallName)

				sys.stdout.write(f"\rChecking for rooms in {hallName}...")
				sys.stdout.flush()

				# Go to results info page
				button = hall.find_element_by_class_name("ui-select-action")
				self.br.execute_script("arguments[0].click();", button)

				try: # Wait for page to finish loading
					element_present = EC.presence_of_element_located(
						(By.CLASS_NAME, "results-list")
					)
					WebDriverWait(self.br, self.timeout).until(element_present)
				except TimeoutException:
					print(">Loading took too much time!")

				roomsList = self.br.find_elements_by_class_name("item-result")

				roomNums = []
				for r in range(len(roomsList)):
					room = self.br.find_elements_by_class_name("item-result")[r]

					if "dummy-item-result" in room.get_attribute("class"):
						continue

					temp = room.find_element_by_class_name("title").text.split("-")
					roomNum = temp[0] + "-" + temp[1][:3]

					if roomNum in roomNums:
						continue
					else:
						roomNums.append(roomNum)
						roomsCount += 1
						sys.stdout.write("\r" + (" " * os.get_terminal_size().columns))
						sys.stdout.write(f"\r{len(roomNums)} rooms found in in {hallName}...")
						sys.stdout.flush()

					wing = room.find_element_by_class_name("multiline").text.split("\n")[0]
					capacity = room.find_element_by_class_name("capacity").text.replace("\n", "").replace("\t", "").replace(" ", "")

					# Go to room info page
					infoLink = room.find_element_by_link_text("Show Room Info")
					self.br.get(infoLink.get_attribute("href"))

					table = self.br.find_element_by_class_name("ui-active-table")
					tableBody = table.find_element_by_tag_name("tbody")
					tableRows = tableBody.find_elements_by_xpath("./*")

					# Get info of each occupant of the room
					occupants = []
					for row in tableRows:
						bed = row.find_element_by_class_name("roomspacedescription").text
						name = row.find_element_by_class_name("nameweb").text.replace("-","")
						gender = row.find_element_by_class_name("genderenum").text
						age = row.find_element_by_class_name("age").text
						age = 0 if name == "Vacant" else int(age)
						occupants.append({
							"bed": bed,
							"name": name,
							"gender": gender,
							"age": age
						})

					roomsData.append({
						"hall": hallName,
						"wing": wing,
						"roomNumber": roomNum,
						"capacity": int(capacity),
						"ocuppants": occupants
					})

					if r < len(roomsList) - 1:
						self.navigateToPage()
						hallsContainer = self.br.find_element_by_class_name("responsive-flow")
						hall = hallsContainer.find_elements_by_xpath("./*")[h]
						button = hall.find_element_by_class_name("ui-select-action")
						self.br.execute_script("arguments[0].click();", button)

						try: # Wait for page to finish loading
							element_present = EC.presence_of_element_located(
								(By.CLASS_NAME, "results-list")
							)
							WebDriverWait(self.br, self.timeout).until(element_present)
						except TimeoutException:
							print(">Loading took too much time!")

				self.navigateToPage()
				
			sys.stdout.write(
				f"\r{dtChecked.strftime('%Y-%m-%d %H:%M')} - {roomsCount} ROOM(S) AVAILABLE:\n"
				)
			sys.stdout.flush()

			for room in roomsData:
				print((" " * 19) + f"+ {room['hall']} - {room['roomNumber']} - {room['wing']} - {room['capacity']} beds")

				for occupant in room['ocuppants']:
					print((" " * 21) + f"> {occupant['bed']} - {occupant['name']} - {occupant['gender']} - {occupant['age']}y")

			self.postIFTTT(dtChecked, roomsData, uniqueHalls) # Post to IFTTT
			self.postNotification(dtChecked, roomsData, uniqueHalls)
			self.logJSON(dtChecked, roomsData) # Save JSON log
			self.lastCheck = roomsData

		self.logCSV(dtChecked, roomsCount) # Save CSV log
		self.snapshot(dtChecked, html) # Save HTML snapshot

		if self.checkPeriodically:
			print()
			self.sleep() # Sleep
			self.checkForRooms() # Recursive


	def begin(self):
		self.logIn()
		self.checkForRooms()