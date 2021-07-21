# University of Calgary Room Checker

A Python script that scrapes the UCalgary residence portal to check if rooms are available

## Features
* The script uses your personal credentials to log you into your residence portal via your web browser
* Navigates to the room change page and detects if rooms are available
* Prints to the console the available rooms' information, incluiding the general information of the current occupants
* Is able to make a POST to the [IFTTT](https://ifttt.com/home) service with the general information on the available rooms, so that you can create cool automations like receive a notification everytime a new room has opened up (read [IFTT Integration](#ifttt-integration))
* Is able to refresh the page periodically each given ammount of seconds (default is 300) to continue checking for rooms indefinetely

## Requirements
* A supported browser: Chrome, Safari, or Firefox
* A webdriver for your chosen browser:
  * Safari: You don't need to download any additional webdriver
  * Chrome: Download the latest webdriver for Chrome from [https://sites.google.com/a/chromium.org/chromedriver/downloads](https://sites.google.com/a/chromium.org/chromedriver/downloads) and save it in the same directory as the Python program with the name `chromedriver`
  * Firefox: Download the latest webdriver for Firefox from [https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases) and save it in the same directory as the Python program with the name `geckodriver`
* A modern version of Python (tested on 3.8.2)
* Selenium for python
  * Install via pip: run the `pip install selenium` command in your terminal / command line

## [Class specifications / documentation](specs.md)

## How to use

Remember to meet all the [requirements][#requirements] before starting

### If you have used Python before...
* The file `roomChecker.py` contains the class `RoomChecker` which performs all the webscraping and contains the needed attributes
* To create an instance of this class use the following constructor format:
* `RoomChecker(user, pssw, iftttKey="", checkPeriodically=False)`
* Where:
  * `user`: (`str`) Your UCalgary username
  * `pssw`: (`str`) Your UCalgary password
  * `iftttKey`: (`str`) Your unique IFTTT webhook key
  * `browser`: (`str`) Your chosen browser, has to be "C" for Chrome, "S" for Safari, or "F" for Firefox
  * `checkPeriodically`: (`bool`) Whether you want the program to check for rooms periodically or not

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
    * `rc = RoomChecker(user, pssw, iftttKey, browser, checkPeriodically)`
    * Where:
      * `user`: Your UCalgary username in quotes ""
      * `pssw`: Your UCalgary password in quotes ""
      * `iftttKey`: Your unique IFTTT webhook key in quotes "" (not required)
      * `browser`: Your chosen browser `"C"` (Chrome), `"S"` (Safari), or `"F"` (Firefox) (not required, default is `"C"`)
      * `checkPeriodically`: `True` or `False`, Whether you want the program to check for rooms periodically or not (not required, default is `False`)
    * By now blank browser window should have opened up
    * Run `rc.begin()` to begin checking for rooms

## IFTTT Integration
RoomChecker is able to make a POST to the [IFTTT](https://ifttt.com/home) service with the general information on the available rooms, so that you can create cool automations like receive a notification everytime a new room has opened up

### How to use

1. Create an [IFTTT](https://ifttt.com/home) account
2. Visit [https://ifttt.com/maker_webhooks](https://ifttt.com/maker_webhooks) and click on `Documentation`
3. Copy your IFTTT key and keep it in a safe place, you'll input the key when using the program
4. Now you can [create a new automation](https://ifttt.com/create) where the trigger is Webhooks / receive a web request and the event name is `room_available`
5. Now you can add whatever applet you want that will act uppon the web request, where the special "ingredients" are as follows:

### Ingredients

* When the program makes a POST to the IFTTT service, a dictionary is sent with the message containing the following data:
  * `Value1`: The amount of rooms available
  * `Value2`: The halls in which rooms where found
  * `Value3`: The date-time when rooms where checked
* You can use these values as "ingredients" inside your automation applet

### My recommendation
* This is the applet that I personally use for my IFTTT automation with my cellphone:
  * **Applet name:** "Send a rich notification from the IFTTT app"
  * **Message:** "`Value1` room(s) available for residence in `Value2`. Checked: `Value3`"
  * **Title:** "ROOM AVAILABLE"
  * **Link URL:** "https://cas.ucalgary.ca/cas/?service=https%3a%2f%2fucalgary.starrezhousing.com%2fStarRezPortalX%2fRedirectLogin%2fStarNet.StarRez.AuthProviders.CasSso"
  * **Image URL:** "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRebQm9jhY-_t2cahGJZE2d1igodtpS8hLyTQ&usqp=CAU"