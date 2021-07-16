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
import json
import os
import requests
import time

#
# UCALGARY ROOM CHECKER
#

class RoomChecker():

	#
	# URLS
	#

	loginURL = "https://cas.ucalgary.ca/cas/?service=https%3a%2f%2fucalgary.starrezhousing.com%2fStarRezPortalX%2fRedirectLogin%2fStarNet.StarRez.AuthProviders.CasSso"
	iftttPostURL = "https://maker.ifttt.com/trigger/room_available/with/key/"

	#
	# BOOLS
	#

	iftttPost = True
	logToCSV = True
	logToJson = True
	saveSnapshot = True

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

	def postIFTTT(self, roomsAvailable, uniqueHalls, dtChecked):
		if self.iftttPost and self.iftttKey != "":
			requests.post(self.iftttPostURL + self.iftttKey,
				{
					"value1": roomsAvailable,
					"value2": ", ".join(uniqueHalls),
					"value3": dtChecked.strftime("%Y-%m-%d %H:%M")
				}
			)


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
				else:
					if dt[1] not in log[dt[0]]:
						log[dt[0]][dt[1]] = data[dt[0]][dt[1]] 
					else:
						if dt[2] not in log[dt[0]][dt[1]]:
							log[dt[0]][dt[1]][dt[2]] = data[dt[0]][dt[1]][dt[2]]
						else:
							if dt[3] not in log[dt[0]][dt[1]][dt[2]]:
								log[dt[0]][dt[1]][dt[2]][dt[3]] = data[dt[0]][dt[1]][dt[2]][dt[3]]
							else:
								log[dt[0]][dt[1]][dt[2]][dt[3]][dt[4]] = data[dt[0]][dt[1]][dt[2]][dt[3]][dt[4]]

			with open(self.jsonFileName, "w") as file:
				file.write(json.dumps(log))


	def snapshot(self, html, dtChecked):
		if self.saveSnapshot:
			snapDir = f"{self.snapshotDir}/{dtChecked.strftime('%Y-%m-%d')}/{dtChecked.strftime('%H')}"
		
		if not os.path.exists(snapDir):
			os.makedirs(snapDir)

		with open(snapDir + f"/{dtChecked.strftime('%M')}.html", "w") as file:
			file.write(html)
	
	#
	# MAIN FUNCS
	#

	def logIn(self):
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
			print("Loading took too much time!")


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
			print("Loading took too much time!")
		
		return dtChecked


	def checkForRooms(self):
		dtChecked = self.navigateToPage() # navigate to change rooms page and return dt checked
		html = self.br.page_source
		
		roomsAvailable = []

		try: # IF Rooms are available
			roomContainer = self.br.find_element_by_class_name("responsive-flow")
			roomsAvailable = roomContainer.find_elements_by_xpath("./*")
			print(
				f"{dtChecked.strftime('%Y-%m-%d %H:%M')} - {len(roomsAvailable)} ROOM(S) AVAILABLE:"
			)

			uniqueHalls = []
			roomsData = []

			for room in roomsAvailable: # Get info of each room available
				hall = room.find_element_by_class_name("title").text

				if hall not in uniqueHalls:
					uniqueHalls.append(hall)

				# Go to results info page
				button = room.find_element_by_class_name("ui-select-action")
				self.br.execute_script("arguments[0].click();", button)

				try: # Wait for page to finish loading
					element_present = EC.presence_of_element_located(
						(By.CLASS_NAME, "results-list")
					)
					WebDriverWait(self.br, self.timeout).until(element_present)
				except TimeoutException:
					print("Loading took too much time!")
				
				resContainer = self.br.find_element_by_class_name("results-list")
				result = resContainer.find_element_by_xpath("./*")

				roomNum = result.find_element_by_class_name("title").text
				wing = result.find_element_by_class_name("multiline").text.split("\n")[0]
				capacity = result.find_element_by_class_name("capacity").text.replace("\n", "").replace("\t", "").replace(" ", "")

				print((" " * 19) + f"+ {hall} - {roomNum} - {wing} - {capacity} beds")

				# Go to room info page
				infoLink = result.find_element_by_link_text("Show Room Info")
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
					print((" " * 21) + f"> {bed} - {name} - {gender} - {age}y")
					age = age if name == "Vacant" else int(age)
					occupants.append({
						"bed": bed,
						"name": name,
						"gender": gender,
						"age": age
					})

				roomsData.append({
					"hall": hall,
					"wing": wing,
					"roomNumber": roomNum,
					"capacity": int(capacity),
					"ocuppants": occupants
				})

				self.navigateToPage()

			self.postIFTTT(len(roomsAvailable), uniqueHalls, dtChecked) # Post to IFTTT
			self.logJSON(dtChecked, roomsData) # Save JSON log
		except NoSuchElementException: # Rooms are not available
			print(f"{dtChecked.strftime('%Y-%m-%d %H:%M')} - No rooms available yet")

		self.logCSV(dtChecked, len(roomsAvailable)) # Save CSV log
		self.snapshot(html, dtChecked) # Save HTML snapshot

		if self.checkPeriodically:
			time.sleep(self.sleepInterval) # Sleep
			self.checkForRooms() # Recursive


	def begin(self):
		self.logIn()
		self.checkForRooms()
