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

LOG_FILENAME = 'integrate.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

# update repo

def main():

    processesFileName = "processes.bin"
    
    processes = getProcesses(processesFileName)
    
    for k, currentProcess in processes.items():
        # stop server
        os.kill(currentProcess['pid'], signal.SIGKILL)
        print("Killing: " + currentProcess['runFilePath'] + " Pid: " + str(currentProcess['pid']))


def getProcesses(pickleFileName):
    
    try:
        inPickleFile = file(pickleFileName, "r")
    except IOError:
        return({})
    
    processes = pickle.load(inPickleFile)

    inPickleFile.close()
    
    return(processes)
        
main()
