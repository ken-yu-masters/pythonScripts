#if you don't have any of following modules, just use pip install moduleName.
#for example : type : "pip install pyodbc" in the IPython command line.
import pyodbc
import csv
import os
import time
import shutil
import openpyxl
import easygui

def convertByteToString (input):
	if(isinstance(input,bytes)):
		return input.decode('utf-8','backslashreplace')
	return input

def addExtrabackslash (input):
	if(isinstance(input,str)):
		return input.encode('unicode_escape').decode('utf-8')
	return input

def convertAccessDataBaseToFiles(inputMDBFile,outputFormat = 'csv', driver = '{Microsoft Access Driver (*.mdb, *.accdb)}',password = ''):
	if(outputFormat != 'csv' and outputFormat != "xlsx") :
		print('Supprted output format is : csv or xlsx, cannot support : {}'.format(outputFormat))
		return
	#output to same directory
	outputPath = os.path.dirname(inputMDBFile)
	dataBaseName = os.path.splitext(os.path.basename(inputMDBFile))[0]
	outputPath = os.path.join(outputPath,dataBaseName)
	print("output to {}",outputPath)
	if (os.path.exists(outputPath) and os.path.isdir(outputPath)):
		shutil.rmtree(outputPath)
	time.sleep(.0000000000000001)
	os.mkdir(outputPath)
	#if the connection failed, you need install Microsoft MDB ODBC driver
	#https://www.microsoft.com/en-us/download/details.aspx?id=13255
	conn = pyodbc.connect('DRIVER={};DBQ={};PWD={}'.format(driver,inputMDBFile,password))
	curs = conn.cursor()
	tableNames = [x[2] for x in curs.tables().fetchall() if x[3] == 'TABLE']
	for tableName in tableNames:
		SQL = 'SELECT * FROM "{}"'.format(tableName)
		#debug:
		#print(SQL)
		curs.execute(SQL)
		#
		columns = [column[0] for column in curs.description]
		rows = curs.fetchall()
		#write to output files
		outputFileName = tableName + '.' + outputFormat
		outputFileName = os.path.join(outputPath,outputFileName)
		print('   generating {}'.format(outputFileName))
		if(outputFormat == 'csv') :
			csv_writer = csv.writer(open(outputFileName, 'w'), lineterminator='\n')
			csv_writer.writerow(columns)
			for row in rows:
				csv_writer.writerow(row)
		elif (outputFormat == 'xlsx'):
			wb = openpyxl.workbook.Workbook();
			worksheet = wb.active
			#debug:
			#print(columns)
			worksheet.append(columns)
			for row in rows:
				#debug:
				#print(row)
				#rowAsList = [convertByteToString(x) for x in row]
				rowAsList = [addExtrabackslash(convertByteToString(x)) for x in row]
				#print(rowAsList)
				worksheet.append(rowAsList)
			wb.save(outputFileName)
	curs.close()
	conn.close()

targetFileName = easygui.fileopenbox("Open .mdb file to convert","test")
if(os.path.splitext(targetFileName)[1] != ".mdb"):
	easygui.msgbox("Only support converting Microsoft Access file to Excel file or cvs file")
else:
	easygui.msgbox("Output to directory : {}".format(os.path.dirname(targetFileName)) )
	convertAccessDataBaseToFiles(targetFileName,'xlsx')

#test
#MDB = 'U:\\Vision\\TestFiles\\CalibrationTests\\CherryMachine_CIRIR_Synced_1_Lane\\Config\\Node1\\Backup\\04_29_2019_11_04\\VConfig.mdb'
#convertAccessDataBaseToFiles(MDB,'xlsx')
#MDB = 'U:\\Vision\\TestFiles\\CalibrationTests\\CherryMachine_CIRIR_Synced_1_Lane\\Config\\Node1\\Backup\\04_29_2019_11_04\\VTypes.mdb'
#convertAccessDataBaseToFiles(MDB,'xlsx')
#MDB = 'U:\\Vision\\TestFiles\\CalibrationTests\\CherryMachine_CIRIR_Synced_1_Lane\\Config\\Node1\\Backup\\04_29_2019_11_04\\VUser.mdb'
#convertAccessDataBaseToFiles(MDB,'xlsx')
