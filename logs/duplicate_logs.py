from os import listdir

DUPLICATES_NUM = 10**5

def getNewVersion(oldVersion, newCount):
    versionMinusCount = '.'.join(oldVersion.split(".")[0:-1])
    return versionMinusCount + "." + str(newCount).zfill(4)

logsPathsInCurrentDirectory = [fileName.strip() for fileName in listdir("./") if "log" == fileName.split(".")[-1].strip()]
logFilePathToDuplicate = logsPathsInCurrentDirectory[0]

with open(logFilePathToDuplicate) as logFileToDuplicate:
    lines = logFileToDuplicate.readlines()
    oldVersion = lines[2].strip("/ ").split()[1]
    for count in range(DUPLICATES_NUM):
        newVersion = getNewVersion(oldVersion, count)
        newFileName = logFilePathToDuplicate.replace(oldVersion, newVersion)
        if (newFileName not in logsPathsInCurrentDirectory):
            with open("./" + newFileName, 'w') as newLogFile:
                for line in lines:
                    newLogFile.write(line.replace(oldVersion, newVersion))