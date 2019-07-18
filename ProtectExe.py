import sys
import os
import shutil
import subprocess
import argparse

#--------------------------  args parsing and setting --------------------------
parser= argparse.ArgumentParser()
parser.add_argument('-i','--inputFile', help=r'the file to be encrypted.',default=r'Y:\Release\Vision.exe')
parser.add_argument('-o','--outputFile',help=r'the output file after encryption.',default=r'Y:\Release\Vision.exe')
parser.add_argument('-a','--axProtectorExeFile',help=r'the codeMeter executable file. When running on teamCity, default value is the path from environment variable "AxProtectorExe", otherwise or cannot fine the file, we will use "X:\packages\Wibu.CodeMeter.AxProtector.6.80.0\tools"')
parser.add_argument('-d','--dryRun',help=r'just print log not really do the encrypition.',default=False,action="store_true")
parser.add_argument('-v','--verbose',help=r'verbose mode',default=False,action="store_true")

args = parser.parse_args()

if args.axProtectorExeFile:
	print("Use axProtectorExeFile seeting from command line : {}".format(args.axProtectorExeFile))
	AxProtectorPath = args.axProtectorExeFile
elif os.environ.get('TEAMCITY_VERSION') is not None:
	print("Running On team City")
	if os.environ.get('AxProtectorExe') is not None:
		AxProtectorPath=os.environ.get('AxProtectorExe')
		print("Use AxProtector path from teamCity : {}".format(AxProtectorPath))
	else:
		AxProtectorPath=r'X:\packages\Wibu.CodeMeter.AxProtector.6.80.0\tools\AxProtector.exe'
		print("Cannot Find AxProtector path from teamCity. Use default TeamCity AxProtector Path: {}".format(AxProtectorPath))
else:
	print("Not running on teamCity, Use Developer AxProtector Path setting")
	AxProtectorPath=r'C:\Program Files (x86)\WIBU-SYSTEMS\AxProtector\Devkit\bin\AxProtector.exe'
	if os.path.exists(AxProtectorPath) :
		print("Found : {}".format(AxProtectorPath))
	else:
		AxProtectorPath=r'X:\packages\Wibu.CodeMeter.AxProtector.6.80.0\tools\AxProtector.exe'
		if os.path.exists(AxProtectorPath) :
			print("Found : {}".format(AxProtectorPath))
		else:
			print("Cannot find AxProtector.exe. EXIT.")
			exit()

targetFile=args.inputFile
outputFile = args.outputFile
dryRun=args.dryRun
#--------------------------  End of args parsing and setting --------------------------

targetFilePrefix=os.path.splitext(targetFile)[0]
targetFileSurfix=os.path.splitext(targetFile)[1]
backupUnprotectedFile=targetFilePrefix + ".unprotected" + targetFileSurfix
protectedFile  =targetFilePrefix + ".protected" + targetFileSurfix

#-x      : Links the static library of the licensing system to the application to be protected.
#-kcm    : uses CmDongle (Default).
#
#-Fx     : Specifies the Firm Code(x) to be used.
#-Px     : Specifies the Product Code (x) to be used.
#-CFx    : Specifies the Feature Code (x) of the Feature Map to be used.
#-D:v    : Specifies the minimum driver version (v).
#-FW:v   : Defines the minimum firmware version(v).
#-SL     : Uses the local subsystem (local).
#-SLW    : Uses first the local subsystem (local), then the Wide Area Network subsystem (WAN).
#-NS     : station share: here several started applications on a client allocate only a single license.
#
#all 4 licenses: master/slave * spectrim/inVision
#-f6000434     : frim code    : 6000434     : Compac
#-p201000000   : product code : 0x201000000 : master
#-p201009999   : product code : 0x201009999 : slave
#-cf2147483648 : feature map  : ‭0x80000000‬  : spectrim
#-cf1073741824 : feature map  : ‭0x40000000‬  : inVision
compacFirmCode=r'-f6000434'
masterProductCode=r'-p201000000'
slaveProductCode=r'-p201009999'
spectrimFeatureCode=r'-cf2147483648'
inVisionFeatureCode=r'-cf1073741824'

