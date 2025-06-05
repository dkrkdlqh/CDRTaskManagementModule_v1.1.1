import time, datetime
import socket
import json
import threading
import select
from cdrutils.log import CDRLog

from const.programVarType import ProgramVarType
from const.tpmCommKeyword import TPMCommKeyword

from data.sysQueueData import SysQueueData
from data.mainData import MainData



class TPMCommManager():

    def __init__(self, mainQueue:SysQueueData):
        super().__init__()

        self.__mainQueue            :SysQueueData       = mainQueue

        self.__socketServer         :socket.socket      = None
        self.__connectedSocket      :socket.socket      = None
        self.__isRunningServer      :bool               = False

        self.__tpmCommThread        :threading.Thread   = None


    def __del__(self):
        
        self.closeServer()
        CDRLog.print("TPMCommManager instance is deleted.")
        CDRLog.Log("#### END ####")
        


    def openServer(self, ip:str = "0.0.0.0", port:int = 200):  #openServer(self, ip:str = "localhost", port:int = 200):
        '''
        ### 서버 오픈
        '''
        self.__tpmCommThread    = threading.Thread(target=self.communicationThreadHandler, args=(ip, port))
        self.__tpmCommThread.start()

        
            

    def closeServer(self):
        '''
        ### 서버 종료
        '''
        self.__isRunningServer = False

        if self.__socketServer != None:

            self.__socketServer.close()
            self.__socketServer = None


        if self.__connectedSocket != None:

            self.__connectedSocket.close()
            self.__connectedSocket = None



    def isConnected(self) -> bool:
        '''
        ### 통신 연결 상태 반환
        '''

        if self.__isRunningServer and self.__connectedSocket != None:
            return True
        else:    
            return False



    def writeCommData(self, jsonData:dict):
        '''
        ### TPM에 데이터 전송
        '''
        if self.__connectedSocket == None:
            return
        
        try:
            
            send_msg:str = TPMCommKeyword.CDR_STR + json.dumps(jsonData) + TPMCommKeyword.CDR_END
            self.__connectedSocket.sendall(send_msg.encode())

        except Exception as error:

            CDRLog.print(error)
            CDRLog.print("클라이언트와 연결 분리 -> 서버 다시 오픈")
            self.openServer()
    
    # def communicationThreadHandler(self, ip: str, port: int):
    #     '''
    #     ### TPM과 통신 처리 전용 쓰레드 
    #     '''
    #     self.__socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     
    #     self.__socketServer.bind((ip, port))
    #     self.__socketServer.listen(1)
    #     CDRLog.print(f"Server opened on {ip}:{port}")

    #     while not MainData.isTerminatedTMMProcess:
    #         self.__socketServer.settimeout(None)  # Non-blocking 상태로 변경
    #         readable, _, _ = select.select([self.__socketServer], [], [], 1)  # 1초 대기

    #         if self.__socketServer in readable:
    #             try:
    #                 self.__connectedSocket, address = self.__socketServer.accept()
    #                 self.__connectedSocket.settimeout(1)
    #                 CDRLog.print(f"Connection success with {address}")
    #                 self.__isRunningServer = True
    #                 break
    #             except Exception as e:
    #                 CDRLog.print(f"Error during accept: {e}")

    #     try:
    #         while self.__isRunningServer:
    #             if self.__connectedSocket is None:
    #                 break

    #             readable, _, _ = select.select([self.__connectedSocket], [], [], 1)  # 1초 대기
    #             if self.__connectedSocket in readable:
    #                 try:
    #                     rawData = self.__connectedSocket.recv(65535)
    #                     if len(rawData) == 0:
    #                         break
    #                     jsonData = json.loads(rawData.decode())
    #                     self.__mainQueue.put(SysQueueData(SysQueueData.RECEIVE_TPM_DATA, jsonData))
    #                 except socket.timeout:
    #                     pass
    #                 except Exception as e:
    #                     CDRLog.print(f"Error during data processing: {e}")
    #                     break
    #     except Exception as err:
    #         CDRLog.print(f"Error: {err}")
    #         self.closeServer()
    #         self.__mainQueue.put(SysQueueData(SysQueueData.CLOSED_TPM_SERVER))
    #     finally:
    #         CDRLog.print("============ communicationThreadHandler terminated...")
            
    def communicationThreadHandler(self, ip:str, port:int):
        '''
        ### TPM과 통신 처리 전용 쓰레드 
        '''
      
        self.__socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socketServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #250528 소켓 재사용 옵션 설정
        self.__socketServer.bind((ip, port))
    
        self.__socketServer.listen(1)
        CDRLog.print(f"Server opened on {ip}:{port}")

        while True:
          
            self.__socketServer.settimeout(1)

            if MainData.isTerminatedTMMProcess == True:
                self.__isRunningServer  = False
                break

            try:
                self.__connectedSocket, address = self.__socketServer.accept()
                self.__connectedSocket.settimeout(1)
                CDRLog.print(f"Connection success with {address}")
        
                self.__isRunningServer  = True
                break

            except socket.timeout:
                continue


        try:
            while self.__isRunningServer :
                
                rawData     :bytes      = None 
                jsonData    :dict       = None
                
                if self.__connectedSocket == None:
                    break

                try:
                    '''
                    데이터 수신
                    '''
                    rawData = self.__connectedSocket.recv(65535)
                    
                    # 수신된 데이터 없음    
                    if len(rawData) == 0 :
                        
                        rawData     = None
                        jsonData    = None
                        break
                        
                    else : # 데이터를 수신했다면, 타입과 데이터 길이 값을 확인
                        
                        jsonData    = json.loads(rawData.decode())
                        
                        if isinstance(jsonData, dict) and "data" in jsonData and jsonData['data'] == "json":
                            
                            # print(jsonData)
                            dataLen         :int    = int(jsonData["length"])
                            tempStrData     :str    = ""

                            # 큰 사이즈의 데이터인 경우, 다음 패킷을 이어붙여서 전체 데이터를 완성시킨다.    
                            while True :
                                
                                tempStrData += self.__connectedSocket.recv(65535).decode()
                                if len(tempStrData) >= dataLen :
                                    break

                            jsonData    = json.loads(tempStrData)

                except socket.timeout:
                    pass
                    
                if jsonData != None:
                    '''
                    수신된 데이터 처리
                    '''
                    self.__mainQueue.put(SysQueueData(SysQueueData.RECEIVE_TPM_DATA, jsonData))
        
        except Exception as err:
            
            CDRLog.print(f"Error : {err}")
            self.closeServer()
            self.__mainQueue.put(SysQueueData(SysQueueData.CLOSED_TPM_SERVER))

        finally:
            CDRLog.print("============ communicationThreadHandler terminated...")
            





