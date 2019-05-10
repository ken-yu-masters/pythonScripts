import os
from xml.etree import ElementTree as et
import easygui

os.chdir('S:\\Vision\\Source\\VisionTesting\\')

currentPath = os.getcwd()

workDir = 'C:\\VisionTestingWorkingDirectory\\'
message = 'Choose the directory as working Directory for testing'
Title = None
workDir = easygui.diropenbox(message,Title,workDir)
if(workDir is not None and os.path.isdir(workDir)):
	print("workDir : {0}".format(workDir))
else:
	workDir = 'C:\\VisionTestingWorkingDirectory\\'
	easygui.msgbox("Input directory is Invalid, use the default value :" + workDir,"Input directory is Invalid")
	if(os.path.isdir(workDir) == False):
		os.mkdir(workDir)

OriginalVisionExeDir = 'Y:\\Release_Developer\\'
OriginalVisionExeDir = easygui.diropenbox("Choose the directory stores 'vision.exe' which need be tested.", None,OriginalVisionExeDir)
if(OriginalVisionExeDir is not None and os.path.isdir(OriginalVisionExeDir)):
	print("OriginalVisionExeDir : {0}".format(OriginalVisionExeDir))
else:
	OriginalVisionExeDir = 'Y:\\Release_Developer\\'
	easygui.msgbox("Input directory is Invalid, use the default value :" + OriginalVisionExeDir,"Input directory is Invalid")

modifyCount = 0;
for root, directory, files in os.walk(currentPath):
	for file in files:
		if (file == "Configuration.xml"):
			fullName = os.path.join(root,file)
			print(fullName)

			changed = False
			tree = et.parse(fullName)
			root = tree.getroot()
			
			element = root.find('Environment/Path/Working')
			if (element is None):
				print('   Cannot find Working directory setting')
			elif (element.text == workDir):
				print('   Same Working directory setting, SKIP.')
			else:
				print('   Replace Working directory setting with : {0}'.format(workDir))
				element.text = workDir
				changed = True
				
			element = root.find('Environment/Path/Clean')
			if (element is None):
				print('   Cannot find clean directory setting')
			elif (element.text == OriginalVisionExeDir):
				print('   Same OriginalVisionExeDir directory setting, SKIP.')
			else:
				print('   Replace Clean directory setting with : {0}'.format(OriginalVisionExeDir))
				element.text = OriginalVisionExeDir
				changed = True
			if (changed):
				tree.write(fullName)
				modifyCount = modifyCount +1
				
Mesasge = "Total Modified {0} files.".format(modifyCount)
Title = "Replacing finished"
#input("Press Enter to continue...")
easygui.msgbox(Mesasge,Title)