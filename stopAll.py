#!/usr/bin/python

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

if not os.path.exists(_IntegrateWorkingDirectory):
    os.mkdir(_IntegrateWorkingDirectory)

_IntegrateProcessesFilePath = _IntegrateWorkingDirectory + "processes.bin"


_LogFilePath = _IntegrateWorkingDirectory + 'integrate.log'
logging.basicConfig(filename=_LogFilePath,level=logging.DEBUG)


# update repo

def main():

    if not os.path.exists(_IntegrateProcessesFilePath):
        print('No processes.bin file found.')
        exit()

    processes = getProcesses(_IntegrateProcessesFilePath)

    for k, currentProcess in processes.items():
        # stop server
        os.kill(currentProcess['pid'], signal.SIGKILL)
        print("Killing: " + currentProcess['runFilePath'] + " Pid: " + str(currentProcess['pid']))

    if len(processes) == 0:
        print('No processes running.')

    os.remove(_IntegrateProcessesFilePath)

def getProcesses(pickleFileName):

    try:
        inPickleFile = file(pickleFileName, "r")
    except IOError:
        return({})

    processes = pickle.load(inPickleFile)

    inPickleFile.close()

    return(processes)

main()
