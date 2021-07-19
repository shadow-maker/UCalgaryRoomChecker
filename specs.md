# Class specifications

## Attributes

* `br`
  * Type: `selenium.webdriver`
  * Default: `webdriver.safari.webdriver.WebDriver()`
  * **Selenium webdriver object, responsible for controlling the browser window and performing the webscraping**

### Credentials

* `user`
  * Type: `str`
  * **Your UCalgary username**
* `pssw`
  * Type: `str`
  * **Your UCalgary password**
* `iftttKey`
  * Type: `str`
  * **Your unique IFTTT webhook key**

### URLS

* `loginURL`
  * Type: `str`
  * Default: `"https://cas.ucalgary.ca/cas/?service=https%3a%2f%2fucalgary.starrezhousing.com%2fStarRezPortalX%2fRedirectLogin%2fStarNet.StarRez.AuthProviders.CasSso"`
  * **URL of the log-in page of the UCalgary residence portal**
* `iftttPostURL`
  * Type: `str`
  * Default `"https://maker.ifttt.com/trigger/room_available/with/key/"`
  * **URL where to make IFTTT posts**

### Booleans

* `iftttPost`
  * Type: `bool`
  * Default: `True`
  * **Whether to make a POST to the IFTTT service**
* `logToCSV`
  * Type: `bool`
  * Default: `True`
  * **Whether to log in a CSV how many rooms where found every time the page is checked**
* `logToJson`
  * Type: `bool`
  * Default: `True`
  * **Whether to log in a JSON the information on the rooms found eveytime available rooms are found**
* `saveSnapshot`
  * Type: `bool`
  * Default: `True`
  * **Whether to save HTML snapshots of the change room page every time the page is checked**
* `checkPeriodically`
  * Type: `bool`
  * Default: `False`
  * **Whether to check for new rooms periodically and indefinetely**

### File names

* `csvFileName`
  * Type: `str`
  * Default: `"log.csv"`
  * **The name of the CSV file to log**
* `jsonFileName`
  * Type: `str`
  * Default: `"log.json"`
  * **The name of the JSON file to log**
* `snapshotDir`
  * Type: `str`
  * Default: `"snapshots"`
  * **The name of the directory where to save the snapshots**

### Time-related

* `timeout`
  * Type: `int`
  * Default: `30`
  * **Amount of seconds that will need to pass before a timeout exception occurs (if the page takes too long to respond)**
* `sleepInterval`
  * Type: `int`
  * Default: `300`
  * **Amount of seconds to wait between room checking intervals**

## Methods

* `__init__`
  * Parameters: `user` (`str`), `pssw` (`str`), `iftttKey=""` (`str`), `checkPeriodically=False` (`bool`)
  * **Constructs a new RoomChecker instance with the input parameters**

### Log

* `logCSV`
  * Parameters: `dtChecked` (`datetime.datetime`), `roomsAvailable` (`int`)
  * **Appends into `csvFileName` the ammount of rooms found at a given time**
* `logJSON`
  * Parameters: `dtChecked` (`datetime.datetime`), `roomsData` (`list`)
  * **Adds to `jsonFileName` (organized by datetime) the `roomsData` of the rooms found at a given time**
* `snapshot`
  * Parameters: `dtChecked` (`datetime.datetime`), `html` (`str`)
  * **Creates the necessary directories organized by datetime and creates a html file with snapshot data from a given time**
* `postIFTTT`
  * Parameters: `dtChecked` (`datetime.datetime`), `roomsAvailable` (`int`), `uniqueHalls` (`list`)
  * **Makes a POST request to the `iftttPostURL` with the `iftttKey` with a dictionary containg the `roomsAvailable`, `uniqueHalls` names, and the `dtChecked` as a string**

### Scraper methods

* `sleep`
  * Parameters: 
  * **Sleeps `sleepInterval` seconds, showing the seconds left with a progress bar in the console**
* `logIn`
  * Parameters: 
  * **Navigates to the log-in page and logs the user in if this isn't the case already**
  * **Closes pop-ups that open automatically when the user is logged in**
* `navigateToPage`
  * Parameters:
  * **Navigates to the room change page**
* `checkForRooms`
  * Parameters:
  * Runs `navigateToPage` and checks if rooms are shown available
  * **If available, scrapes the data from the needed sub-websites**
  * **Prints the general rooms info**
  * **Runs the necessary methods to log the general rooms info to CSV and JSON, save an HTML snapshot of the change rooms page, and make a post to the IFTTT service**
  * **Runs `sleep` and runs itself recursively if `checkPeriodically` is `True`**
* `begin`
  * Parameters:
  * **Runs `logIn` and `checkForRooms`**