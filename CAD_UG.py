'''LA CAD Extraction script:

This script was developed for the purpose of conducting CAD Extractions on segments submitted to the GIS department
for the LA market. 
'''

#import necessary modules
import arcpy
import os
import datetime
import shutil 

#Arcmap Settings
arcpy.env.overwriteOutput = True 
arcpy.env.addOutputsToMap = False

# Start process...
starttime = datetime.datetime.now()

# Script input parameters:
csv_input = arcpy.GetParameterAsText (0)
single_input = arcpy.GetParameterAsText (1)

# Script output parameter location for geoprocessing results
user_output = arcpy.GetParameterAsText (2) 
existingDataPath = arcpy.GetParameterAsText (3)

# Check box to indicate if segments are being "re extracted"
reExtracted = arcpy.GetParameterAsText (4)

#makes a list of segments from a CSV file
csvList = []
if csv_input :
	fhand = open(csv_input)
	for i in fhand:
		i = i.rstrip()
		csvList.append(i)
	
#makes a list of segments from a single entry
singleList = []
if single_input :
	singleList = [single_input]
	
#makes a combined list from the CSV file and single entry	
if len(csvList) > 0 and len(singleList) > 0:
	listSegment = csvList + singleList
elif len(csvList) > 0 and len(singleList) == 0:
	listSegment = csvList
elif len(csvList) == 0 and len(singleList) > 0:
	listSegment = singleList

#Makes general CAD folder
os.chdir(user_output)
os.mkdir("CAD Extractions")

#Makes folder named with the date for all zipped segment file folders to be saved to 
time = datetime.datetime.now()
timeString = str(time.strftime("%m%d%Y" + "_Extractions"))
os.chdir("{0}\\{1}".format(user_output, "CAD Extractions"))
os.mkdir("{0}".format(timeString))

#Makes txt file to log errors
cadFolder = "{0}\\{1}".format(user_output, "CAD Extractions")
errorFile = 'errorReport.txt'
fullPath = "{0}\\{1}".format(cadFolder, errorFile)
f = open(fullPath,"w+")

f.write('--------------------' + '\n')
f.write('--------------------' + '\n')
f.write('Log: ' + str(starttime) + '\n')

#Logs total # of segments requested for extraction
f.write('\n')
f.write('Total segments requested for extraction: ' + str(len(listSegment)) + '\n')
f.write('\n')

#create variables for input feature classes
inFC1 = '{0}\\xxxxxx'.format(existingDataPath)
inFC2 = '{0}\\xxxxxx'.format(existingDataPath)
inFC3 = '{0}\\xxxxxx'.format(existingDataPath)

#create variables for SQL fieldnames
fieldName1 = "SEGMENT_"
fieldName2 = "LID_NAME"
fieldName3 = "Segment_Name"

#creating delimiters for SQL statements
delimField1 = arcpy.AddFieldDelimiters(inFC1, fieldName1)
delimField2 = arcpy.AddFieldDelimiters(inFC2, fieldName2)
delimField3 = arcpy.AddFieldDelimiters(inFC3, fieldName3)

#variables for City and County boundary layer feature classes
lyrCity = '{0}\\xxxxxx'.format(existingDataPath)
lyrCounty = '{0}\\xxxxxx'.format(existingDataPath)

#full list of layers to be clipped to segment buffer for delivery
inFCList = []

