#coding=utf-8

import os
import os.path as path
import re
import shutil
from xml.dom import minidom
from xml.dom import Node
from functionData import FunctionData
from functionData import FunctionMetadata


#folder path
CurrentPath = os.getcwd()
GCFilesFolder = CurrentPath + os.sep + 'GCFiles' + os.sep
HandlerFilesFolder = CurrentPath + os.sep + 'HandlerFiles' + os.sep
ConfigFilesFolder = CurrentPath + os.sep + 'Config' + os.sep
ConfigXMLFileName = ConfigFilesFolder + 'config.xml'

#global variable
FunctionReg = ''
DocCommentBeginReg = ''
DocCommentEndReg = ''
FunctionBeginReg = ''
FunctionEndReg = ''
VariableReg = ''
GCMessageReg = ''
HandlerFunctionReg = ''

TemplateFileName = ''
HandlerFileClassNameFlag = ''
HandlerFileContentFlag = ''
HandlerFileFunctionFormat = ''
ApplicationCMDName = ''
NResponderApplicationCMD = ''
NResponderApplicationCMDNoParam = ''
ApplicationCMDStatement = ''
HandlerFileName = ''
ApplicationCMDArea = ''


def debug(func):
    def _call(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            print('function:%s()  ->  Error:\n%s' % (func.__name__, error))
    return _call

def initVariable():
    '''init path variable'''
    global TemplateFileName, FunctionReg, FunctionBeginReg, VariableReg, HandlerFunctionReg
    TemplateFileName = ConfigFilesFolder + TemplateFileName

    FunctionMetadata.setRegexp(FunctionReg, FunctionBeginReg)
    FunctionData.setRegexp(VariableReg, HandlerFunctionReg, HandlerFileFunctionFormat, ApplicationCMDName, NResponderApplicationCMD, NResponderApplicationCMDNoParam, ApplicationCMDStatement)

@debug
def init():
    '''init xml config'''
    if os.path.exists(ConfigXMLFileName):
        configXMLDom = minidom.parse(ConfigXMLFileName)
        root = configXMLDom.documentElement

        getStatement = lambda name, value, reg : name + ' = ' + 're.compile("' + value+ '")' if reg else name + ' = ' + '"' + value + '"'

        for node in root.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                element = node.firstChild;
                isReg = bool(node.getAttribute('reg'))
                statement = getStatement(node.tagName, element.nodeValue, isReg)
                exec(statement, globals())

        initVariable()
        return True
    else:
        print('No config file:\n%s' % configXMLFileName)
        return False

@debug
def codeBlock(fileLineList, funcLineIndex, startFlag, endFlag, forward):
    '''forward or back search code area form source code'''
    if len(fileLineList) == 0:
        return ''
    if funcLineIndex > len(fileLineList) - 1:
        return ''

    if forward == True:
        step = 1
        endLine = len(fileLineList)
    else:
        step = -1
        endLine = 0

    startFlagCount = 0
    endFlagCount = 0
    for index in range(funcLineIndex, endLine, step):
        if startFlag.match(fileLineList[index]) != None:
            startFlagCount += 1
        if endFlag.match(fileLineList[index]) != None:
            endFlagCount += 1
        if startFlagCount != 0 and endFlagCount != 0 and startFlagCount == endFlagCount:
            return index
    return None

@debug
def getFunctionStatement(fileLineList, funcLineIndex):
    '''search function statement'''
    global DocCommentBeginReg, DocCommentEndReg, FunctionBeginReg, FunctionEndReg

    funcDocIndex = codeBlock(fileLineList, funcLineIndex, DocCommentBeginReg, DocCommentEndReg, False)
    funcEndBlock = codeBlock(fileLineList, funcLineIndex, FunctionBeginReg, FunctionEndReg, True)

    if funcEndBlock != None:
        return creatData(fileLineList, funcDocIndex, funcLineIndex, funcEndBlock)
    else:
        return None

@debug
def creatData(fileLineList, startBlockIndex, funcLineIndex, endBlockIndex):
    'creat function metadata'
    if startBlockIndex == None:
        startBlockIndex = funcLineIndex
    funcTextList = fileLineList[startBlockIndex: endBlockIndex + 1]
    mdata = FunctionMetadata(funcTextList, funcLineIndex - startBlockIndex)
    fdata = FunctionData(mdata)
    return fdata

@debug
def saveHandlerFile(className, content):
    '''creat new file'''
    global HandlerFilesFolder
    fileName =  HandlerFilesFolder + className + '.as'
    if os.path.exists(fileName):
        print('File already exists:\n%s' % (fileName))
        return
    shutil.copy(TemplateFileName, fileName)

    newClass = open(fileName, 'r', -1, 'UTF-8')
    allLines = newClass.readlines()
    newClass.close()

    arrLen = len(allLines)
    for index in range(arrLen):
        if allLines[index].find(HandlerFileClassNameFlag) != -1:
            allLines[index] = allLines[index].replace(HandlerFileClassNameFlag, className)
        elif allLines[index].find(HandlerFileContentFlag) != -1:
            allLines[index] = allLines[index].replace(HandlerFileContentFlag, content)

    newClass = open(fileName, 'w', -1, 'UTF-8')
    newClass.writelines(allLines)
    newClass.close()

    print ('Creat Class:\n%s' % (fileName))

@debug
def handleFile(fileName):
    '''handler file info'''
    global FunctionReg, GCMessageReg, HandlerFileName

    handlerFilePrefixMatch = GCMessageReg.match(path.split(fileName)[1])
    if handlerFilePrefixMatch == None:
        print('%s : GCFile Name invalid!' % fileName)
        return

    handlerFileName = HandlerFileName % handlerFilePrefixMatch.groups()[0]

    fileHandler = open(fileName, 'r', -1, 'UTF-8')
    fileLineList = fileHandler.readlines()
    fileHandler.close()

    funcData = None
    funcArea = ''
    applicationCMDArea = ''
    for funcLineIndex in range(0, len(fileLineList)):
        if FunctionReg.match(fileLineList[funcLineIndex]) != None:
            funcData = getFunctionStatement(fileLineList, funcLineIndex)
            if funcData != None:
                funcArea += funcData.toHandlerText()
                applicationCMDArea += funcData.getApplicationCMDArea()

    applicationCMDArea = ApplicationCMDArea % applicationCMDArea
    saveHandlerFile(handlerFileName, funcArea + applicationCMDArea)

@debug
def iterFiles():
    global GCMessageReg, GCFilesFolder
    os.chdir(GCFilesFolder)
    filesList = [path.realpath(fName) for fName in os.listdir() if path.isfile(fName) and GCMessageReg.match(fName) != None]
    for fileName in filesList:
        handleFile(fileName)
@debug
def main():
    '''core function enter'''
    if init() == True:
        iterFiles()
    else:
        print('Init Error!')

if __name__ == '__main__':
    main()