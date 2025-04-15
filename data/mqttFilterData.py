class MqttFilterData:

    def __init__(self, key:str, value):

        self.__key      :str    = key
        self.__value            = value

    def getKey(self) -> str:

        return self.__key
    
    def getValue(self):
        
        return self.__value

