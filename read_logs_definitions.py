import argparse
import datetime
import json
from os import listdir, sep, getpid

import matplotlib.pyplot as plt
import numpy as np
import pandas
from mysql.connector import connection

addWorkbenchQuery = (
  "INSERT INTO WORKBENCH "
  "(name, directory, date, version, total_runtime, clock_time) "
  "VALUES (%(name)s, %(directory)s, STR_TO_DATE(%(date)s, '%m/%d/%Y %r'), %(version)s, %(totalRuntime)s, %(clockTime)s)"
)

addTestQuery = (
  "INSERT INTO TEST "
  "(wb_id, name, is_passed, reason, realtime) "
  "VALUES (%(workbenchId)s, %(name)s, %(isPassed)s, %(reason)s, %(realtime)s)"
)

updateWorkbenchPassFailCount = (
  "UPDATE WORKBENCH w SET "
  "w.passed_tests_num = (SELECT COUNT(*) FROM TEST t WHERE w.wb_id=t.wb_id AND is_passed IS TRUE), "
  "w.failed_tests_num = (SELECT COUNT(*) FROM TEST t WHERE w.wb_id=t.wb_id AND is_passed IS FALSE) "
  "WHERE w.wb_id = %s"
)

checkWorkbenchIsSaved = (
  "SELECT COUNT(*) FROM WORKBENCH "
  "WHERE name = %s AND version = %s"
)

searchTestQuery = (
  "SELECT t.name, w.version, t.is_passed, t.reason, t.realtime FROM WORKBENCH w "
  "LEFT OUTER JOIN TEST t ON t.wb_id = w.wb_id "
  "WHERE t.name LIKE %s "
  "AND w.version LIKE %s "
)

getWorkbenchDataForDisplay = (
  "SELECT name, version, date, passed_tests_num, failed_tests_num "
  "FROM WORKBENCH"
)

def getTestResults(resultsLines):
  testResults = []
  isPassed = False
  for line in resultsLines:
    strippedLine = line.strip("- \n")
    if "PASS" in strippedLine:
      isPassed = True
    elif "FAIL" in strippedLine:
      isPassed = False
    elif strippedLine:
      testResult = strippedLine.split()
      testResults.append({
          'name': testResult[0],
          'isPassed': isPassed,
          'realtime': testResult[1].split("=")[1] if isPassed else testResult[2].split("=")[1],
          'reason': testResult[1].strip("()") if not isPassed else None
      })
  return testResults

def getWorkbenchData(filePath):
  testLogFile = open(filePath)
  testLogLines = testLogFile.readlines()
  testLogFile.close()
  startIndices = {}
  endIndices = {}
  isTestsResultsSection = False
  testData = {}

  for index in range(len(testLogLines)):
    line = testLogLines[index]
    if "TEST SUMMARY" in line:
      startIndices['testsResults'] = index + 2
      isTestsResultsSection = True
    elif "PASS" in line and isTestsResultsSection:
      testData['passedTestsNum'] = line.split('-')[1].strip()
    elif "FAIL" in line and isTestsResultsSection:
      testData['failedTestsNum'] = line.split('-')[1].strip()
    elif "TOTAL RUNTIME:" in line and isTestsResultsSection:
      endIndices['testsResults'] = index - 1
      isTestsResultsSection = False

  testData['name'] = testLogLines[0].split("/")[-1].strip()
  testData['directory'] = testLogLines[3].split(": ")[1].strip()
  testData['date'] = testLogLines[1].split(": ")[1].strip()
  testData['version'] = testLogLines[2].strip("/ ").split()[1]
  testData['totalRuntime'] = int(testLogLines[-2].split(": ")[1].strip())
  testData['clockTime'] = int(testLogLines[-1].split(": ")[1].strip())
  testData['results'] = getTestResults(testLogLines[startIndices['testsResults']:endIndices['testsResults']])
  
  return testData

def parseAndOutput(
  inputDirectory,
  outputDirectory,
  cursor,
  cnx,
  shouldDisplayTabular,
  shouldSaveToJSON,
  shouldSaveToDB,
  logFilePath
):
  print("Worker process id: {0}".format(getpid()))
  workbenchData = getWorkbenchData(logFilePath)
  if shouldDisplayTabular:
    dataframe = pandas.DataFrame(workbenchData['results'])
    dataframe['version'] = workbenchData['version']
    dataframe['date'] = workbenchData['date']
    print(dataframe)
    parsedFileName = outputDirectory + workbenchData['name'].split("/")[-1] + ".tabular.csv"
    dataframe.to_csv(parsedFileName, index=False)
    del dataframe # release memory

  if shouldSaveToJSON:
    # save parsed logs to json file
    parsedFileName = outputDirectory + workbenchData['name'].split("/")[-1] + ".parsed.json"
    with open(parsedFileName, 'w') as outfile:
      json.dump(workbenchData, outfile)

  if shouldSaveToDB and cursor:
    # save parsed logs to MySQL database
    testsData = workbenchData.pop('results')
    cursor.execute(checkWorkbenchIsSaved, (workbenchData['name'], workbenchData['version']))
    if cursor.fetchall()[0][0] > 0:
      print("Workbench already saved in database; name: " + workbenchData['name'] + ", version: " + workbenchData['version'])
    else:
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
      cursor.execute(updateWorkbenchPassFailCount, (workbenchId,))
      cnx.commit()
  
  del workbenchData # release memory
