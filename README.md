# University of Calgary Room Checker

A Python script that scrapes the UCalgary residence portal to check if new rooms have opened up

## Features
* The script uses your personal credentials to log you into your residence portal via your web browser
* Navigates to the room change page and detects if rooms are available
* Prints to the console the available rooms' information, incluiding the general information of the current occupants
* Is able to make a POST to the [IFTTT](https://ifttt.com/home) service with the general information on the available rooms, so that you can create cool automations like receive a notification everytime a new room has opened up
* Is able to refresh the page periodically each given ammount of seconds (default is 300) to continue checking for rooms indefinetely

## Requirements
* IMPORTANT: Mac Safari is currently the only supported web browser
* A modern version of Python (tested on 3.8.2)
* Selenium for python
  * Install via pip: run the `pip install selenium` command in your terminal / command line

## How to use
### If you have used Python before...
* The file `roomChecker.py` contains the class `RoomChecker` which performs all the webscraping and contains the needed attributes
* To create an instance of this class use the following constructor format:
* `RoomChecker(user, pssw, iftttKey="", checkPeriodically=False)`
* Where:
  * `user`: (str) Your UCalgary username
  * `pssw`: (str) Your UCalgary password
  * `iftttKey`: (str) Your unique IFTTT webhook key
  * `checkPeriodically`: (bool) Whether you want the program to check for rooms periodically or not

### If you haven't used Python before...
* Clone this repository or download the `roomChecker.py` file, which contains the `RoomChecker` class
* From here there are two ways you can run the script:
  1. By running a separate Python file
    * Download the `main.py` file if you havent already, this contains everything you need to get you started
    * Open up your terminal / command line in the same directory as the `roomChecker.py` and `main.py` files
    * Run the file with the `python main.py` command (`python3 main.py` could work too)
    * You should be promted from the terminal to enter you requiered credentials, when this is done the program will start running.
  2. From the interactive interpreter
    * Open up your terminal / command line in the same directory as the `roomChecker.py` file
    * Run the `python` command (`python3` could work too)
    * Now your inside your interactive interpreter and you should see `>>>` at the begining of each line
    * Run `from roomChecker import RoomChecker` to import the class into the interpreter
    * Create an instance of `RoomChecker` by running the following:
    * `rc = RoomChecker(user, pssw, iftttKey, checkPeriodically)`
    * Where:
      * `user`: Your UCalgary username in quotes ""
      * `pssw`: Your UCalgary password in quotes ""
      * `iftttKey`: Your unique IFTTT webhook key in quotes "" (not required)
      * `checkPeriodically`: True or False, Whether you want the program to check for rooms periodically or not (not required, default is False)
    * By now blank browser window should have opened up
    * Run `rc.begin()` to begin checking for rooms

## Class specifications

### Attributes

* br (selenium.webdriver, default=webdriver.safari.webdriver.WebDriver())
  * Selenium webdriver object, responsible for controlling the browser window and performing the webscraping

#### Credentials

* `user` (str)
  * Your UCalgary username
* `pssw` (str)
  * Your UCalgary password
* `iftttKey` (str)
  * Your unique IFTTT webhook key

#### URLS

* `loginURL` (str, default="https://cas.ucalgary.ca/cas/?service=https%3a%2f%2fucalgary.starrezhousing.com%2fStarRezPortalX%2fRedirectLogin%2fStarNet.StarRez.AuthProviders.CasSso")
  * URL of the log-in page of the UCalgary residence portal
* `iftttPostURL` (str, default="https://maker.ifttt.com/trigger/room_available/with/key/")
  * URL where to make IFTTT posts

#### Booleans

* `iftttPost` (bool, default=True)
  * Whether to make a POST to the IFTTT service
* `logToCSV` (bool, default=True)
  * Whether to log in a CSV how many rooms where found every time the page is checked
* `logToJson` (bool, default=True)
  * Whether to log in a JSON the information on the rooms found eveytime available rooms are found
* `saveSnapshot` (bool, default=True)
  * Whether to save HTML snapshots of the change room page every time the page is checked
* `checkPeriodically` (bool, default=False)
  * Whether to check for new rooms periodically and indefinetely

#### File names

* `csvFileName` (str, default="log.csv")
  * The name of the CSV file to log
* `jsonFileName` (str, default="log.json")
  * The name of the JSON file to log
* `snapshotDir` (str, default="snapshots")
  * The name of the directory where to save the snapshots

#### Time-related

* `timeout` (int, default=30)
  * Amount of seconds that will need to pass before a timeout exception occurs (if the page takes too long to respond)
* `sleepInterval` (int, default=300)
  * Amount of seconds to wait between room checking intervals

### Methods

* `__init__`
  * Parameters: `user` (str), `pssw` (str), `iftttKey=""` (str), `checkPeriodically=False` (str)
  * Constructs a new RoomChecker instance with the input parameters

#### Log

* `logCSV`
  * Parameters: `dtChecked` (datetime.datetime), `roomsAvailable` (int)
  * Appends into `csvFileName` the ammount of rooms found at a given time
* `logJSON`
  * Parameters: `dtChecked` (datetime.datetime), `roomsData` (list)
  * Adds to `jsonFileName` (organized by datetime) the `roomsData` of the rooms found at a given time
* `snapshot`
  * Parameters: `dtChecked` (datetime.datetime), `html` (str)
  * Creates the necessary directories organized by datetime and creates a html file with snapshot data from a given time
* `postIFTTT`
  * Parameters: `dtChecked` (datetime.datetime), `roomsAvailable` (int), `uniqueHalls` (list)
  * Makes a POST request to the `iftttPostURL` with the `iftttKey` with a dictionary containg the `roomsAvailable`, `uniqueHalls` names, and the `dtChecked` as a string

#### Scraper methods

* `logIn`
  * Parameters: 
  * Navigates to the log-in page and logs the user in if this isn't the case already
  * Closes pop-ups that open automatically when the user is logged in
* `navigateToPage`
  * Parameters:
  * Navigates to the room change page
* `checkForRooms`
  * Parameters:
  * Runs `navigateToPage` and checks if rooms are shown available
  * If available, scrapes the data from the needed sub-websites
  * Prints the general rooms info
  * Runs the necessary methods to log the general rooms info to CSV and JSON, save an HTML snapshot of the change rooms page, and make a post to the IFTTT service
  * Waits `sleepInterval` and runs itself recursively if `checkPeriodically` is True
* `begin`
  * Parameters:
  * Runs `logIn` and `checkForRooms`

## IFTTT Integration
...