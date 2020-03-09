#install wkhtmltopdf first.
import pdfkit
import urllib.request
import re
import os 
import PyPDF2
import pathlib

#options
baseUrlStr = r"https://firewalld.org/documentation/"
outputDirectory = r".\\output\\"
baseFileName = "index.pdf"
mergeAllPDF=True
outputName = "firewalld.pdf" #only generate this file when mergeAllPDF==True

#output directory
if(os.path.exists(outputDirectory) == False):
    print("Path : " + outputDirectory + " DIDN't exist, create it.")
    os.mkdir(outputDirectory)

#get every hierachey name of the base url path.
basrUrlHierachies = baseUrlStr.split('/')
while("" in basrUrlHierachies):
    basrUrlHierachies.remove("")

#get base html file
print ("Opening : " + baseUrlStr)
baseUrl = urllib.request.urlopen(baseUrlStr)
print ("result code: " + str(baseUrl.getcode()))
baseData = baseUrl.read()
baseHtmlLines = baseData.decode('utf-8').splitlines()
#print(baseHtmlLines)

#parse baseHtmlLines and get child html files --> ListOfUrlOutputFileName
ListOfUrlOutputFileName = list()
ListOfUrlOutputFileName.append([baseUrlStr,os.path.join(outputDirectory,baseFileName)])

for line in baseHtmlLines:
    if line.find(r'<a href=') != -1 and line.find(r'.html') != -1  and line:
        lineContentList = re.split('\"|\'',line)
        url = urllib.parse.urljoin(baseUrlStr,lineContentList[1])
        name = lineContentList[2].strip('>').rstrip('</a>')
        if(url.find(basrUrlHierachies[-1]) == -1): #url is NOT under current hierachey.
            continue
        urlHierachies = url.split("/")
        i = len(urlHierachies) -1
        while i >=0 :
            if urlHierachies[i] == basrUrlHierachies[-1] :
                break;
            else :
                i = i -1
        i = i+1
        outputFileName = outputDirectory
        while i < len(urlHierachies):
            outputFileName = os.path.join(outputFileName,urlHierachies[i])
            i = i +1
        outputFileName = outputFileName.rstrip(".html")
        outputFileName = outputFileName + ".pdf"
        #print("url : " + url + " name : " +name + " outputFileName : " + outputFileName)
        ListOfUrlOutputFileName.append([url,outputFileName])

#fetch all html files and convert them to pdf files
for line in ListOfUrlOutputFileName:
    #print(line)
    url = line[0]
    outputFileName = line[1]
    print("{}      ------>    {}".format(url,outputFileName))
    if os.path.isdir(os.path.dirname(outputFileName)) == False : #parent directory doesn't exist
        path = pathlib.Path(os.path.dirname(outputFileName))
        path.mkdir(parents=True, exist_ok=True)
        
    pdfkit.from_url(url, outputFileName)          

#write to merge result
if (mergeAllPDF == True):
    input_streams = []
    try:
        # First open all the files
        for line in ListOfUrlOutputFileName:
            url = line[0]
            inputFileName = line[1]
            input_streams.append(open(inputFileName, 'rb'))
        outputFileName = os.path.join(outputDirectory,outputName)
        print("Merge all pdf files to : " + outputFileName)
        output_stream = open(outputFileName,"wb")
        #  
        writer = PyPDF2.PdfFileWriter()
        for reader in map(PyPDF2.PdfFileReader, input_streams):
            for n in range(reader.getNumPages()):
                writer.addPage(reader.getPage(n))
        writer.write(output_stream)
        print("Merged successfully!")
    finally:
        for f in input_streams:
            f.close()
        output_stream.close()

