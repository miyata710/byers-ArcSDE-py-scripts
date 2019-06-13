'''Transmedia Delivery Script:

This script is being developed in order to help streamline Transmedia deliveries to EA.
'''

import arcpy 
import os
import datetime 

#Arcmap Settings
arcpy.env.overwriteOutput = True 
arcpy.env.addOutputsToMap = False

#Script input parameters

#NFID for transmedia delivery
NFID = arcpy.GetParameterAsText (0)

#Excel sheet for HLD Route join
excelSheet = arcpy.GetParameterAsText (1)

#Output folder path
folderPath = arcpy.GetParameterAsText (2)

#Database Connection
existingDataPath = arcpy.GetParameterAsText (3) 

#Path to FC template in West Coast GDB
templatePath = '{0}\\xxxxxx'.format(existingDataPath)

#Path to HLD Route
HLDroute = '{0}\\xxxxxx'.format(existingDataPath)

#Variable to store proper SQL expression
expressionSQL = "NF_ID = '{0}'".format(NFID)

#Select input NFID and use in SQL expression to export HLD Route
HLDexport = arcpy.Select_analysis(HLDroute, "in_memory\\HLDexport" , expressionSQL)

#Make lyr file for table join
HLDlyr = arcpy.MakeFeatureLayer_management(HLDexport, "in_memory\\HLDlyr")

#Excel to Table
myTable = arcpy.ExcelToTable_conversion(excelSheet, "in_memory\\myTable")

#Join
joined = arcpy.AddJoin_management(HLDlyr, "SEGMENT_", myTable, "Segment_Name", "KEEP_COMMON")

#copy the FC stored in the joined variable and export to its own FC
newFC = arcpy.CopyFeatures_management(joined, "in_memory\\newFC")

#Apply correct projection to HLDexport
HLDproject = arcpy.Project_management(newFC, "HLDproject", 
"PROJCS['NAD_1983_StatePlane_California_V_FIPS_0405_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',6561666.666666666],PARAMETER['False_Northing',1640416.666666667],PARAMETER['Central_Meridian',-118.0],PARAMETER['Standard_Parallel_1',34.03333333333333],PARAMETER['Standard_Parallel_2',35.46666666666667],PARAMETER['Latitude_Of_Origin',33.5],UNIT['Foot_US',0.3048006096012192]]", 
"WGS_1984_(ITRF00)_To_NAD_1983", 
"PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", 
"NO_PRESERVE_SHAPE", "", "NO_VERTICAL")

dataPath = HLDproject

#Fields in HLD Route needed for calculating new fields and formatting
calcList = ["HLDexport_SEGMENT_","HLDexport_HUB","HLDexport_ROUTETYPE","HLDexport_FIBERSIZE","HLDexport_NETWORKTYPE","HLDexport_NF_ID",
"myTable_DYEA_permit_number","myTable_Site_name","SHAPE@"]

# New fields for delivery
newList = ['none',"HUB","Type_Name", "NumberOfFibers","Network_Type","Cluster_Ring_NFID","Site_Span_NFID",
"Permits", "WorkOrderID","SHAPE@"]

#Search cursor to retrieve necessary records from table
cursor = arcpy.da.SearchCursor(dataPath, calcList)

#Empty dictionary to write to
myDict = {}												
permDict = {}											
woDict = {}												
useWO =  {}												

