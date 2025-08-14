import json
import traceback
from const.event import Event
from cdrutils.log import CDRLog 
from data.mainData import MainData

import sys


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
        from variable.fastechVar import FastechVar

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
        elif commVarType == FastechVar:
            return "FastechVar"
        

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
    @classmethod
    def commVarEventCallback(self, eventId:int, data):
        '''
        통신 변수 이벤트 처리 전용 콜백 함수
        '''
        
        # 객체의 클래스 이름과 특정 속성(예: name)을 가져옴
        targetVar = type(data).__name__
        
        
        if hasattr(data, 'name') and data.name:
            targetVar = f"{targetVar} ({data.name})"

        # if data == self.__plcComm:
        #     targetVar = "PLC"
        # elif data == self.__delonghi01Comm:
        #     targetVar = "1번 드롱기"
        # elif data == self.__delonghi02Comm:
        #     targetVar = "2번 드롱기"
        # elif data == self.__delonghiContainer1:
        #     targetVar = "1번 드롱기 컨테이너"
        # elif data == self.__delonghiContainer2:
        #     targetVar = "2번 드롱기 컨테이너"
        # elif data == self.__cupDispenser:
        #     targetVar = "컵 디스펜서"   
        # elif data == self.__FR5Comm:
        #     targetVar = "FR5"   
        # elif data == self.__DHGripperComm:
        #     targetVar = "DH Gripper"    
        
        
        if eventId == Event.COMM_VAR_DISCONNECTED:

            CDRLog.print(f"{targetVar} 통신 끊어짐")
            self.terminateSystem()

        elif eventId == Event.COMM_VAR_FAILED_TO_CONNECT:
            
            CDRLog.print(f"{targetVar} 통신 연결 실패")
            self.terminateSystem()
            
            
    @classmethod
    def terminateSystem(self):
        MainData.isRunningTPMProgram    = False
        sys.exit()
        