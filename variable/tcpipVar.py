
import socket

from typing import Callable, Any

from cdrutils.log import CDRLog 

from data.mainData import MainData

from const.event import Event



class TcpIPVar :

    def __init__(self, eventCallback:Callable[[int, Any], None], name=None) :

        self.__eventCallback    :Callable[[int], None]  = eventCallback
        self.__tcpClient        :socket.socket          = None
        self.__server_addr: str | None = None
        self.__server_port: int | None = None
        self.name = name



    def __del__(self) :

        self.__disconnect()
        CDRLog.print('TcpIPVar instance is deleted.')
        
    

    def __disconnect(self):

        if self.__tcpClient != None:
            self.__tcpClient.close()
            self.__tcpClient = None



    # ==========================================================================
    # 외부 호출 함수 ============================================================
    # ==========================================================================

    def connect(self, addr : str ,port : int) :
        
        self.__disconnect()
        self.__server_addr = addr  # 서버 주소 저장
        self.__server_port = port  # 서버 포트 저장
        try:
            self.__tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__tcpClient.settimeout(5)
            self.__tcpClient.connect((addr, port))
            CDRLog.print(f"TCP/IP Connected!!! : {addr} ({port})")
        
        except Exception:
            # 서버 연결 실패 -> 이벤트 발생
            CDRLog.print(f"TCP/IP Fail!!! : {addr} ({port})")
            if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                self.__eventCallback(Event.COMM_VAR_FAILED_TO_CONNECT, self)
            self.__tcpClient = None
            
    def reconnect(self) -> bool:
        """서버 재연결 시도"""
        if MainData.isRunningTPMProgram == True :
            if self.__server_addr is None or self.__server_port is None:
                CDRLog.print("TCP/IP 재연결 실패 : No server info.")
                return False

            CDRLog.print("TCP/IP 재연결 시도 중...")
            self.connect(self.__server_addr, self.__server_port)

            return self.__tcpClient is not None
        else :
            return False


    #mini gripper 250109 
    def write(self, writeData:str, writeType :int = 0):
        CDRLog.print(f"TCP write : {writeData}")
        try : 
            if writeType == 0 :
                self.__tcpClient.sendall((writeData + '\n').encode(encoding='utf-8'))
                return True
            elif writeType == 1 :
                cvtData = bytes.fromhex(writeData)
                self.__tcpClient.sendall((cvtData))
                return True     
            elif writeType == 2:
                self.__tcpClient.sendall(writeData.encode(encoding='utf-8'))
                return True
          

        except Exception as e:#socket.error:
            CDRLog.print(f"TCP/IP Write failed: {e}")

            # 재연결 시도 후 다시 write
            if self.reconnect():
                CDRLog.print("TCP/IP 재연결 성공")
                return self.write(writeData, writeType)
            
            if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                    self.__eventCallback(Event.COMM_VAR_DISCONNECTED, self)
                    
            return False



    def read(self, recvSize:int = 4096) :
        
        try :
            data = self.__tcpClient.recv(recvSize)
            
            if not data:            #상대방이 연결을 종료한 경우
                CDRLog.print(f"TCP/IP Read fail: No data received.")
                if self.reconnect():
                    CDRLog.print("TCP/IP 재연결 성공")
                    return self.read()            
                
                if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                        self.__eventCallback(Event.COMM_VAR_DISCONNECTED, self)        
                return None
            else:    
                CDRLog.Log({data.decode()})  #mini 임시 아두이노 테스트
                return data.decode()
        
        except socket.timeout:      #상대방이 연결을 유지하고 있지만 데이터를 보내지 않은 경우
            CDRLog.Log("TCP/IP Read failed: Timeout.")

            return ""
    
        except Exception as e:      #네트워크 오류 또는 소켓 문제
            CDRLog.print(f"TCP/IP Read failed: {e}")
            if self.reconnect():
                CDRLog.print("TCP/IP 재연결 성공")
                return self.read()            
            
            if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                    self.__eventCallback(Event.COMM_VAR_DISCONNECTED, self)         
            
            return None
        
