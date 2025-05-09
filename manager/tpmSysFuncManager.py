import threading
import json
import socket
import traceback


from const.tpmJsonKeyword import TPMJsonKeyword as TPMKey
from const.crcJsonKeyword import CRCJsonKeyword as CRCKey
from const.programVarType import ProgramVarType as VarType
from const.crcMenuId import CRCMenuId
from const.delonghiPacket import DelonghiPacket
from const.delonghiState import DelonghiState
from const.modbusFuncCode import ModbusFuncCode
from const.sysFuncKeyword import SysFuncKeyword
from const.sysFuncName import SysFuncName

from variable.tcpipVar import TcpIPVar
from variable.bleVar import BLEVar
from variable.melsecPLCVar import MelsecPLCVar
from variable.modbusTCPVar import ModbusTCPVar
from variable.mqttVar import MqttVar


from data.sysFuncData import SysFuncData
from data.paramDefineData import ParamDefineData as Param
from data.mqttFilterData import MqttFilterData
from data.mainData import MainData

from cdrutils.log import CDRLog 
from cdrutils.cdrUtil import CDRUtil

# import FRControlAPI

import datetime
import time
from queue import Queue

from data.orderData import OrderHandler
from manager.CRCManager import CRCManager

class TPMSysFuncManager():

    def __init__(self):

        super().__init__()

        self.__initVar()
        self.__initSystemFuncList()



    def __initVar(self):

        self.__sysfuncList              :list[SysFuncData]       = []



    def __initSystemFuncList(self) :
        
        self.__sysfuncList          = []
        self.__sysfuncList.append(SysFuncData(  SysFuncName.FR_CONNECT,       
                                                [   Param(SysFuncKeyword.ADDRESS, VarType.TYPE_STR)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.FR_STOP_MOTION, [], []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.FR_READ,          
                                                [], 
                                                [Param(SysFuncKeyword.DATA, VarType.TYPE_FLOAT_ARRAY)]))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.SEND_FR_MODBUS_CMD,          
                                                [   Param(SysFuncKeyword.ROBOT_COMM, VarType.TYPE_MODBUS_TCP), 
                                                    Param(SysFuncKeyword.CMD_MEMORY_ADDRESS, VarType.TYPE_INT), 
                                                    Param(SysFuncKeyword.COMMAND, VarType.TYPE_INT), 
                                                    Param(SysFuncKeyword.FEEDBACK_MEMORY_ADDRESS, VarType.TYPE_INT), 
                                                    Param(SysFuncKeyword.START_FEEDBACK, VarType.TYPE_INT), 
                                                    Param(SysFuncKeyword.FIN_FEEDBACK, VarType.TYPE_INT)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.RUN_RWRP_COMM,          
                                                [   Param(SysFuncKeyword.ADDRESS, VarType.TYPE_STR), Param(SysFuncKeyword.PORT, VarType.TYPE_INT)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_RWRP_COLLISION,          
                                                [], 
                                                [Param(SysFuncKeyword.COLLISION, VarType.TYPE_INT)]))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.DH_GRIPPER_INIT,          
                                                [   Param(SysFuncKeyword.TCPIP_VAR, VarType.TYPE_TCP_IP)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.DH_GRIPPER_HOLD, 
                                                [   Param(SysFuncKeyword.TCPIP_VAR, VarType.TYPE_TCP_IP)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.DH_GRIPPER_RELEASE, 
                                                [   Param(SysFuncKeyword.TCPIP_VAR, VarType.TYPE_TCP_IP)], 
                                                []))
        #mini gripper 250109
        self.__sysfuncList.append(SysFuncData(  SysFuncName.JODELL_GRIPPER_INIT,          
                                                [   Param(SysFuncKeyword.TCPIP_VAR, VarType.TYPE_TCP_IP)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.JODELL_GRIPPER_HOLD, 
                                                [   Param(SysFuncKeyword.TCPIP_VAR, VarType.TYPE_TCP_IP)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.JODELL_GRIPPER_RELEASE, 
                                                [   Param(SysFuncKeyword.TCPIP_VAR, VarType.TYPE_TCP_IP)], 
                                                []))


        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.BREW_DELONGHI_ESPRESSO,          
                                                [   Param(SysFuncKeyword.DEVICE, VarType.TYPE_BLE)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.BREW_DELONGHI_AMERICANO,          
                                                [   Param(SysFuncKeyword.DEVICE, VarType.TYPE_BLE)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.WAKE_UP_DELONGHI,          
                                                [   Param(SysFuncKeyword.DEVICE, VarType.TYPE_BLE)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_DELONGHI_STATE_CODE,          
                                                [   Param(SysFuncKeyword.DEVICE, VarType.TYPE_BLE)], 
                                                [Param(SysFuncKeyword.STATE_CODE, VarType.TYPE_INT)]))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.IS_DELONGHI_IDLE,          
                                                [   Param(SysFuncKeyword.DEVICE, VarType.TYPE_BLE)], 
                                                [Param(SysFuncKeyword.RESULT, VarType.TYPE_BOOL)]))

        self.__sysfuncList.append(SysFuncData(  SysFuncName.RUN_CRC_COMM,          
                                                [   Param(SysFuncKeyword.STORE_ID, VarType.TYPE_INT), 
                                                    Param(SysFuncKeyword.PRINTER_ID, VarType.TYPE_INT)], 
                                                []))
        self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_CRC_ORDER,          
                                                [], 
                                                [Param(SysFuncKeyword.ORDER_ID, VarType.TYPE_INT), 
                                                 Param(SysFuncKeyword.ORDER_NUM, VarType.TYPE_INT),
                                                 #Param(SysFuncKeyword.ORDER_MENU, VarType.TYPE_INT)
                                                 Param(SysFuncKeyword.ORDER_MENU_LIST, VarType.TYPE_INT_ARRAY)
                                                 ]))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.SET_CRC_ORDER_DONE,          
                                                [   Param(SysFuncKeyword.ORDER_ID, VarType.TYPE_INT)#,
                                                    #Param(SysFuncKeyword.ORDER_MENU, VarType.TYPE_INT)
                                                ], 
                                                []))

        # self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_CRC_ORDER_MENU,          
        #                                         [], 
        #                                         [Param(SysFuncKeyword.ORDER_MENU, VarType.TYPE_INT)]))
        
        # self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_CRC_ORDER_MENU_LIST,          
        #                                         [], 
        #                                         [Param(SysFuncKeyword.ORDER_MENU_LIST, VarType.TYPE_INT_ARRAY)]))
        
        # self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_CRC_ORDER_QUANTITY,          
        #                                         [], 
        #                                         [Param(SysFuncKeyword.ORDER_QUANTITY, VarType.TYPE_INT)]))
        
        # self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_CRC_ORDER_ID,          
        #                                         [], 
        #                                         [Param(SysFuncKeyword.ORDER_ID, VarType.TYPE_INT)]))
        
        # self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_CRC_ORDER_NUMBER,          
        #                                         [], 
        #                                         [Param(SysFuncKeyword.ORDER_NUM, VarType.TYPE_INT)]))
        
        # self.__sysfuncList.append(SysFuncData(  SysFuncName.RUN_CRC_COMM,          
        #                                         [   Param(SysFuncKeyword.MQTT_VAR, VarType.TYPE_MQTT), 
        #                                             Param(SysFuncKeyword.STORE_ID, VarType.TYPE_INT), 
        #                                             Param(SysFuncKeyword.PRINTER_ID, VarType.TYPE_INT), 
        #                                             Param(SysFuncKeyword.MAX_ORDER_QUANTITY, VarType.TYPE_INT)],
        #                                         []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.SEND_PRINT_DATA,          
                                                [   Param(SysFuncKeyword.ORDER_ID, VarType.TYPE_INT),
                                                    Param(SysFuncKeyword.ORDER_MENU, VarType.TYPE_INT)], 
                                                []))

        self.__sysfuncList.append(SysFuncData(  SysFuncName.SEND_PRINT_START,          
                                                [   Param(SysFuncKeyword.ORDER_ID, VarType.TYPE_INT)], 
                                                []))

        self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_PRINT_STATE,          
                                                [], 
                                                [Param(SysFuncKeyword.PRINTER_STATE, VarType.TYPE_STR)]))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.ORDER_UI_SENDDATA, 
                                                    [Param(SysFuncKeyword.TCPIP_VAR, VarType.TYPE_TCP_IP),
                                                    Param(SysFuncKeyword.TRAY_ID, VarType.TYPE_STR),
                                                    Param(SysFuncKeyword.ORDER_ID, VarType.TYPE_INT)], 
                                                []))
        



    # ============================================================================================================
    # ============================================================================================================
    # 외부 호출 함수 ==============================================================================================
    # ============================================================================================================
    # ============================================================================================================


    # def initSysFuncVar(self):
     
    #     '''
    #     ### 시스템 변수 초기화
    #     '''

    #     # CRC 시스템 함수 관련 변수들
    #     #self.__crcComm                  :MqttVar    = None
    #     self.__crcManager               = CRCManager()
        
    #     self.__storeId                  :int        = -1
    #     #self.__orderId                  :int        = -1
    #     #self.__printerId                :int        = -1
    #     #self.__maxOrderNum              :int        = 1
    #     #self.__printerState             :str        = ""
    #     #self.__orderQuantity            :int        = 0
    #     #self.__orderNumber              :int        = -1
    #     #self.__orderPhoneInfo           :str        = ""
    #     # 주문 내 메뉴
    #     #self.__orderMenuList            :list[int]  = []
    #     # 메세지 관리 변수
    #     self.__crcServerMsgQueue        :Queue       = Queue()
    #     self.__mbrushPrinterMsgQueue    :Queue       = Queue()
    #     # 주문처리 상태 확인 변수 (True : 처리 중 / False : 대기 중)
    #     #self.__orderState               :bool       = False
    #     #self.__mbrushPrintType          :str        = ""
    #     self.__isCRCCommThreadRunning   :bool       = False

    #     #self.FR                         = None


    def getSysFuncList(self) -> list[SysFuncData]:

        return self.__sysfuncList



    def connectToFR(self, addr : str) :
        '''
        시스템 함수 : FR 로봇암 연결 
        '''
        # if self.FR == None :
        #     self.FR = FRControlAPI.RPC(addr)
        #     print(self.FR)

    
    def stopFRMotion(self) :    
        '''
        시스템 함수 : FR 로봇암 동작 정지
        '''    
        # self.FR.stopmotion()
        # return data

    
    def readFRData(self) :       
        '''
        시스템 함수 : FR 로봇암 상태 값 읽기
        ''' 
        data = self.FR.read()
        return data

    
    def runRWRPCommunicator(self,host : str ,port : int) :
        '''
        시스템 함수 : RwRP 연결 함수\n
        host : RwRP 연결 주소\n
        port : RwRP 연결 포트
        '''
        threading.Thread(target=self.__RWRPCommunicateThreadHandler,args=(host, port)).start()



    def __RWRPCommunicateThreadHandler(self, host:str, port:int):
        '''
        시스템 함수 : RwRP 통신 함수\n
        충돌 감지시 동작 및 로봇Pos데이터, Gripper상태 전달
        '''
        
        self.read_th_exit = True
        while MainData.isRunningTPMProgram:
            try:
                self.read_th_exit = True
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, port))
                    s.settimeout(0.1)
                    print(f'Connected to server at {host}:{port}')
                    self.read_th_exit =False
                    
                    while MainData.isRunningTPMProgram:
                        try:      
                            read_data = None                      
                            read_data = s.recv(1024)
                            if read_data is not None :
                                if len(read_data) > 0 :
                                    data_str = read_data.decode()
                                    data_dict = json.loads(data_str)
                                    self.Collision = data_dict["collision"]
                        except socket.timeout:
                            # 타임아웃 발생 시 처리                     
                            pass
                        data = self.FR_Read()
                        temp_data = {
                            "robotpos": data,
                            "gripper": self.gripper_status
                        }
                        send_data = json.dumps(temp_data)
                        if data != None :
                            s.sendall(send_data.encode())
                        elif data == None :
                            print('none')
                        time.sleep(0.1)

            except Exception as e:
                time.sleep(5)

        CDRLog.print("============ RWRPCommunicateThreadHandler terminated...")



    def getRWRPCollsion(self) :
        '''
        RwRP 충돌 감시 확인
        '''
        __collision = self.Collision
        return __collision
    




    #DH Gripper
    def initDHGripperVar(self, gripperComm:TcpIPVar):
        '''
        시스템 함수 : DH 그리퍼 초기화 명령 (485ToEthernet연결시)
        '''
        writeTcpIpResult    :bool           = False

        while MainData.isRunningTPMProgram == True:
            #초기화
            writeTcpIpResult = gripperComm.write('01060100000149f6', 1) #01060100000149f6

            if writeTcpIpResult == False:
                time.sleep(0.1)
                CDRLog.print("그리퍼 초기화 명령 전송 실패")
            else:
                # 그리퍼 초기화 소요 시간      
                time.sleep(3)#mini time.sleep(0.3)
                break

    def holdDHGripper(self, gripperComm:TcpIPVar) :
        '''
        시스템 함수 : DH 그리퍼 잡기 명령
        '''
        writeTcpIpResult    :bool           = False

        while MainData.isRunningTPMProgram == True:

            writeTcpIpResult = gripperComm.write('0106010300007836', 1)

            if writeTcpIpResult == False:
                time.sleep(0.1)
                CDRLog.print("그리퍼 hold 명령 전송 실패")
            else:
                time.sleep(1.5) #mini
                break

               
    def releaseDHGripper(self, gripperComm:TcpIPVar):
        '''
        시스템 함수 : DH 그리퍼 놓기 명령
        '''
        writeTcpIpResult    :bool           = False

        while MainData.isRunningTPMProgram == True:

            writeTcpIpResult = gripperComm.write('0106010303E87888', 1)

            if writeTcpIpResult == False:
                time.sleep(0.1)
                CDRLog.print("그리퍼 Release 명령 전송 실패")
            else:
                time.sleep(1.5) #mini
                break

    #Jodell Gripper  #mini gripper 250109 
    def initJodellGripper(self, gripperComm:TcpIPVar):
        '''
        시스템 함수 : Jodell 그리퍼 활성화 명령
        '''
        # 활성화
        gripperComm.write('090603E80001C932', 1)
        # 그리퍼 활성화 소요 시간      
        #time.sleep(0.3)

    def holdJodellGripper(self, gripperComm:TcpIPVar) :
        '''
        시스템 함수 : Jodell 그리퍼 잡기 명령
        '''
        gripperComm.write('091003E800030600090000FFFFAE81', 1)
               
    def releaseJodellGripper(self, gripperComm:TcpIPVar):
        '''
        시스템 함수 : Jodell 그리퍼 놓기 명령
        '''
        gripperComm.write('091003E80003060009FF00FFFF9E95', 1)


        
        
    # def publishCRCOrderComplete(self, crcComm : MqttVar, storeId : int, orderId : int):
    #     '''
    #     시스템 함수 : CRC 제조완료 구문 발행
    #     '''
    #     publishMsg          :str = json.dumps({"code" : "ORDER_COMPLETE", "storeId": storeId, "data": {"orderId": orderId}})
    #     writeMQTTResult     :bool           = False        

    #     while True:

    #         writeMQTTResult = crcComm.write(CRCKey.TOPIC_CRC_RMS, publishMsg)

    #         if writeMQTTResult == False:
    #             time.sleep(0.1)
    #             CDRLog.print("MQTT 변수 write 실패")
    #         else:
    #             print(f"publish order complete @@@ !!! {publishMsg}")
    #             break 

    #     # self.__orderState       = False 
    #     # self.__orderId          = -1
    #     # self.__orderNumber      = -1
    #     # self.__orderQuantity    = 0
    #     # self.__mbrushPrintType  = ""
    #     # self.__orderPhoneInfo   = ""
    #     # self.__orderMenuList    = []   



    # def getCRCOrderMenu(self) -> int:
    #     '''
    #     시스템 함수 : CRC 시스템으로 주문된 메뉴에 대해, 첫번째 메뉴의 id값 반환
    #     '''
    #     orderMenu :int = -1

    #     if self.__orderMenuList and len(self.__orderMenuList) > 0:

    #         orderMenu :int = self.__orderMenuList[0]
    #         del(self.__orderMenuList[0])
    #     return orderMenu



    # def getCRCOrderMenuList(self) -> list[int]:
    #     '''
    #     시스템 함수 : CRC 시스템으로 주문된 메뉴에 대해, 모든 메뉴의 id값들을 반환
    #     '''
    #     orderMenuList :list[int] = []

    #     # 최대 주문 가능 개수만큼 -1값을 리스트에 할당.
    #     for i in range(self.__maxOrderNum):
    #         orderMenuList.append(-1)

    #     if self.__orderMenuList:   
    #         for i in range(len(self.__orderMenuList)):
    #             orderMenuList[i] = self.__orderMenuList[i]
    #     print(f'orderMenuList : {orderMenuList}')
    #     return orderMenuList

        
    
    # def getCRCOrderNum(self) -> int:
    #     '''
    #     시스템 함수 : CRC 주문 메뉴 총 수량 확인
    #     '''
    #     return self.__orderQuantity
    
    
    # def getCRCOrderId(self) -> int:
    #     '''
    #     시스템 함수 : CRC 주문 Id 확인
    #     '''
    #     return self.__orderId
    
    # def getCRCOrderNumber(self) -> int:
    #     '''
    #     시스템 함수 : CRC 주문 번호 확인
    #     '''
    #     return self.__orderNumber
    
    # def sendCRCOrderComplete(self, orderId : int):
    #     '''
    #     시스템 함수 : CRC 제조완료 구문 발행
    #     '''
    #     self.__crcManager.publishCRCOrderComplete(orderId)
        
        
    def setCRCOrderMakeDone(self, orderId:int):
        '''
        시스템 함수 : CRC 주문 완료 상태로 변경
        '''
        #order = self.__crcManager.orderHandler.getOrderItemByIdMenuState(orderId, orderMenuId, self.__crcManager.ORDER_STATE_MAKE_READY)
        self.__crcManager.orderHandler.updateOrderStateByOrderId(orderId, self.__crcManager.ORDER_STATE_PICKUP_ENABLE)
        
        
      #     # 최대 주문 가능 개수만큼 -1값을 리스트에 할당.
    #     for i in range(self.__maxOrderNum):
    #         orderMenuList.append(-1)

    #     if self.__orderMenuList:   
    #         for i in range(len(self.__orderMenuList)):
    #             orderMenuList[i] = self.__orderMenuList[i]
    #     print(f'orderMenuList : {orderMenuList}')
    #     return orderMenuList      
        
    def getCRCOrder(self) -> tuple[int, int, list[int]]:
        '''
        시스템 함수 : CRC 주문 정보 확인
        '''
        orderId          :int   =   -1
        orderNumber      :int   =   -1
        #orderMenu        :int   =   -1
        orderMenuList    :list[int] = [-1]
        order = self.__crcManager.orderHandler.getOrderItemByState(self.__crcManager.ORDER_STATE_NONE)
        if order :
            orderId     = order.orderId
            orderNumber = order.orderNumber
            #orderMenu   = order.menuId  
            orderMenuList = self.__crcManager.orderHandler.getMenuIdsByOrderId(orderId)
            
                
            self.__crcManager.orderHandler.updateOrderStateByOrderId(orderId, self.__crcManager.ORDER_STATE_MAKE_READY)
            CDRLog.print(f"getCRCOrder : {orderId}, {orderNumber}, {orderMenuList}")
        return (orderId, orderNumber, orderMenuList)
    
    def runCRCCommunication(self,  storeId : int, printerId : int) :        
        '''
        시스템 함수 : CRC 상태, 주문 데이터 처리 함수 실행
        '''
        self.__crcManager = CRCManager()
        self.__printerState             :str        = ""
        self.__crcManager.startCRCCommunication(storeId, printerId)

  
    def sendPrintData(self, orderId:int ,orderMenuId:int):
        self.__crcManager.publishCRCPrintData(orderId, orderMenuId)

    def sendPrintStart(self, orderId:int):
        self.__crcManager.publishCRCPrintStart(orderId)
        
    def getPrintState(self) -> str:
        '''
        각인기 mbrush 상태 정보 반환
        '''
        return self.__printerState          


    
    def brewDelonghiEspresso(self, delonghiComm:BLEVar):
        '''
        시스템 함수 : 드롱기 Espresso 추출
        '''
        delonghiComm.write(DelonghiPacket.REQ_BREW_ESPRESSO)

        readBLEDataValue        :bytearray          = None
        readCount               :int            = 0

        delonghiComm.clearReadPacket()
        while MainData.isRunningTPMProgram == True:

            readBLEDataValue = delonghiComm.read()

            if readBLEDataValue == None:
                
                time.sleep(0.1)
                readCount += 1
                # 문제 : 일정 확률로 write에 대한 상대측 응답이 회신되지 않는 case 발생.
                # 대응 : 
                #   1) 마지막에 성공한 write 값을 저장 
                #   2) read 요청 후 응답 대기.  
                #   3) 일정 횟수(또는 시간)동안 응답없으면, 이슈 상황이라 판단. -> 마지막 write 데이터를 다시 송신   
                if readCount == 5:
                    readCount = 0
                    CDRLog.print("에스프레소 추출 명령 재전송")
                    delonghiComm.write(DelonghiPacket.REQ_BREW_ESPRESSO)

            else:
                # 아래의 사이트에서 음료 brew/stop 명령에 대한 응답 패킷이 회신되는 것을 확인
                # https://grack.com/blog/2022/12/02/hacking-bluetooth-to-brew-coffee-on-github-actions-part-2/
                
                # 추출 명령에 대한 응답 패킷 회신되면 while문 탈출 후 메서드드 작업 종료.
                if readBLEDataValue == DelonghiPacket.RESPONSE_BREW_CMD:
                    CDRLog.print("에스프레소 추출 명령 전송 성공!")
                    break
                else: #회신된 패킷이 추출 명령에 대한 응답 패킷이 아니라면 다시 추출 명령 재전송
                    CDRLog.print("에스프레소 추출 명령 재전송")
                    delonghiComm.write(DelonghiPacket.REQ_BREW_ESPRESSO)  
                    delonghiComm.clearReadPacket()      

    
    def brewDelonghiAmericano(self, delonghiComm:BLEVar) :
        '''
        시스템 함수 : 드롱기 Americano 추출
        '''
        delonghiComm.write(DelonghiPacket.REQ_BREW_AMERICANO)

        readBLEDataValue        :bytearray          = None
        readCount               :int            = 0

        delonghiComm.clearReadPacket()
        while MainData.isRunningTPMProgram == True:

            readBLEDataValue = delonghiComm.read()

            if readBLEDataValue == None:
                
                time.sleep(0.1)
                readCount += 1
                # 문제 : 일정 확률로 write에 대한 상대측 응답이 회신되지 않는 case 발생.
                # 대응 : 
                #   1) 마지막에 성공한 write 값을 저장 
                #   2) read 요청 후 응답 대기.  
                #   3) 일정 횟수(또는 시간)동안 응답없으면, 이슈 상황이라 판단. -> 마지막 write 데이터를 다시 송신   
                if readCount == 5:
                    readCount = 0
                    CDRLog.print("아메리카노 추출 명령 재전송(None)")
                    delonghiComm.write(DelonghiPacket.REQ_BREW_AMERICANO)

            else:
                # 아래의 사이트에서 음료 brew/stop 명령에 대한 응답 패킷이 회신되는 것을 확인
                # https://grack.com/blog/2022/12/02/hacking-bluetooth-to-brew-coffee-on-github-actions-part-2/
                
                # 추출 명령에 대한 응답 패킷 회신되면 while문 탈출 후 메서드드 작업 종료.
                if readBLEDataValue == DelonghiPacket.RESPONSE_BREW_CMD:
                    CDRLog.print("아메리카노 추출 명령 전송 성공!")
                    break
                else: #회신된 패킷이 추출 명령에 대한 응답 패킷이 아니라면 다시 추출 명령 재전송
                    CDRLog.print(f"아메리카노 추출 명령 재전송(response) {readBLEDataValue}")
                    delonghiComm.write(DelonghiPacket.REQ_BREW_AMERICANO)  
                    delonghiComm.clearReadPacket()
        
    def brewDelonghiHotWater(self, delonghiComm:BLEVar) :
        '''
        시스템 함수 : 드롱기 Americano 추출
        '''
        delonghiComm.write(DelonghiPacket.REQ_BREW_HOT_WATER)

        readBLEDataValue        :bytearray          = None
        readCount               :int            = 0

        delonghiComm.clearReadPacket()
        while MainData.isRunningTPMProgram == True:

            readBLEDataValue = delonghiComm.read()

            if readBLEDataValue == None:
                
                time.sleep(0.1)
                readCount += 1
                # 문제 : 일정 확률로 write에 대한 상대측 응답이 회신되지 않는 case 발생.
                # 대응 : 
                #   1) 마지막에 성공한 write 값을 저장 
                #   2) read 요청 후 응답 대기.  
                #   3) 일정 횟수(또는 시간)동안 응답없으면, 이슈 상황이라 판단. -> 마지막 write 데이터를 다시 송신   
                if readCount == 5:
                    readCount = 0
                    CDRLog.print("아메리카노 추출 명령 재전송(None)")
                    delonghiComm.write(DelonghiPacket.REQ_BREW_HOT_WATER)

            else:
                # 아래의 사이트에서 음료 brew/stop 명령에 대한 응답 패킷이 회신되는 것을 확인
                # https://grack.com/blog/2022/12/02/hacking-bluetooth-to-brew-coffee-on-github-actions-part-2/
                
                # 추출 명령에 대한 응답 패킷 회신되면 while문 탈출 후 메서드드 작업 종료.
                if readBLEDataValue == DelonghiPacket.RESPONSE_BREW_CMD:
                    CDRLog.print("아메리카노 추출 명령 전송 성공!")
                    break
                else: #회신된 패킷이 추출 명령에 대한 응답 패킷이 아니라면 다시 추출 명령 재전송
                    CDRLog.print(f"아메리카노 추출 명령 재전송(response) {readBLEDataValue}")
                    delonghiComm.write(DelonghiPacket.REQ_BREW_HOT_WATER)  
                    delonghiComm.clearReadPacket()
        

    def disconnectDelonghi(self, delonghiComm:BLEVar) :
        '''
        시스템 함수 : 드롱기 연결해제
        '''
        # delonghiComm.disconnect()


    
    def wakeupDeloghi(self, delonghiComm:BLEVar) :
        '''
        시스템 함수 : 드롱기 전원 켜기
        '''
        delonghiComm.write(DelonghiPacket.REQ_WAKE_UP)




    def isDelonghiIdle(self, delonghiComm:BLEVar) -> bool:

        state   :int = self.getDelonghiStateCode(delonghiComm)

        if state == DelonghiState.READY:
            return True
        else: 
            return False
        
        
    
    def getDelonghiStateCode(self, delonghiComm:BLEVar) -> int:
        '''
        ### 시스템 함수 : 드롱기 상태 코드 요청\n
        '''

        return self.__generateDelonghiStateCode(self.__getDelonghiState(delonghiComm))
    


    def __getDelonghiState(self, delonghiComm:BLEVar) -> bytearray:#list[str]:
        '''
        ### 시스템 함수 : 드롱기 상태 요청\n
        '''   
        # 드롱기 상태 정보 값 요청 데이터 송수신        
        delonghiComm.write(DelonghiPacket.REQ_DELONGHI_STATE)
        
        # readBLEDataValue        :list[str]          = None
        readBLEDataValue        :bytearray          = None
        readCount               :int            = 0

        delonghiComm.clearReadPacket()
        while MainData.isRunningTPMProgram == True:

            readBLEDataValue = delonghiComm.read()

            if readBLEDataValue == None:
                
                time.sleep(0.2)
                readCount += 1
                # 문제 : 일정 확률로 write에 대한 상대측 응답이 회신되지 않는 case 발생.
                # 대응 : 
                #   1) 마지막에 성공한 write 값을 저장 
                #   2) read 요청 후 응답 대기.  
                #   3) 일정 횟수(또는 시간)동안 응답없으면, 이슈 상황이라 판단. -> 마지막 write 데이터를 다시 송신   
                if readCount == 5:
                    readCount = 0
                    delonghiComm.write(DelonghiPacket.REQ_DELONGHI_STATE)

            else:
                break

        return readBLEDataValue
    
    # 아래의 git 소스를 참조하여 드롱기 주요 상태 정보 패킷 확보
    # https://github.com/Arbuzov/home_assistant_delonghi_primadonna/tree/master/custom_components/delonghi_primadonna
    # ------------------------------------------------------------------------------------------------------------------------------------
    #                   0     1     2     3     4     5     6     7     8     9    10    11    12    13    14    15    16    17    18
    # ------------------------------------------------------------------------------------------------------------------------------------  
    # 준비 완료     | [0xd0, 0x12, 0x75, 0x0f, 0x01, 0x05, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x9d, 0x61]
    # 전원 꺼짐     | [0xd0, 0x12, 0x75, 0x0f, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x03, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0xd6, 0x96]
    # 물탱크 열림   | [0xd0, 0x12, 0x75, 0x0f, 0x01, 0x15, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xaa, 0x31]
    # 물 부족       | [0xd0, 0x12, 0x75, 0x0f, 0x01, 0x45, 0x00, 0x01, 0x00, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2f, 0x64]    
    # 찌꺼기 가득   | [0xd0, 0x12, 0x75, 0x0f, 0x01, 0x05, 0x00, 0x02, 0x00, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x43, 0xd0]
    # 찌꺼기 통 열림| [0xd0, 0x12, 0x75, 0x0f, 0x01, 0x0d, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x86, 0xc9]
    # 커피 추출 시작| [0xd0, 0x12, 0x75, 0x0f, 0x01, 0x05, 0x00, 0x00, 0x00, 0x07, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5c, 0xa7]
    # ------------------------------------------------------------------------------------------------------------------------------------ 
    def __generateDelonghiStateCode(self, statusData:bytearray) -> int:

        curStatus  :int = DelonghiState.NOT_READY

        if statusData != None:

            if statusData == DelonghiPacket.STATUS_READY:
                curStatus = DelonghiState.READY

            elif statusData == DelonghiPacket.STATUS_OFF_POWER:
                curStatus = DelonghiState.ERR_POWERED_OFF   
            
            #mini 250114 OFF Status 추가
            elif statusData == DelonghiPacket.STATUS_OFF_POWER_2:
                curStatus = DelonghiState.ERR_POWERED_OFF   
            elif statusData == DelonghiPacket.STATUS_OFF_POWER_3:
                curStatus = DelonghiState.ERR_POWERED_OFF   
            elif statusData == DelonghiPacket.STATUS_OFF_POWER_4:
                curStatus = DelonghiState.ERR_POWERED_OFF   
            elif statusData == DelonghiPacket.STATUS_OFF_POWER_5:
                curStatus = DelonghiState.ERR_POWERED_OFF               
            elif statusData == DelonghiPacket.STATUS_OFF_POWER_6:
                curStatus = DelonghiState.ERR_POWERED_OFF   
            elif statusData == DelonghiPacket.STATUS_OPEN_WATER_TANK:
                curStatus = DelonghiState.ERR_OPENED_WATER_TANK 

            elif statusData == DelonghiPacket.STATUS_EMPTY_WATER:
                curStatus = DelonghiState.ERR_EMPTY_WATER 
                
            elif statusData == DelonghiPacket.STATUS_EMPTY_WATER_2:
                curStatus = DelonghiState.ERR_EMPTY_WATER 
 
            elif statusData == DelonghiPacket.STATUS_FULL_GROUNDS_CONTAINER:
                curStatus = DelonghiState.ERR_FULL_GROUNDS

            elif statusData == DelonghiPacket.STATUS_OPEN_GROUNDS_CONTAINER:
                curStatus = DelonghiState.ERR_OPENED_GROUNDS_CONTAINER
                
            elif statusData == DelonghiPacket.STATUS_OPEN_GROUNDS_CONTAINER_2:
                curStatus = DelonghiState.ERR_OPENED_GROUNDS_CONTAINER
                
            elif statusData == DelonghiPacket.STATUS_OPEN_GROUNDS_CONTAINER_3:
                curStatus = DelonghiState.ERR_OPENED_GROUNDS_CONTAINER
            
            elif statusData == DelonghiPacket.STATUS_BREWING:
                curStatus = DelonghiState.BREWING     

            elif statusData == DelonghiPacket.STATUS_EMPTY_COFFEE_BEANS:
                    curStatus = DelonghiState.ERR_EMPTY_COFFEE_BEANS
                    
            elif statusData == DelonghiPacket.STATUS_EMPTY_COFFEE_BEANS_2:
                    curStatus = DelonghiState.ERR_EMPTY_COFFEE_BEANS
 
            else:
                statusDataList:list[str] = CDRUtil.convertBytesToStrList(statusData)
                CDRLog.print(f"packet data is : {CDRUtil.convertBytesToStrList(statusData)}")
                #mini 250106 모르는 패킷 오는 경우 log 남기기
                if statusDataList[5] == "05" and statusDataList[7] =="04" :
                    curStatus = DelonghiState.ERR_POLLUTION # 석회 오염

                #['d0', '12', '75', '0f', '01', '05', '00', '20', '00', '07', '00', '00', '00', '00', '00', '00', '00', 'a4', '6c']

        # CDRLog.print(f"I know that delonghi status is : {curStatus}")

        return curStatus
    
    
        # Status  :int = DelonghiState.READY
        
        # if stateData != None and len(stateData) > 0 :

        #     if stateData[5] == "05":

        #         if stateData[7] =="02" :
        #             # print('커피 찌꺼기 통 가득 참')
        #             Status = DelonghiState.ERR_FULL_TRASH

        #         if stateData[7] =="04" :
        #             # print('석회 제거 필요')
        #             Status = DelonghiState.ERR_POLLUTION

        #     elif stateData[5] == "15" :
        #         # print('물탱크 열림')
        #         Status = DelonghiState.ERR_OPENED_WATER_TANK

        #     elif stateData[5] == "45" :
        #         # print('물 부족')
        #         Status = DelonghiState.ERR_EMPTY_WATER

        #     elif stateData[5] == "0d" :
        #         # print('커피 찌꺼기 통 열림')
        #         Status = DelonghiState.ERR_OPENED_TRASH_CONTAINER
            
        #     elif stateData[7] == "20" :
        #         # print('커피 부족')
        #         Status = DelonghiState.ERR_EMPTY_COFFEE_BEANS
            
        #     elif stateData[5] =="03" :
        #         # print('추출 중')
        #         Status = DelonghiState.BREWING

        #     if stateData[11] != "00":
        #         Status = DelonghiState.BREWING
       
        # CDRLog.print(f"packet data is : {CDRUtil.convertBytesToStrList(statusData)}")




    def sendFRModbusCmd(self, frComm : ModbusTCPVar, cmdMemoryAddr : int, cmdValue : int, feedbackMemoryAddr : int, startFeedback:int, finFeedback:int):
        '''
        ### FR로봇 전용 모드버스 명령 전송 함수 
        frComm : FR로봇 모드버스 통신 변수 \n
        memoryAddr : 타겟 메모리 주소 \n
        cmdValue : 명령 값 \n
        startFeedback : frComm에서 전달되는 명령 시작 신호 \n
        finFeedback : frComm에서 전달되는 명령 종료 신호 \n
        '''
        writeResult             :bool   = False
        readValue               :list   = []
        CDRLog.print(f"sendFRModbusCmd // addr : {cmdMemoryAddr}, cmd : {cmdValue}")  #mini250107
        while True:
            # FR 로봇의 모드버스 통신 주기는 100ms (0.1초), 하여 모드버스 write/read 명령 사이에는 최소 0.1초의 대기가 필요하다.
            time.sleep(0.1)   
            # 모드버스 write 요청 -> write 성공 시, 다음 코드 진행
            writeResult  = frComm.write(ModbusFuncCode.WRITE_MULTI_REGISTERS, cmdMemoryAddr, [cmdValue])
            if writeResult == True:
                break


        while True:
            # FR 로봇의 모드버스 통신 주기는 100ms (0.1초), 하여 모드버스 write/read 명령 사이에는 최소 0.1초의 대기가 필요하다.
            time.sleep(0.1)   
            # 모드버스 read 요청 -> FR로봇으로부터 약속된 '작업시작' 신호값이 수신되면, 다음 코드 진행
            readValue   = frComm.read(ModbusFuncCode.READ_INPUT_REGISTERS, feedbackMemoryAddr, 1)
            if readValue != None and readValue[0] == startFeedback:
                break  

        while True:
            # FR 로봇의 모드버스 통신 주기는 100ms (0.1초), 하여 모드버스 write/read 명령 사이에는 최소 0.1초의 대기가 필요하다.
            time.sleep(0.1)   
            # 모드버스 write 요청 -> write 성공 시, 다음 코드 진행
            writeResult  = frComm.write(ModbusFuncCode.WRITE_MULTI_REGISTERS, cmdMemoryAddr, [0])
            if writeResult == True:
                break  
        
        while True:
            # FR 로봇의 모드버스 통신 주기는 100ms (0.1초), 하여 모드버스 write/read 명령 사이에는 최소 0.1초의 대기가 필요하다.
            time.sleep(0.1)   
            # 모드버스 read 요청 -> FR로봇으로부터 약속된 '작업완료' 신호값 수신되면, 작업 완료
            readValue   = frComm.read(ModbusFuncCode.READ_INPUT_REGISTERS, feedbackMemoryAddr, 1)
            if readValue != None and readValue[0] == finFeedback:
                break
            



     

    def initIndyModbusCmd(self, indyComm:ModbusTCPVar):
        while True : 
            time.sleep(0.1)   
            # 모드버스 write 요청 -> write 성공 시, 다음 코드 진행
            writeResult  = indyComm.write(ModbusFuncCode.WRITE_MULTI_REGISTERS, 0, [0])         
            if writeResult == True :
                break


    def sendIndyModbusCmd(self, indyComm:ModbusTCPVar, cmdMemoryAddr : int, cmdValue : int, feedbackMemoryAddr : int, startFeedback:int, finFeedback:int):
        '''
        ### indy로봇 전용 모드버스 명령 전송 함수 
        indyComm : indy로봇 모드버스 통신 변수 
        memoryAddr : 타겟 메모리 주소 (0)
        cmdValue : 명령 값 
        feedbackMemoryAddr : indyComm에서 전달되는 명령 시작 신호 메모리 주소 (1)
        startFeedback : indyComm에서 전달되는 명령 시작 신호 (100)
        finFeedback : indyComm에서 전달되는 명령 종료 신호 (0)
        '''
        # indy 로봇의 모드버스 통신 주기는 10ms (0.01초), 하여 모드버스 write/read 명령 사이에는 최소 0.01초의 대기가 필요하다.
           
        writeResult             :bool   = False
        readValue               :list   = []
        CDRLog.print(f"sendIndyModbusCmd // addr : {cmdMemoryAddr}, cmd : {cmdValue}")  #mini250107
        while True:
            time.sleep(0.1)   
            # 모드버스 write 요청 -> write 성공 시, 다음 코드 진행
            writeResult  = indyComm.write(ModbusFuncCode.WRITE_MULTI_REGISTERS, cmdMemoryAddr, [cmdValue])
            if writeResult == True:
                break


        while True:
            time.sleep(0.1)   
            # 모드버스 read 요청 -> indy로봇으로부터 약속된 '작업시작' 신호값이 수신되면, 다음 코드 진행
            readValue   = indyComm.read(ModbusFuncCode.READ_HOLDING_REGISTERS, feedbackMemoryAddr, 1)
            if readValue != None and readValue[0] == startFeedback:
                break  

        while True:
            time.sleep(0.1)   
            # 모드버스 write 요청 -> write 성공 시, 다음 코드 진행
            writeResult  = indyComm.write(ModbusFuncCode.WRITE_MULTI_REGISTERS, cmdMemoryAddr, [0])
            if writeResult == True:
                break  
        
        while True:
            time.sleep(0.1)   
            # 모드버스 read 요청 -> indy로봇으로부터 약속된 '작업완료' 신호값 수신되면, 작업 완료
            readValue   = indyComm.read(ModbusFuncCode.READ_HOLDING_REGISTERS, feedbackMemoryAddr, 1)
            if readValue != None and readValue[0] == finFeedback:
                break
        # writeModbusResult   :bool           = False
        # readModbusDataValue     :list           = None       
        
                
        # while MainData.isRunningTPMProgram == True:
        #     time.sleep(0.1)    
        #     writeModbusResult = indyComm.write(ModbusFuncCode.WRITE_MULTI_REGISTERS, 0, cmd)
        #     if writeModbusResult == False:
        #         CDRLog.print("Indy modbus 변수 write 실패") 
        #     else:
        #         break
                

   

        # while MainData.isRunningTPMProgram == True:
        #     time.sleep(0.1)
        #     readModbusDataValue = indyComm.read(ModbusFuncCode.READ_HOLDING_REGISTERS, 0, 1)   
            
        #     if readModbusDataValue == None:
        #         CDRLog.print("Indy modbus 변수 read 실패")
        #     else:
        #         # 0번 주소의 값이 '0' -> Indy7이 대기중인 상태임을 의미  
        #         if readModbusDataValue[0] == 0:
        #             break
                
            

    def sendURCmd(self, urComm:ModbusTCPVar, cmd:int):

        writeModbusResult   :bool           = False
        readModbusDataValue     :list           = None
        CDRLog.print(f"sendURModbusCmd //  cmd : {cmd}")  #mini250225        
        while MainData.isRunningTPMProgram == True:
            time.sleep(0.1)
            writeModbusResult = urComm.write(ModbusFuncCode.WRITE_MULTI_REGISTERS, 128, [cmd])

            if writeModbusResult == False:
                CDRLog.print("UR modbus 변수 write 실패")
            else:
                break


        while MainData.isRunningTPMProgram == True:
            time.sleep(0.1)
            readModbusDataValue = urComm.read(ModbusFuncCode.READ_HOLDING_REGISTERS, 128, 1)   
            
            if readModbusDataValue == None:
                CDRLog.print("UR modbus 변수 read 실패")
            else:
                # 0번 주소의 값이 '0' -> UR이 대기중인 상태임을 의미  
                if readModbusDataValue[0] == 0:
                    break

            time.sleep(0.1)


    def order_UI_SendData(self, UIComm:TcpIPVar, slot : str, ordernum : int) :
        msg = '$'+slot+str(ordernum)+'%'#'$b'+str(order_num)+'%'

        UIComm.write(msg,2)
        #CDRLog.print(f'Order_UI << Tray : {slot}  Order : {ordernum}')