masterSpectrimLicenseOption = r'-x -kcm' + " " + compacFirmCode + " " + masterProductCode + " " + spectrimFeatureCode + " -d:6.20 -fw:3.00 -sl -ns"
slaveSpectrimLicenseOption  = r'-x -kcm' + " " + compacFirmCode + " " + slaveProductCode  + " " + spectrimFeatureCode + " -d:6.20 -fw:3.00 -slw -ns"
masterInVisionLicenseOption = r'-x -kcm' + " " + compacFirmCode + " " + masterProductCode + " " + inVisionFeatureCode + " -d:6.20 -fw:3.00 -sl -ns"
slaveInVisionLicenseOption  = r'-x -kcm' + " " + compacFirmCode + " " + slaveProductCode  + " " + inVisionFeatureCode + " -d:6.20 -fw:3.00 -slw -ns"

encrpytOptions=""
#Option -CA[[A[l]],[Ct[,u]],[D[m]],[E],[G[l[,1]]],[L],[M],[R[t][,m]],[S[p]],[T[t][,u]],[V],[Z]] : Encrypts the executable file using automatic encryption.
#-CAA <l>    : Activates the security options (Advanced Protection Schemes, APS). <l> covers the options [0, 15]
#              Option Description
#              0 No resource encryption is performed.
#              1 Resource encryption applies (APS 1)
#              2 Static modification applies (APS 2)
#              4 Dynamic modification applies (APS 3)
#              8 Extended static modification applies (APS 4)
#              CAA6 applies APS 2 and 3
#              CAA7 applies  APS 1, 2 and 3
#              CAA13 applies APS 1, 4 and 8
#NOTE!!! Current Vision is NOT compatible with APS2, if using options like -caa2, -caa3, -caa6 or -caa7, we will get a crash when releasing std::shared_lock.
#        Reasons behind this is not clear, but we will avoid it by turnning off APS.
encrpytOptions= encrpytOptions + " -caa0"

#Option -CI[H][N][D] : Encrypts explicitly defined source code fragments within the executable file to be used with IxProtector.
#-CIH        : Defines that WupiXXX functions functions are NOT dynamically hooked
#-CIN        : Defines that no error messages are displayed when an error occurs.
#              -CIHN : WupiXXX functions are staticlly hooked and no error messages are displayed when an error occurs.
encrpytOptions= encrpytOptions + " -cihn"

#-CAE        : Activates instantly the detection that a has been removed from the PC ( plug-out ) (CmDongle only).
encrpytOptions= encrpytOptions + " -cae"
#-CAZ        : Saves the time when the encryption was performed within the protected application 
#             (CmContainer System Time. Then the application runs only when the PC time is older than this encryption time.
encrpytOptions= encrpytOptions + " -caz"
#-CACt<,u>   : Checks the CmContainer system time related to the PC time. 
#              A protected application runs only when the PC time in a time window is t minutes younger and, optionally, u minutes older than the CmContainer system time.
#              -cac15,15 means A protected application runs only when the PC time is less then 15 minutes ahead or after the CmContainer system time 
encrpytOptions= encrpytOptions + " -cac15,15"
#-CAV<level> : Adds a code integrity check to the automatically encrypted application or not. 
#            :    0 no integrity check.
#            :    1 adds a code integrity check to the automatically encrypted application.
#-CAV2       : Deactivates the code integrity check for an automatically encrypted application or for several executable files / libraries.
encrpytOptions= encrpytOptions + " -cav"
#-CAS<p>     : Specifies the size of the protected application to be encrypted. You enter the length, in percent, anywhere from 0 to 100%.The default setting is 75 percent.
encrpytOptions= encrpytOptions + " -cas100"
#-CAR<t>,<m> : Adds a runtime check to the automatic encryption. The check occurs every <t> seconds. <m> specifies how often the end-user is able to ignore a failed check.
#              -car60,3 means The check occurs every 60 seconds and end-user is able to ignore a failed check for 3 times
encrpytOptions= encrpytOptions + " -car60,3"

