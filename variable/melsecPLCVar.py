import pymcprotocol

from typing import Callable, Any

from cdrutils.log import CDRLog

from data.mainData import MainData

from const.event import Event


class MelsecPLCVar :

    def __init__(self, eventCallback:Callable[[int, Any], None], name=None) :

        self.__eventCallback    :Callable[[int], None]  = eventCallback
        self.__plcClient                                = None    
        self.name = name  # 객체 이름 저장
    
    
    def __del__(self) :
        
        if self.__plcClient != None:
            self.__plcClient.close()

        del(self.__plcClient)
        
        CDRLog.print('MPLCVar instance is deleted.')
    


    def connect(self, addr:str, port:int, PLCType:str = 'Q'):
        
        try:  
            if PLCType == '4E':
                self.__plcClient = pymcprotocol.Type4E()
            else :
                self.__plcClient = pymcprotocol.Type3E(plctype=PLCType)
            
            self.__plcClient.connect(addr,port)
            CDRLog.print(f"PLC Connected!!! : {self.__plcClient._is_connected}")
            
        except Exception as err:

            CDRLog.print(f'error : init comm melsecPLC var : {err}') 
            self.__plcClient = None


    def isConnected(self) -> bool:

        if self.__plcClient == None:
            return False
        elif self.__plcClient._is_connected == False:
            return False
        else:
            return True
        


    def write(self, headDevice:str, writeData:list[int]) :
        
        if self.__plcClient != None and self.__plcClient._is_connected == False:
            if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                self.__eventCallback(Event.COMM_VAR_DISCONNECTED, self)

        try :
            if self.__plcClient != None:
                self.__plcClient.batchwrite_bitunits(headDevice, writeData)
                return True
            else:
                return False    
        except :
            return False
        
    
    
    def read(self, headDevice:str, readSize:int) -> list[int]:
        
        if self.__plcClient != None and self.__plcClient._is_connected == False:
            if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                self.__eventCallback(Event.COMM_VAR_DISCONNECTED, self)

        try:
            data = self.__plcClient.batchread_bitunits(headDevice, readSize)
            return data
        
        except Exception as error:
            CDRLog.print(f"Melsec PLC error : {error}")
            return None
