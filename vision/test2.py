import os

def getDirectory():
    return os.getcwd()

def setDirectory(x):
    os.chdir(x)
    print("Directory Changed to:" + os.getcwd())