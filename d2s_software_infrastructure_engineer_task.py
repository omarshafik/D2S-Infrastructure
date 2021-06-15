import json
import argparse
from os import listdir, sep
from mysql.connector import (connection)
from d2s_software_infrastructure_engineer_task_definitions import *

# initialize database connection
with open("./db_credentials.json") as credentialsFile:
    credentials = json.load(credentialsFile)
cnx = connection.MySQLConnection(**credentials)
cursor = cnx.cursor()

# initialize argument parser
parser = argparse.ArgumentParser()
parser.add_argument("-o", "--Output", help = "Output directory (Default is current directory)")
parser.add_argument("-i", "--Input", help = "Input directory (Default is current directory)")
args = parser.parse_args()
inputDirectory = args.Input if args.Input else "./"
outputDirectory = args.Output if args.Output else ""

# loop over logs files in specified directory 
logFilesNames = [fileName.strip() for fileName in listdir(inputDirectory) if "log" in fileName.split(".")[-1]]
for logFileName in logFilesNames:
  # parse data as json object
  logFilePath = inputDirectory + logFileName
  workbenchData = getWorkbenchData(logFilePath)
  
  # save parsed logs to json file
  parsedFileName = outputDirectory + workbenchData['name'].split("/")[-1] + ".parsed.json"
  with open(parsedFileName, 'w') as outfile:
    json.dump(workbenchData, outfile)

  # save parsed logs to MySQL database
  testsData = workbenchData.pop('results')
  cursor.execute(addWorkbenchQuery, workbenchData)
  workbenchId = cursor.lastrowid
  print("=========================================================")
  print("Workbench saved with id: '", workbenchId, "'", sep="")
  print("=========================================================")
  for test in testsData:
    test['workbenchId'] = workbenchId
    cursor.execute(addTestQuery, test)
    testId = cursor.lastrowid
    print("Test saved with id: '", testId, "'", sep="")
  print("=========================================================")

  del workbenchData # release memory
