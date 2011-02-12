#!/usr/bin/python

# this requires a hard or sym link to the node binary in the root of the integrate directory

# theoretically this allows arbitrary execution of node.js scripts as the
# person who causes the integration on an hg push because they can modify the integration.conf
# however we're private ssh only, so I'm not concerned.
# actually, even if we restricted the exec file path
# we are still accepting a file to run on our servers from the pusher
# -- non issue, or a bigger issue of server security.

import sys
import os
import shutil
import signal
import pickle
import re
import subprocess
import logging
import ConfigParser

_IntegratePath = os.path.abspath(os.path.dirname(__file__)) + "/"
_IntegrateWorkingDirectory = _IntegratePath + "running/"


_NodePath = _IntegratePath + 'node'


_LogFilePath = _IntegratePath + 'integrate.log'
logging.basicConfig(filename=_LogFilePath,level=logging.DEBUG)

# update repo

def main():

    if len(sys.argv) == 1:
        print 'usage: start.py [path to dir with integrate.conf]'
        exit()

    processesFileName = "processes.bin"

    
    print(_IntegratePath)
    print(_IntegrateWorkingDirectory)
    
    sourceProjectPath = os.path.abspath(sys.argv[1])
    print(sourceProjectPath)
    
    if sourceProjectPath[-1] != "/":
        sourceProjectPath = sourceProjectPath + "/"
    
    configFilePath = sourceProjectPath + 'integrate.conf'
    logging.info('Reading config file:' + configFilePath)
    
    projectType, projectExec = getConfig(configFilePath)
    logging.info("Current Project: ProjectType: " + projectType + " ProjectExec: " + projectExec)


    processes = getProcesses(processesFileName)

    logging.info("Processes currently running: " + str(processes))
    
    try:
        currentProcess = processes[sourceProjectPath]
    except KeyError:
        currentProcess = None
    
    workingProjectPath = _IntegrateWorkingDirectory + getWorkingDirectoryName(sourceProjectPath)
    runFilePath = workingProjectPath + "/" + projectExec
    
    if currentProcess is not None:
        # stop server
        os.kill(currentProcess['pid'], signal.SIGKILL)
        
    # delete working dir if it exists
    if os.path.exists(workingProjectPath):
        shutil.rmtree(workingProjectPath)
        
    # copy repo to working dir
    shutil.copytree(sourceProjectPath, workingProjectPath, True)
 
    # start server

    if projectType.lower() == 'node':
        currentProcess = runNode(_NodePath, runFilePath, workingProjectPath + "/stdout.stderr.node.integrate.log")
    else:
        logging.error("Unsupported project type: " + projectType)
        exit()
    
    currentProcess['runFilePath'] = runFilePath
    
    logging.info('new proc created: ' + str(currentProcess))
    
    processes[sourceProjectPath] = currentProcess

    saveProcesses(processesFileName, processes)



def runNode(pathToNode, pathToScript, pathToLogFile):
    logging.info("Node running file: " + pathToScript)
    
    logFile = open(pathToLogFile, 'w')
    
    try:
        proc = runProcess([pathToNode, pathToScript], logFile)
    except OSError:
        logging.error("There was a problem starting the node process, make sure " + pathToScript + " is a valid path to a node script.")        
        exit()
        
    return({ 'pid' : proc.pid })
    
def getConfig(configFilePath):
    
    projectConfig = ConfigParser.RawConfigParser() 
    projectConfig.read(configFilePath)
    
    try:
        projectType = projectConfig.get('project', 'type')
        projectExec = projectConfig.get('project', 'executable')
    except ConfigParser.NoSectionError as e:
        logging.error('There was a problem with your config file. Please make sure it exists. Attempted path: ' + configFilePath + ' Error: ' + str(e))
        exit()
    except ConfigParser.NoOptionError as e:
        logging.error('There was a problem with your config file. You were missing at least one option we require. Error: ' + str(e))
        exit()
        
    return(projectType, projectExec)



def getWorkingDirectoryName(projectPath):
    # it blows up getting the config file if it's not a valid directory
    # way before it gets here
    
    projectPath, lastDir = os.path.split(projectPath)
    
    if lastDir == '':
        projectPath, lastDir = os.path.split(projectPath)
    if lastDir != '.' and lastDir != '..':
        return(lastDir)
    else:
        logging.error(". or .. as working directory name, don't want to blow away the whole tree so I'm exiting.")
        exit()

def saveProcesses(pickleFileName, processes):

    outPickleFile = file(pickleFileName, "w")

    pickle.dump(processes, outPickleFile)

    outPickleFile.close()


def getProcesses(pickleFileName):
    
    try:
        inPickleFile = file(pickleFileName, "r")
    except IOError:
        return({})
    
    processes = pickle.load(inPickleFile)

    inPickleFile.close()
    
    return(processes)

def runProcess(psData, fileToPipe):
    ps = subprocess.Popen(psData, shell=False, stdout=fileToPipe, stderr=fileToPipe)
    return(ps)

#def getNodeProcess(dir):
#    ps = subprocess.Popen(['ps', '-eo', 'pid,command'], shell=False, stdout=subprocess.PIPE)
#    out, err = ps.communicate()
#    lines = out.split('\n')
#    print(grep('mongo',lines))


#def grep(string,list):
#    expr = re.compile(string)
#    return filter(expr.search,list)



main()
