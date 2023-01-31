
# This script syncs the files and folders in source directory with replicate directory
# This process consists of 4 steps as follows;
# 1. Collect the list of files and directories from source and replica folders
# 2. Check if there are any files or directories to delete
# 3. If there are any files or directories to create
# 4. If there are any files to copy

import os, sys
import shutil
from datetime import datetime
import time

def collectData(dir):
        data = []
        for root, dirs, files in os.walk(dir):
            data.extend([os.path.join(root, file),"file"] for file in files)
            data.extend([os.path.join(root, dir),"folder"] for dir in dirs)
        return data

class SyncDataSource:
    def __init__(self, sourceDir, replicaDir, interval, logFileName):
        self.sourceDir = sourceDir
        self.replicaDir = replicaDir
        self.interval = interval
        self.logFileName = logFileName
        self.log("Starting the program...",True)

    def log(self,message,first=False):
        print(message)
        try:
            if first:
                with open(self.logFileName,'w') as f: 
                    f.write(message+'\n')
            else:
                with open(self.logFileName,'a') as f:
                    f.write(message+ '\n')
        except Exception:
            print("ERROR: Error writing to log file")

    def trimSource(self,dir):
        # trim the source directory to remove the ./source/ part
        return dir[len(self.sourceDir):]

    def addSourceString(self,dir):
        return f"{self.sourceDir}{dir}"

    def trimReplica(self,dir):
        # trim the source directory to remove the ./replica/ part
        return dir[len(self.replicaDir):]

    def addReplicaString(self,dir):
        return f"{self.replicaDir}{dir}"

    def checkForDelete(self,dataReplica):
        # iterate through dataReplica and check if it exists in source directory
        # if it does not exist, delete the file or folder
        for anything in dataReplica:
            pathInSource = self.addSourceString(self.trimReplica(anything[0]))
            if not os.path.exists(pathInSource):
                self.log(f"INFO: Deleting {anything[0]}")
                # check if the file or folder in replica exists
                try:
                    if os.path.exists(anything[0]): 
                        if anything[1] == "file":
                                os.remove(anything[0])
                        else:
                            shutil.rmtree(anything[0])
                except Exception:
                    self.log(f"ERROR: Could not delete {anything[0]} Exception: {Exception}")

    def checkForCreate(self,dataSource):
        # iterate through dataSource and check if it exists in replica directory
        # if it does not exist, create the file or folder
        for anything in dataSource:
            pathInReplica = self.addReplicaString(self.trimSource(anything[0]))
            if not os.path.exists(pathInReplica):
                self.log(f"INFO: Creating {pathInReplica} ")
                try:
                    if anything[1] == "file":
                        fp = open(pathInReplica, 'x')
                        fp.close()
                    else:
                        os.makedirs(pathInReplica)
                except Exception:
                    self.log(f"ERROR: Failed to create {pathInReplica} Exception: {Exception} ")


    def checkForCopy(self,dataSource):  # sourcery skip: remove-redundant-if
        # iterate through dataSource 
        # copy if the file is changed more recently than the file in Replica
        # copy if the file size is different
        for anything in dataSource:
            if anything[1] == "file": # no need to check folders
                statSource = os.stat(anything[0])
                statReplica = os.stat(self.addReplicaString(self.trimSource(anything[0])))
                timeDiffSource = datetime.now() - datetime.fromtimestamp(statSource.st_mtime)
                timeDiffReplica = datetime.now() - datetime.fromtimestamp(statReplica.st_mtime)
                #log(f"Checking Last Modified for {anything[0]} In Source {timeDiffSource.total_seconds()} and In Replica {timeDiffReplica.total_seconds()}")
                # compare the last modified times and sizes of the files
                if timeDiffSource < timeDiffReplica or statSource.st_size != statReplica.st_size:
                    self.log(f"INFO: Copying {anything[0]} to {self.addReplicaString(self.trimSource(anything[0]))}")
                    try:
                        shutil.copy(anything[0], self.addReplicaString(self.trimSource(anything[0])))
                    except Exception:
                        self.log(f"ERROR: Failed to copy {anything[0]} to {self.addReplicaString(self.trimSource(anything[0]))} Exception: {Exception}")

    def syncDirs(self):
        # collect all the folders and files from source and replica directories
        dataSource = collectData(self.sourceDir)
        dataReplica = collectData(self.replicaDir)

        # if a file exists in replicaDir but not in sourceDir, delete the file or folder
        self.checkForDelete(dataReplica)
        # if a file exists in sourceDir but not in replicaDir, create the file or folder
        self.checkForCreate(dataSource)
        # if a file in sourceDir is different than the one in replicaDir, copy the file
        self.checkForCopy(dataSource)

    def run(self):
        while True:
            self.syncDirs()
            time.sleep(self.interval)
        
    
if __name__ == '__main__':

    interval = 10 # default interval
    if len(sys.argv) != 5 :
        print("Usage: python sync.py <sourceDir> <replicaDir> <interval> <logFilename> ")
        print("Exiting... ")
        sys.exit(1)
    else:
        sourceDir = sys.argv[1]
        replicaDir = sys.argv[2]
        interval = int(sys.argv[3])
        logFilename = sys.argv[4]
    
    syncer = SyncDataSource(sourceDir,replicaDir,interval,logFilename)
    syncer.run()
        
        


