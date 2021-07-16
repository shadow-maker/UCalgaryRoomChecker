from roomChecker import RoomChecker

user = input("Enter your UCalgary username: ")
pssw = input("Enter your UCalgary password: ")
iftttKey = input("Enter your IFTTT webhook key: ")
checkPeriodic = bool(input("Enter anything to check periodically"))

rc = RoomChecker(user, pssw, iftttKey, checkPeriodic) # Create RoomChecker instance
rc.begin() # Begin checking for rooms