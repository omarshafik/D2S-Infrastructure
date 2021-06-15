import json
import argparse
from os import listdir, sep
from mysql.connector import (connection)
from d2s_software_infrastructure_engineer_task_definitions import *

cursor = None # cursor to use for database queries

# initialize argument parser
parser = argparse.ArgumentParser()

parseGroup = parser.add_argument_group('parse')
parseGroup.add_argument("-p", "--parse", help = "Parse logs to JSON files", action="store_true")
parseGroup.add_argument("-o", "--output", help = "Output directory (Default is current directory)")
parseGroup.add_argument("-i", "--input", help = "Input directory (Default is current directory)")
parseGroup.add_argument("-s", "--save", help = "Save parsed logs to MySQL database", action="store_true")


queryGroup = parser.add_argument_group('query')
queryGroup.add_argument("-q", "--query", help = "Query the data from database", action="store_true")
queryGroup.add_argument("--name", help = "Test name")
queryGroup.add_argument("--version", help = "Test version")
queryGroup.add_argument("--or", help = "Query the data from database using OR statement", action="store_true")

args = parser.parse_args()
shouldParse = args.parse
shouldSave = args.parse and args.save
shouldQuery = args.query

# initialize database connection when needed
if shouldQuery or shouldSave:
  with open("./db_credentials.json") as credentialsFile:
      credentials = json.load(credentialsFile)
  cnx = connection.MySQLConnection(**credentials)
  cursor = cnx.cursor()


if shouldParse:
  inputDirectory = args.input if args.input else "./"
  outputDirectory = args.output if args.output else ""

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

    if shouldSave and cursor:
      # save parsed logs to MySQL database
      testsData = workbenchData.pop('results')
      cursor.execute(checkWorkbenchIsSaved, (workbenchData['name'], workbenchData['version']))
      if len(cursor.fetchall()) > 0:
        raise Exception("Workbench already saved in database!")
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
    cnx.commit()
    del workbenchData # release memory

# search tests by (name and version) or by version only
if shouldQuery and cursor:
  name = "%" if not args.name else ("%" + args.name + "%")
  version = "%" if not args.version else ("%" + args.version + "%%")
  cursor.execute(searchTestQuery, (name, version))
  for (version, is_passed, reason, realtime) in cursor:
    print("Test found with "
    "version: ", version,
    ", isPassed: ", is_passed,
    ", reason: " + reason if not is_passed else "",
    ", realtime: ", realtime,
    sep="")
print("=========================================================")
print("Exited")
print("=========================================================")