for item in listSegment:
	#applies change to segment folder name for re extractions
	if str(reExtracted) == 'true':
		
		#Makes time stamp for re extracted file naming
		segTime = datetime.datetime.now() 
		tString = str(segTime.strftime("%m%d%Y"))
		#Make folder for every segment you're doing re extraction for 
		os.chdir(cadFolder)
		os.mkdir('{0}_R_{1}'.format(item, tString))
		segFold = '{0}_R_{1}'.format(item, tString)
		folderPath = '{0}\\{1}'.format(cadFolder, segFold)
	else:
		#Make folder for every segment that you are doing CAD extraction for
		os.chdir(cadFolder)
		os.mkdir('{0}'.format(item))
		segFold = '{0}'.format(item)
		folderPath = '{0}\\{1}'.format(cadFolder,segFold)
	
	#set workspace to correct output folder
	targetWorkspace = "{0}\\{1}".format(cadFolder, segFold)
	arcpy.env.workspace = targetWorkspace 
	
	#Make feature layer from specified segment name from the following layers:  
	memFC1 = arcpy.FeatureClassToFeatureClass_conversion(inFC1, "in_memory", "HLD_seg", "{0}  = '{1}'".format(delimField1, item))
	
	#prints the segment name with '_'
	x=item.rstrip()
	x=item.replace(".","_")
	x=x.replace("-","_")
	HLD_SEG = arcpy.CopyFeatures_management(memFC1, '{0}'.format(x)) 
	if arcpy.management.GetCount(HLD_SEG)[0] == "0":
		f.write('ERROR: ' + '{0}'.format(item) + ' not in HLD Route' + '\n' )
		#this deletes the folder & all contents of empty segment
		shutil.rmtree(folderPath) 
		f.write('ATTN: ' + '{0}'.format(item) + ' segment folder has been deleted' + '\n')
		f.write('\n')
		arcpy.Delete_management(memFC1) 
		continue  
	else:
		arcpy.Delete_management(memFC1)


	memFC2 = arcpy.FeatureClassToFeatureClass_conversion(inFC2, "in_memory", "struct_tele", "{0}  = '{1}'".format(delimField2, item))
	struct = arcpy.CopyFeatures_management(memFC2, 'LA_Structure_Telecom') 
	arcpy.Delete_management(memFC2)

	
	memFC3 = arcpy.FeatureClassToFeatureClass_conversion(inFC3, "in_memory", "LLD_Notes_lyr", "{0}  = '{1}'".format(delimField3, item))
	LLD_notes = arcpy.CopyFeatures_management(memFC3, 'LA_LLD_Notes_Layer') 
	arcpy.Delete_management(memFC3)

	#Create 200ft buffer from MakeFeatureLayer output HLD_seg
	memClipFeature = arcpy.Buffer_analysis(HLD_SEG, "in_memory\\HLD_seg_buffer", "200 FEET", "", "", "ALL")
		
	###Start of city/county boundary clips###
	#City boundary clip
	memCityClip = arcpy.Clip_analysis(lyrCity, memClipFeature, "in_memory\\cityBoundary")
	lyrCityName = arcpy.da.SearchCursor(memCityClip, ['CITY_NAME'])
	listCityName = []
	for row in lyrCityName:
		listCityName.append(row[0])
		
	for city in listCityName:
		delimFieldCity = arcpy.AddFieldDelimiters(memCityClip, "CITY_NAME")
		cityProper = city.replace(" ","_")
		arcpy.Select_analysis(memCityClip, "{0}_CityBoundary".format(cityProper), "{0}  = '{1}'".format(delimFieldCity, city))
	
	#County boundary clip
	memCountyClip = arcpy.Clip_analysis(lyrCounty, memClipFeature, "in_memory\\countyBoundary")
	lyrCountyName = arcpy.da.SearchCursor(memCountyClip, ['NAME'])
	listCountyName = []
	for row in lyrCountyName:
		listCountyName.append(row[0])
		
	for county in listCountyName:
		delimFieldCounty = arcpy.AddFieldDelimiters(memCountyClip, "NAME")
		countyProper = county.replace(" ","_")
		arcpy.Select_analysis(memCountyClip, "{0}_CountyBoundary".format(countyProper), "{0}  = '{1}'".format(delimFieldCounty, county))
	###End city/county boundary clips###

	#fileCount variable created to be used as a counter in for loop to control flow
	#fileCount = len(inFCList)
	fileCount = 29
	
	#!!!counter for number of empty feature classes
	emptFC = 0
	
	#create loop that goes through all contents of inFClist and clips them 
	for FC in inFCList:
		
		#counter for control flow
		fileCount = fileCount - 1
		
		#Set workspaces and output file names
		inputFC = "{0}\\{1}".format(existingDataPath, FC)
		shortName = FC.split(".")[2]
		
		#construct output path 
		arcpy.env.workspace = targetWorkspace 
		outClipFeatureClass = "{0}_clip".format(shortName)		
		
		#for each feature class clip to the clip feature memClipFeature
		memClip = arcpy.Clip_analysis(inputFC, memClipFeature, "in_memory\\outClipFeatureClass")
		
		#need to copy from in_memory to folder to the desktop folder
		FCmem = arcpy.CopyFeatures_management(memClip, outClipFeatureClass)
		
		### keep log of number of feature classes that are empty...
		if arcpy.management.GetCount(FCmem)[0] == "0":
			emptFC += 1
		arcpy.Delete_management (memClip) 
		
		#counter used to determine if loop is completely finished and ready to move on on to CAD conversion 
		if fileCount == 0:
			arcpy.Delete_management(memClipFeature)			
			dwgShapefiles = arcpy.ListFeatureClasses()
			outCAD = arcpy.ExportCAD_conversion(dwgShapefiles, "DWG_R2013", "{0}.dwg".format(x),"IGNORE_FILENAMES_IN_TABLES", "APPEND_TO_EXISTING_FILES", "")
			#### ZIPFILE BELOW ####
			shutil.make_archive(segFold, 'zip', folderPath)
# End process...
endtime = datetime.datetime.now()

# Total feature classes in clip that are empty 
f.write('Total number of empty input feature classes: ' + str(emptFC) + '\n')
f.write('\n')

# Process Completed...
f.write('CAD extractions completed successfully in ' + str(endtime - starttime) + '\n') 
f.write("--------------------" + "\n")
f.write("--------------------" + "\n")

#!!! Close log file !!!#
f.close()
			
			
### EOlson 09/2018 ###
### rosemary.erin.o@gmail.com ###
