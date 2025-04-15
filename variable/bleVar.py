import threading
import asyncio
import datetime
import time
import uuid

from bleak import BleakClient
from bleak.exc import BleakError

from typing import Callable, Any


from cdrutils.log import CDRLog

from const.event import Event

from data.mainData import MainData



class BLEVar :

    def __init__(self, eventCallback:Callable[[int, Any], None]):
        
        self.__eventCallback    :Callable[[int], None]      = eventCallback

        self.__bleClient        :BleakClient                = None
        self.__characteristic   :uuid.UUID                  = None

        self.__prevWritePacket  :str                        = None              
        self.__writePacket      :str                        = None
        self.__isConnected      :bool                       = False
        
        self.__readPacketList   :list[bytearray]            = []
        self.__readPacket       :bytearray                  = None    
        


    def __del__(self) :
        
        self.__bleClient = None
        CDRLog.print('BLEVar instance is deleted.')
    


    async def __disconnect(self):

        if self.__bleClient != None:
            
            await self.__bleClient.disconnect()
            self.__bleClient = None

        self.__isConnected = False



    def connect(self, macAddr:str, serviceUUID:str, characteristicUUID:str, descriptorUUID:str) :
        
        threading.Thread(target = self.__bleCommunicationThreadHandler, args=(macAddr, serviceUUID, characteristicUUID, descriptorUUID)).start()
        
        
    #mini 250114    
    async def reconnect(self, macAddr:str, serviceUUID:str, characteristicUUID:str, descriptorUUID:str):
        await self.__disconnect()

        i = 0 
        while i < 5 :
            if MainData.isRunningTPMProgram == False :
                break
            try:
                if self.__bleClient == None : 
                    self.__characteristic   = uuid.UUID(characteristicUUID)
                    self.__bleClient        = BleakClient(macAddr, timeout=5)#(macAddr)
                CDRLog.print(f"재연결 시도 중...{i}..{self.__bleClient.is_connected} {self.__bleClient.address}")
    
                if not self.__bleClient.is_connected:
                    await self.__bleClient.connect()
                    CDRLog.print(f"재연결 성공...{self.__bleClient.is_connected} {self.__bleClient.address}")

                if self.__bleClient.is_connected:
                    await self.__bleClient.start_notify(self.__characteristic, self.__onBLENotificationCallback)
                    self.__isConnected      = True
                    CDRLog.print(f"재연결 되었습니다. {self.__bleClient.address}")
                    break
            except :
                CDRLog.print("재연결 실패. 1초 후 재시도...")
                await asyncio.sleep(1)
            i += 1
   
        if i >= 5 :
            CDRLog.print(f"재연결 실패... 프로그램 종료...")  #mini 250328
            self.__eventCallback(Event.COMM_VAR_FAILED_TO_CONNECT, self) 
                       
 

    def __bleCommunicationThreadHandler(self, macAddr:str, serviceUUID:str, characteristicUUID:str, descriptorUUID:str):

        try :
            asyncio.run(self.__bleCommunicationAsyncHandler(macAddr, serviceUUID, characteristicUUID, descriptorUUID))
        except:

            if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                self.__eventCallback(Event.COMM_VAR_FAILED_TO_CONNECT, self)
                
            self.__bleClient = None

        CDRLog.print("============ __bleCommunicationThreadHandler terminated...")



    async def __bleCommunicationAsyncHandler(self, macAddr:str, serviceUUID:str, characteristicUUID:str, descriptorUUID:str) :    
        
        await self.__disconnect()

        try :   
                while (not self.__isConnected) and (MainData.isRunningTPMProgram == True) :  
                    try : 
                        self.__characteristic   = uuid.UUID(characteristicUUID)
                        self.__bleClient        = BleakClient(macAddr,timeout=5)#(macAddr)
                        await self.__bleClient.connect()
                        await self.__bleClient.start_notify(self.__characteristic, self.__onBLENotificationCallback)
                        
                        self.__isConnected      = True
                        CDRLog.print(f"BLE Connected!!! : {self.__bleClient.is_connected} {self.__bleClient.address}")
                    except : 
                        await self.reconnect(macAddr, serviceUUID, characteristicUUID, descriptorUUID)  #  재연결 시도   ##mini connect
                while MainData.isRunningTPMProgram == True:
                    
                    if self.__writePacket != None:
                        
                        if self.__bleClient != None and self.__bleClient.is_connected == False  :
                            if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                                self.__eventCallback(Event.COMM_VAR_DISCONNECTED, self) 
                                #mini 250114 임시 테스트
                                CDRLog.print(f"blecomm")
                        else:
                            try:
                                await self.__bleClient.write_gatt_char(self.__characteristic, bytes.fromhex(self.__writePacket), response=True)
                                self.__prevWritePacket  = self.__writePacket
                                self.__writePacket      = None
                            
                            # except BleakError as error:
                            #     self.__isConnected = False
                                

                            except :
                                await self.reconnect(macAddr, serviceUUID, characteristicUUID, descriptorUUID)  #  재연결 시도   ##mini connect

                    await asyncio.sleep(0.1)
                    


        except Exception as e:

            if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                CDRLog.print(f"blecomm_E : {e} // {self.__bleClient.is_connected}")
                await self.reconnect(macAddr, serviceUUID, characteristicUUID, descriptorUUID)  #  재연결 시도   ##mini connect
                #self.__eventCallback(Event.COMM_VAR_FAILED_TO_CONNECT, self)
                #mini 250114 임시 테스트
                
            #self.__bleClient = None
            CDRLog.print(f"except?")

        except : 
            CDRLog.print(f"except???")

        finally:
            CDRLog.print(f"finally~") 
            
        # self.__bleClient.read_gatt_char()
        await self.__bleClient.stop_notify(self.__characteristic)
        await self.__disconnect()



    def clearReadPacket(self):
        '''
        변수에 저장된 패킷 정보 모두 초기화
        '''

        self.__readPacketList   = []
        self.__readPacket       = None



    def isConnected(self) -> bool:

        if self.__bleClient == None:
            return False
        elif self.__isConnected == False:
            return False
        elif self.__bleClient.is_connected == False:
            return False
        else:
            return True



    def read(self) -> bytearray: #list[str]:
        '''
        단일 변수에 저장된 패킷 읽기
        '''
        
        if self.__bleClient != None and self.__bleClient.is_connected == False:                            
            if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                self.__eventCallback(Event.COMM_VAR_DISCONNECTED, self)
                #mini 250114 임시 테스트
                CDRLog.print(f"read")                
        if self.__readPacket == None:
            return None
        else:
            # read된 패킷 정보는 재사용 안되도록 호출 뒤에 초기화
            returnValue:list[str] = self.__readPacket.copy()
            self.__readPacket = None
        
            return returnValue
    


    def readFirstPacket(self) -> list[bytearray]:
        '''
        리스트 변수에 저장된 첫번째 패킷 읽기
        '''    
        
        if self.__bleClient != None and self.__bleClient.is_connected == False:
            if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                self.__eventCallback(Event.COMM_VAR_DISCONNECTED, self)
                #mini 250114 임시 테스트
                CDRLog.print(f"read_f")                
        if len(self.__readPacketList) == 0:
            return None
        
        else:
            return self.__readPacketList.pop(0)



    def reWrite(self):
        '''
        최근 전송한 패킷 다시 전송하기
        '''

        if self.__prevWritePacket != None:
            self.write(self.__prevWritePacket)

    
    def write(self, msg:str) -> bool:
        '''
        패킷 전송하기 
        '''
            
        try :
            
            if self.__bleClient != None:
                
                if self.__bleClient.is_connected == False:
                    if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                        self.__eventCallback(Event.COMM_VAR_DISCONNECTED, self)
                        #mini 250114 임시 테스트
                        CDRLog.print(f"write")
                self.__writePacket = msg
                
                return True
            else:
                
                return False
            
        except Exception as e:
            
            return False
        


    def __onBLENotificationCallback(self, sender: int, data: bytearray):
        '''
        데이터 수신 콜백 함수
        '''
        
        # 수신된 데이터(bytearray)를 문자열 배열 형식으로 변환 후, 단일 변수와 리스트 변수에 모두 할당
        if len(data) > 0 :
            
            self.__readPacket = data #self.__convertBytesToStrList(data)

            # 리스트의 read 패킷 개수가 100개가 넘지 않도록 조절 
            if len(self.__readPacketList) > 100:
                self.__readPacketList.pop(0)

            self.__readPacketList.append(self.__readPacket.copy())



    