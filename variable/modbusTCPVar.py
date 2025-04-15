from pyModbusTCP.client import ModbusClient

from typing import Callable, Any

from const.modbusFuncCode import ModbusFuncCode
from const.event import Event

from cdrutils.log import CDRLog

from data.mainData import MainData


class ModbusTCPVar :

    def __init__(self, eventCallback:Callable[[int, Any], None]) :
        
        self.__eventCallback    :Callable[[int], None]  = eventCallback
        self.__modbusClient     :ModbusClient           = None
        


    def __del__(self) :

        self.__disconnect()
        CDRLog.print('ModbusTCPVar instance is deleted.')



    def __disconnect(self): 

        if self.__modbusClient != None:
            self.__modbusClient.close()
            self.__modbusClient = None


    # ==========================================================================
    # 외부 호출 함수 ============================================================
    # ==========================================================================

    
    def connect(self, addr:str, port:int) :
        
        self.__disconnect()

        # auto_open 옵션을 false로 하고 open() 명령을 통해 수동으로 연결한경우, 작업 중 연결 상태가 끊어지는 상황 발생한다.(is_open -> false)
        # auto_open 옵션을 True로 시작하거나, 사용할때마다 open()을 호출하여 대응해야 한다. 
        self.__modbusClient = ModbusClient(host=addr, port=port, unit_id=1, auto_open=False, timeout=0.5)
        openResult:bool = self.__modbusClient.open()
        
        # 타겟 모드버스 서버에 연결 실패한 경우, 이벤트 전파 
        if openResult == False:

            if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                self.__eventCallback(Event.COMM_VAR_FAILED_TO_CONNECT, self)
            
            self.__modbusClient = None 
        else:
            CDRLog.print(f"ModbusTCP Connected!!!")


    # def isConnected(self) -> bool:

    #     if self.__modbusClient == None:
    #         return False
    #     else:
    #         return self.__modbusClient.is_open
        

    def write(self, writeFunc:str, memoryAddr:int, writeData:list) -> bool:
        '''
        ### 모드버스 write 명령
        [Parameters] \n
        writeOption : write 옵션 \n
        memoryAddr : 시작 메모리 주소 \n
        writeData : write할 데이터 리스트 \n
        [Return] \n
        True : write 성공 \n
        False : write 실패
        '''
        result :bool = False
        
        if self.__modbusClient.is_open == False \
            and MainData.isRunningTPMProgram == True \
            and self.__eventCallback != None:
                
                result = self.__modbusClient.open()
                #mini 250114 임시 테스트
                CDRLog.print(f"modbus TCP write - 재연결. 결과 : {result} ")
                if result == False:
                    self.__eventCallback(Event.COMM_VAR_DISCONNECTED, self)
                    return result

        if writeFunc == ModbusFuncCode.WRITE_MULTI_REGISTERS:
            result = self.__modbusClient.write_multiple_registers(memoryAddr, writeData)  
            
        elif writeFunc == ModbusFuncCode.WRITE_MULTI_COILS :
            result = self.__modbusClient.write_multiple_coils(memoryAddr, writeData)
        
        elif writeFunc == ModbusFuncCode.WRITE_SINGLE_REGISTERS :
            result = self.__modbusClient.write_single_register(memoryAddr, writeData)
        
        elif writeFunc == ModbusFuncCode.WRITE_SINGLE_COILS :
            result = self.__modbusClient.write_single_coil(memoryAddr, writeData)

        return result
    

    def read(self, readFunc:str, memoryAddr:int, readSize:int) -> list:
        '''
        ### 모드버스 read 명령
        [Parameters] \n
        readFunc : read 옵션 \n
        memoryAddr : 시작 메모리 주소 \n
        readSize : read 개수 \n
        [Return] \n
        list : read 성공
        None : read 실패
        '''
        result :list = None

        if self.__modbusClient.is_open == False \
            and MainData.isRunningTPMProgram == True \
            and self.__eventCallback != None:
                
                result = self.__modbusClient.open()

                if result == False:
                    self.__eventCallback(Event.COMM_VAR_DISCONNECTED, self)
                    return result

        if readFunc == ModbusFuncCode.READ_HOLDING_REGISTERS :
            result = self.__modbusClient.read_holding_registers(memoryAddr, readSize)
            
        elif readFunc == ModbusFuncCode.READ_COILS :
            result = self.__modbusClient.read_coils(memoryAddr, readSize)
            
        elif readFunc == ModbusFuncCode.READ_INPUT_REGISTERS :
            result = self.__modbusClient.read_input_registers(memoryAddr, readSize)
            
        return result
