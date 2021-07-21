from roomChecker import RoomChecker

user = input(">Enter your UCalgary username: ")
pssw = input(">Enter your UCalgary password: ")
iftttKey = input(">Enter your IFTTT webhook key (or leave empty): ")
browser = input(">Enter 'C' for Chrome, 'S' for Safari, or 'F' for Firefox: ")
checkPeriodic = bool(input(">Enter anything to check periodically"))

# Create RoomChecker instance
rc = RoomChecker(user, pssw, iftttKey, browser, checkPeriodic)
rc.begin() # Begin checking for rooms