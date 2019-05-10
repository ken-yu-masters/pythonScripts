import winreg
import easygui
import sys

#https://docs.python.org/3/library/winreg.html
def createNewRegValueIfNoExist(regRoot,regKeyPathName,regValueName,newType,newValue):
	try:
		print ("Try to set {0}/{1} to {2}".format(regKeyPathName,regValueName,newValue))
		key = winreg.OpenKey(regRoot,regKeyPathName,0,winreg.KEY_READ)
		regValue,regType = winreg.QueryValueEx(key,regValueName)
		winreg.CloseKey(key)
		if (regType == newType or regValue == value):
			print ("The registry is alreay there.")
			return 0
		else:
			print ("create New ...")
	except OSError:
		print ("create New ...")
	
	try:
		key = winreg.OpenKey(regRoot,regKeyPathName,0,winreg.KEY_ALL_ACCESS)
		winreg.SetValueEx(key,regValueName,0,newType,newValue)
		winreg.CloseKey(key)
		return 1
	except OSError:
		print ("Need run from Administrator account")
		input("Press Enter to continue...")
		return -1
	
	
#https://community.spiceworks.com/topic/306159-mapped-network-drives-not-showing-in-application
regRoot = winreg.HKEY_LOCAL_MACHINE
regKeyPathName = "SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
regValueName   = "EnableLinkedConnections"
newType = winreg.REG_DWORD
newValue = 1

result = createNewRegValueIfNoExist(regRoot,regKeyPathName,regValueName,newType,newValue)
if(result == -1):
	easygui.msgbox("FAILED to set {0}/{1} to {2}".format(regKeyPathName,regValueName,newValue),"Modify Registry Failed!")
	sys.exit()
	
#https://community.spiceworks.com/topic/371685-user-can-t-access-mapped-network-drive
regRoot = winreg.HKEY_LOCAL_MACHINE
regKeyPathName = "SYSTEM\CurrentControlSet\Services\Mup\Parameters"
regValueName   = "EnableDfsLoopbackTargets"
newValue = 1
newType = winreg.REG_DWORD

result = createNewRegValueIfNoExist(regRoot,regKeyPathName,regValueName,newType,newValue)
if(result == -1):
	easygui.msgbox("FAILED to set {0}/{1} to {2}".format(regKeyPathName,regValueName,newValue),"Modify Registry Failed!")
	sys.exit()

if(result ==1):
	easygui.msgbox("You need to restart windows to make the registry modification effective!","Restart!!")
