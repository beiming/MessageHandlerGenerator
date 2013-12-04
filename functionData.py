#coding=utf-8

class ParameterData(object):
    '''parameter data value, type'''

    def __init__(self, lis):
        super(ParameterData, self).__init__()
        self.value = lis[0]
        if len(lis) > 1:
            self.type = lis[1]
        else:
            self.type = '*'

    def __str__(self):
        return '%s:%s' % (self.value, self.type)

class FunctionData(object):
    ''''function metadata class'''

    @classmethod
    def setRegexp(cls, variableReg, handlerFunctionReg, handlerFileFunctionFormat, applicationCMDName, nResponderApplicationCMD, nResponderApplicationCMDNoParam, applicationCMDStatement):
        cls.VariableReg = variableReg
        cls.HandlerFunctionReg = handlerFunctionReg
        cls.HandlerFileFunctionFormat = handlerFileFunctionFormat
        cls.ApplicationCMDName = applicationCMDName
        cls.NResponderApplicationCMD = nResponderApplicationCMD
        cls.NResponderApplicationCMDNoParam = nResponderApplicationCMDNoParam
        cls.ApplicationCMDStatement = applicationCMDStatement

    def __init__(self, mData):
        super(FunctionData, self).__init__()
        self.metadata = mData
        self.functionName = mData.functionName
        self.applicationCMDName = FunctionData.ApplicationCMDName % self.functionName
        self.docComment = mData.docComment
        self.params = {}
        self.analyze()

    def analyze(self):
        import re
        for line in self.metadata.variableText:
            varMatch = FunctionData.VariableReg.match(line)
            if varMatch != None:
                parameterData = ParameterData(varMatch.groups())
                self.params[parameterData.value] = parameterData

            handlerFunctionMatch = FunctionData.HandlerFunctionReg.match(line)
            self.handlerParamList = None
            if handlerFunctionMatch != None:
                self.handlerParamList = [pName.strip() for pName in handlerFunctionMatch.groups()[0].split(',')]

    def toHandlerText(self):
        text = self.docComment
        if self.handlerParamList[0] != '':
            nResponderApplicationCMD = FunctionData.NResponderApplicationCMD % (self.applicationCMDName , ', '.join(self.handlerParamList))
            text += FunctionData.HandlerFileFunctionFormat % (self.functionName, ', '.join([ str(self.params[pName]) for pName in self.handlerParamList]), nResponderApplicationCMD)
        else:
            nResponderApplicationCMD = FunctionData.NResponderApplicationCMDNoParam % self.applicationCMDName
            text += FunctionData.HandlerFileFunctionFormat % (self.functionName, '', nResponderApplicationCMD)

        return text

    def getApplicationCMDArea(self):
        return FunctionData.ApplicationCMDStatement % (self.applicationCMDName, self.applicationCMDName)

    def __str__(self):
    	return '%s, %s, (%s)' % (self.functionName, self.docComment, ', '.join([str(x) for x in self.handlerParamList]))

class FunctionMetadata(object):
    '''function metadata from source code'''

    @staticmethod
    def setRegexp(functionReg, functionBeginReg):
        FunctionMetadata.FunctionReg = functionReg
        FunctionMetadata.FunctionBeginReg = functionBeginReg

    def __init__(self, tList, fIndex):
        super(FunctionMetadata, self).__init__()
        self.textList = tList
        self.functionLineIndex = fIndex
        self.anslyzeInfo()

    def anslyzeInfo(self):
        import re
        self.docComment = ''.join(self.textList[: self.functionLineIndex])
        self.functionName = self.textList[self.functionLineIndex].strip()
        funcBodyIndex = self.functionLineIndex + 1 if FunctionMetadata.FunctionBeginReg.match(self.functionName) != None else self.functionLineIndex + 2

        self.variableText = self.textList[funcBodyIndex: -1]
        nameMatch = FunctionMetadata.FunctionReg.match(self.functionName)
        self.functionName = nameMatch.groups()[0] if nameMatch != None else '__NOT_MATCH__%s' % self.functionName
