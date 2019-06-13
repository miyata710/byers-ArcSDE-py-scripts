'''This is the code that has been used to go through and assess the WestCoast SDE. Various block of code have been
written to perform tasks and are detailed below.'''

'''Script / code block to take all LA feature classes and tables from the SDE connection and copy to a 
file GDB to be used for the data dictionary'''
#import arcpy module
import arcpy
arcpy.env.overwriteOutput = True 
arcpy.env.addOutputsToMap = False

####GeoDatabase / SDE connections###
sdeConnection = 
#GDB made on my personal connection to house all the LA data for the data dictionary
fileGeoDatabase = 

#Set workspace 
arcpy.env.workspace = sdeConnection
#List all items in workspace that fit wildcard
fcList = arcpy.ListFeatureClasses()
tableList = arcpy.ListTables()

####Loop through list  of feature classes and copy/paste to new GDB
for i in fcList:
	result = i.startswith("WestCoast.LAADMIN")
	print result
	if result == True:
		in_features = i
		out_features = '{0}\{1}'.format(fileGeoDatabase, i)
		arcpy.CopyFeatures_management(i, out_features)
	else:
		continue

###Loop through list of tables and copy/paste to new GDB
for i in tableList:
	result = i.startswith("WestCoast.LAADMIN")
	print result
	if result == True:
		in_features = i
		out_features = '{0}\{1}'.format(fileGeoDatabase, i)
		arcpy.CopyFeatures_management(i, out_features)
	else:
		continue	
		
'''Code block to make a list of feature classes with empty attributes tables'''
#Set local variable to GDB 
fileGeoDatabase = 
#Set workspace
arcpy.env.workspace = fileGeoDatabase
#Create a list of all FC in GDB
dataList = arcpy.ListFeatureClasses()
#Empty list variable 
emptyList = []
#Loop through every FC. If a FC has an empty attributes table, 
#it is appended to the emptyList variable and the length of the list
#as well as the FC in the list are printed.
for i in dataList:
	if arcpy.management.GetCount(i)[0] == "0":
		emptyList.append(i)
		print i
print len(emptyList)
print emptyList
#!cutList is the list of input FC for LA CAD tool w/o empty FCs
cutList = []

 '''Code block to make a list of feature classes based on the number of attributes in tables'''
#Set local variable to GDB 
fileGeoDatabase = 
#Set workspace
arcpy.env.workspace = fileGeoDatabase
#Create a list of all FC in GDB
dataList = arcpy.ListFeatureClasses()
#
#Loop through every FC. Use the arcpy GetCount method to get the total number of rows in attribute table. 
#make nested dictionary with the FC name as the key and the total number of rows as the value! 
for i in dataList:
	arcpy.management.GetCount(i)[0]
 
'''Code block to print names of all FCs with attribute data'''
#Set local variable to GDB 
fileGeoDatabase = 
#Set workspace
arcpy.env.workspace = fileGeoDatabase
#Create a list of all FC in GDB
dataList = arcpy.ListFeatureClasses()
#Empty list variable 
emptyList = []
#Loop through every FC. If a FC has values in the attributes table, 
#it is appended to the emptyList variable and the length of the list
#as well as the FC in the list are printed.
for i in dataList:
	if arcpy.management.GetCount(i)[0] != "0":
		emptyList.append(i)
		print i
print len(emptyList)
print emptyList
	
'''Code block to make a list of tables with empty attributes tables'''
#Set local variable to GDB 	
fileGeoDatabase = 
#Set workspace
arcpy.env.workspace = fileGeoDatabase
#Create a list of all tables in GDB
dataList = arcpy.ListTables()
#Empty list variable
emptyList = []
#Loop through every table. If a table has an empty attributes table, 
#it is appended to the emptyList variable and the length of the list
#as well as the tables in the list are printed.
for i in dataList:
	if arcpy.management.GetCount(i)[0] == "0":
		emptyList.append(i)
print len(emptyList)
print emptyList

'''Code block to print name of each table in GDB'''
#Set local variable to GDB 	
fileGeoDatabase = 
#Set workspace
arcpy.env.workspace = fileGeoDatabase
#Create a list of all tables in GDB
dataList = arcpy.ListTables()
#Loop through every table and print its name
for i in dataList:
	print i
	
'''Code bloack to take list of all FC on AGOL and that have attribute data and append to a list. This is 
done so that we can assess which FC are actively edited by Engineers on the platform and which ones
are not edited'''
#import module
import os

#Arcmap Settings
arcpy.env.overwriteOutput = True 
arcpy.env.addOutputsToMap = False

#Set local variable to GDB 	
fileGeoDatabase = 
csv_input = 

#Set workspaces
arcpy.env.workspace = fileGeoDatabase

#access file and make list of FC names that fit requirements stated above.
listFC = []
fhand = open(csv_input)
for i in fhand:
	i = i.rstrip()
	listFC.append(i)
print listFC

for item in listFC:
	in_data = "{0}\\{1}".format(fileGeoDatabase, item)
	out_dataset = in_data + "_Sorted"
	sorting = arcpy.Sort_management(in_data, out_dataset, [["last_edited_date", "DESCENDING"]])
	#!cursor = arcpy.da.SearchCursor(out_dataset, ["last_edited_date"])
	value = arcpy.da.SearchCursor(out_dataset, ["last_edited_date"]).next()[0]
	#!print cursor[0]
	print item + "_" + str(value)


#Set local variable to GDB 
fileGeoDatabase = 
#Set workspace
arcpy.env.workspace = fileGeoDatabase
#Create a list of all FC in GDB
dataList = arcpy.ListFeatureClasses()
#Loop through every FC. If a FC has values in the attributes table, 
#it is appended to the emptyList variable and the length of the list
#as well as the FC in the list are printed.
for i in dataList:
	count = arcpy.management.GetCount(i)[0]
	print i + " " + count 
	

### EOlson 11/2018 ###
### rosemary.erin.o@gmail.com ###