#for loop to create nested dictionary w/segment name & permit as key & cursor row as values
#also edits entries so they are calculated/formatted properly
for row in cursor:
	# collect permit numbers for each segment
	seg = row[0]
	perm = row[6]
	dKey = "{0}, {1}".format(seg, perm)					
	myDict [dKey] = {}									 
	if seg not in permDict :							
		permDict[seg] = [perm]							 
	else :
														
		myList = permDict[seg]	   
											
		myList.append(perm)								
											
		permDict[seg] = myList							
		
	#Calculate and format Type_Name field
	typeName = row[2]
	typeName = typeName.replace("New Underground", "BURIED")
	typeName = typeName.replace("New Aerial", "AERIAL")
	#Calculate and format NumberofFibers field
	fibers = row[3]
	#Calculate and format Network_Type field
	networkType = row[4]
	networkType = networkType.replace("Lateral", "Fronthaul")
	#Calculate and format Cluster_Ring_NFID field
	cluster = row[5]
	cluster = cluster[:-4]
	#Calculate and format Site_Span_NFID field
	siteSpan = row[5]
	#Calculate and format WorkOrderID field
	workID = "LSA_N_{}_{}_LLD".format(row[5],row[7])
	workID = workID.replace(".","_")
	workID = workID.replace("-","_")
	workID = workID.replace(" ","_")
	###Now we can populate the empty dictionary with the new values###
	myDict [dKey][newList[2]] = typeName				
										 
	myDict [dKey][newList[3]] = fibers					
	
	myDict [dKey][newList[4]] = networkType
	
	myDict [dKey][newList[5]] = cluster
	
	myDict [dKey][newList[6]] = siteSpan
	
	myDict [dKey][newList[8]] = workID
	
	#HUB
	myDict [dKey][newList[1]] = row[1]
	
	#SHAPE@
	myDict [dKey][newList[9]] = row[8]
	
	# count fronthaul segments for each workorder
	if networkType == 'Fronthaul' :						
		if workID in woDict :							
			
			woDict[workID] = woDict[workID] + 1			
			
			useWO[workID] = "yes"						
										 
		else :
			woDict[workID] = 1
			useWO[workID] = "no"						
	
#always delete cursor after you're done
del cursor 

###Now these new values/dictionary(s) can be used to populate the template FC###

###create folder and GDB for Transmedia deliverable###

#create datetime object for folder naming
time = datetime.datetime.now()
timeString = str(time.strftime("%m%d%Y"))

#Make folder for Transmedia delivery 
os.chdir(folderPath)
os.mkdir('{0}_Transmedia_{1}'.format(siteSpan, timeString))

transmediaFolder = '{0}\\{1}_Transmedia_{2}'.format(folderPath, siteSpan, timeString)

#Create file GDB and set as workspace
arcpy.CreateFileGDB_management (transmediaFolder, 'Sub_Transmedia_{0}'.format(timeString))
newGDB = r'{0}\Sub_Transmedia_{1}.gdb'.format(transmediaFolder, timeString)

arcpy.env.workspace = newGDB 

#Copy and export to new FC in corresponding GDB
arcpy.FeatureClassToFeatureClass_conversion(templatePath, newGDB, "Sub_Transmedia")
#list of fields in template FC
FCfields = ["SHAPE@","Type_Name", "NumberOfFibers", "Network_Type", "Cluster_Ring_NFID", "Site_Span_NFID", 
"Permits", "WorkOrderID","Segment_", "HUB", "SHAPE_Length"]

#use update cursor and for loop to iterate over records and input into new FC
insertCursor = arcpy.da.InsertCursor("Sub_Transmedia", FCfields)

#To control "Fronthaul" WO naming
woDict[workID] = woDict[workID] - 1

for segment in myDict:
	geometry = myDict[segment]["SHAPE@"]					
	geo = geometry.length									
	permKey = segment.split(",")[0]							 
	permits = ",".join(permDict[permKey])					
	# check for multiple fronthaul segs in workorder
	wo = myDict[segment]["WorkOrderID"]						
	if myDict[segment]["Network_Type"] == "Fronthaul" and useWO[wo] == "yes" :	
		if woDict[wo] > 9 :
			newWO = wo[:-3] + "{0}_".format(woDict[wo]) + wo[-3:]	
		elif woDict[wo] == 0 :
			newWO = wo												
		else :
			newWO = wo[:-3] + "0{0}_".format(woDict[wo]) + wo[-3:] 
		woDict[wo] = woDict[wo] - 1							
	else :
		newWO = wo											
	# create new row using list
	nRow = [myDict[segment]["SHAPE@"],						
	 myDict[segment]["Type_Name"],							
	 myDict[segment]["NumberOfFibers"],
	 myDict[segment]["Network_Type"],
	 myDict[segment]["Cluster_Ring_NFID"],
	 myDict[segment]["Site_Span_NFID"],
	 permits,
	 newWO,
	 permKey,
	 myDict[segment]["HUB"],
	 geometry.length]
	#use insert cursor to populate new row in FC
	insertCursor.insertRow(nRow)
del insertCursor


### EOlson 12/2018 ###
### rosemary.erin.o@gmail.com ###
