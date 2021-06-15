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
