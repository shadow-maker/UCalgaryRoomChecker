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

## [Class specifications / documentation]("specs.md")

## IFTTT Integration
...