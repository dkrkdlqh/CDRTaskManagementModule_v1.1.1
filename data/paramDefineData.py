from const.programVarType import ProgramVarType



class ParamDefineData():

    def __init__(self, paramName:str = "", paramType:str = ""):

        self.__paramName        :str     = paramName
        self.__paramType        :str     = paramType
            
    
    
    def setParam(self, name:str, type:str):
        
        self.__paramName    = name
        self.__paramType    = type


    def getParamName(self) -> str:
        return self.__paramName
    

    def getParamType(self) -> str:
        return self.__paramType