from typing import List

from data.paramDefineData import ParamDefineData



class SysFuncData():

    def __init__(self, funcName:str, paramList:list[ParamDefineData], returnList:list[ParamDefineData]):
        
        self.__funcName         :str                        = funcName
        self.__paramDataList    :list[ParamDefineData]      = paramList
        self.__returnDataList   :list[ParamDefineData]      = returnList
    

    def parse(self, jsonData:str):
        #데이터를 파싱하여 내부 클래스로 저장
        pass
    

    def setFuncName(self, name:str):

        self.__funcName = name



    def getFuncName(self)->str:

        return self.__funcName
    


    def addParamData(self, param:ParamDefineData):

        self.__paramDataList.append(param)



    def getParamDataList(self) -> List[ParamDefineData]:

        return self.__paramDataList
    


    def addReturnData(self, param:ParamDefineData):

        self.__returnDataList.append(param)



    def getReturnDataList(self) -> List[ParamDefineData]:

        return self.__returnDataList
    

    def toJson(self) -> dict:

        jsonData    :dict = {}
        paramData   :ParamDefineData = None    

        jsonData["funcName"]    = self.__funcName

        jsonData["paramList"]   = []
        for i in range(len(self.__paramDataList)):
            paramData = self.__paramDataList[i]
            jsonData["paramList"].append({"name" : paramData.getParamName(), "type" : paramData.getParamType()})


        jsonData["returnList"]  = []
        for i in range(len(self.__returnDataList)):
            paramData = self.__returnDataList[i]
            jsonData["returnList"].append({"name" : paramData.getParamName(), "type" : paramData.getParamType()})

        return jsonData

        