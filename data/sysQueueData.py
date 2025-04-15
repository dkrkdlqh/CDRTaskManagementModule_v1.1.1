from typing import List


class SysQueueData():

    RECEIVE_TPM_DATA                :str = "RECEIVE_TPM_DATA"
    CLOSED_TPM_SERVER               :str = "CLOSED_TPM_SERVER"
    ERR_COMM_VAR_CONNECTION         :str = "ERR_COMM_VAR_CONNECTION"

    def __init__(self, id:str = "", data:dict = {}):

        self.__id           :str                 = id
        self.__data         :dict                = data   


    def setId(self, id:str):
        self.__id = id

    def getId(self) -> str:
        return self.__id
    
    def setData(self, data:dict):
        self.__data = data

    def getData(self) -> dict:
        return self.__data
    

