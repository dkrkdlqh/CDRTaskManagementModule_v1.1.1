import json
import traceback

from cdrutils.log import CDRLog 



class CDRUtil:

    @classmethod
    def loadJsonFile(self, filePath:str) -> dict:
        '''
        ### 타겟 경로의 json 파일 로드
        '''

        jsonData:dict = {}

        with open(filePath, 'r') as file:
            jsonData = json.load(file)

        return jsonData
    


    @classmethod
    def strToJson(self, data:str) -> dict:
        
        result:dict = None
        
        try:
            result = json.loads(data)
        except:
            CDRLog.print("error in CDRUtil.strToJson()")
            traceback.print_exc()
        finally:
            return result




    @classmethod
    def jsonToStr(self, data:dict) -> str:
        
        result:str = None 
        
        try:
            result = json.dumps(data)  
        except:
            CDRLog.print("error in CDRUtil.jsonToStr()")
            traceback.print_exc()
        finally:
            return result  
        

    
    @classmethod
    def getCommVarTypeStr(self, commVarType:type) -> str:

        from variable.tcpipVar import TcpIPVar
        from variable.bleVar import BLEVar
        from variable.melsecPLCVar import MelsecPLCVar
        from variable.modbusTCPVar import ModbusTCPVar
        from variable.mqttVar import MqttVar

        if commVarType == TcpIPVar:
            return "TcpIpVar"
        elif commVarType == MqttVar:
            return "MqttVar"
        elif commVarType == BLEVar:
            return "BLEVar"
        elif commVarType == MelsecPLCVar:
            return "MelsecPLCVar"
        elif commVarType == ModbusTCPVar:
            return "ModbusTCPVar"
        

    @classmethod
    def convertBytesToStrList(self, data:bytearray) -> list[str]:
        '''
        바이트 배열 값을 2자리수 문자열 배열로 변환
        '''
        bytesData:bytes = bytes(data)    
        #데이터 전체를 문자열로 치환 
        # dataStr :str = data.hex()
        
        packetStrList:list[str] = []

        if len(bytesData) > 0 :

            for packet in bytesData :
                
                datasStr :str   = hex(packet).replace("0x", "")
                
                if len(datasStr) == 1:
                    datasStr = '0' + datasStr

                packetStrList.append(datasStr) 

        # CDRLog.print(f"callack : {packetStrList}")
        return packetStrList