#-CAG<l>     : Activates Anti-Debugging mechanisms (Anti-Debugging-Checks, ADC).
#              <l> covers the options [0,367]
#              Option Description
#              1  Checks whether a debugger is attached to your application. In the case a debugger is detected, the application does not start (ADC1).
#              2  Checks additionally for Kernel debugger programs, e.g. "SoftICE". In the case a debugger is detected, the application does not start (ADC2).
#              4  Checks in an extended search for debugger programs running parallel to your applications. Cracker tools, such as IMPREC are detected. (ADC3).
#              8  Checks for all debugger programs. Then no debugger programs are allowed, i.e. also within developer environments (IDE), e.g. VISUAL STUDIO, DELPHI.(ADC4).
#              16 Locking of the license entry and thus of the hardware when a debugger program has been detected (ADC5).
#              32 Adds a mechanism to the application preventing the attachment of a debugger program to the application at runtime (generic debugger detection) (ADC6).
#              64 Detects whether the application is to be started in a virtual machine and prevents this (ADC7).
#              128 Hardware locking is performed only with a valid Firm Access Counter (only in combination with ADC5 and CmContainer).
#              256 Firm Access Counter decrementing by 1 is performed (only in combination with ADC5 and CmContainer).
#encrpytOptions= encrpytOptions + " -cag1"

#Option -W[C[t]]E[t]][P][U[c]] : Specifies the threshold of issued warnings.
#-WE[t] : Specifies the threshold <t> in days for the Expiration Time.
encrpytOptions= encrpytOptions + " -wu100"
#-WU[c] : Specifies the threshold <c> in units for the Unit Counter.
encrpytOptions= encrpytOptions + " -we30"

#Option -E[A(C|I|R)],[E(C|I|R)],[F],[M],[T],[U(S(C|R)[n]|R(C|R)[n]|I)]) : Defines additional checks while encryption and decryption operations are performed.
#-EAC   : Checks if the Product Item Option Activation Time exists.
encrpytOptions= encrpytOptions + " -eac"
#-EEC   : Checks if the Product Item Option Expiration Time exists.
encrpytOptions= encrpytOptions + " -eec"
#-EUSC1 : Activates an Unit Counter check and the counter decrementing by the specified value. (Checks and decrements at the start of the protected application only)
encrpytOptions= encrpytOptions + " -eusc1"
#-EMC   : Checks, if the Product Item Option Maintenance Period exists.
encrpytOptions= encrpytOptions + " -emc"

otherOptions=""
#-U[:FileName] : When specifying the FileName, the user-defined Message DLL holds the name FileNameXX.dll where XX stands for an optional country placeholder: Us, Sa, Cn,...
otherOptions = otherOptions + r' -u:"UserMsg64"'
#-V            : Activates the verbose mode.
otherOptions = otherOptions + r' -v'
#-#[File]      : Prints the logging to the specified [File]. This option exists next to automatic output to the AxProtector.log.[//Documents and Settings\user].
otherOptions = otherOptions + r' -#'

fileOptions=""
#-O[:FileName] : Specifies the path and the name of the encrypted destination file.
fileOptions = fileOptions + ' -o:"' + protectedFile + '" "' + targetFile+'"'


allOptions= masterSpectrimLicenseOption + " " + slaveSpectrimLicenseOption + " " + masterInVisionLicenseOption + " " + slaveInVisionLicenseOption 
allOptions= allOptions + " " + encrpytOptions + " " + otherOptions + " " + fileOptions

#'Y:\Release\Vision.exe' --> 'Y:\Release\Vision.unprotedted.exe'
print("Will backup from {} to {}".format(targetFile,backupUnprotectedFile))
if (dryRun == False) :
	if os.path.exists(backupUnprotectedFile):
		os.remove(backupUnprotectedFile)
	shutil.copy(targetFile,backupUnprotectedFile)

#encrypt 'Y:\Release\Vision.exe'
print("Will encrypt from {} to {}".format(targetFile,protectedFile))
if os.path.exists(protectedFile):
	os.remove(protectedFile)
cmd='"' + AxProtectorPath + '" ' + allOptions
print("cmd: {}".format(cmd))
if (dryRun == False) :
	#subprocess.call(cmd, shell=True)
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	o, e = proc.communicate()
	print('Output:      ' + o.decode('ascii'))
	#print('Error:      '  + e.decode('ascii'))
	print('returnCode: ' + str(proc.returncode))
	if(proc.returncode != 0):
		sys.exit()

#output file
print("Will copy from {} to {}".format(protectedFile,outputFile))
if (dryRun == False) :
	if os.path.exists(outputFile):
		os.remove(outputFile)
	shutil.copy(protectedFile,outputFile)


 
