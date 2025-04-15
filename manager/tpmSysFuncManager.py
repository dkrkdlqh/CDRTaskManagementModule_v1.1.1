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
                                                [Param(SysFuncKeyword.ADDRESS, VarType.TYPE_STR)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.FR_STOP_MOTION, [], []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.FR_READ,          
                                                [], 
                                                [Param(SysFuncKeyword.DATA, VarType.TYPE_FLOAT_ARRAY)]))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.RUN_RWRP_COMM,          
                                                [Param(SysFuncKeyword.ADDRESS, VarType.TYPE_STR), Param(SysFuncKeyword.PORT, VarType.TYPE_INT)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_RWRP_COLLISION,          
                                                [], 
                                                [Param(SysFuncKeyword.COLLISION, VarType.TYPE_INT)]))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.DH_GRIPPER_INIT,          
                                                [Param(SysFuncKeyword.TCPIP_VAR, VarType.TYPE_TCP_IP)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.DH_GRIPPER_HOLD, 
                                                [Param(SysFuncKeyword.TCPIP_VAR, VarType.TYPE_TCP_IP)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.DH_GRIPPER_RELEASE, 
                                                [Param(SysFuncKeyword.TCPIP_VAR, VarType.TYPE_TCP_IP)], 
                                                []))
        #mini gripper 250109
        self.__sysfuncList.append(SysFuncData(  SysFuncName.JODELL_GRIPPER_INIT,          
                                                [Param(SysFuncKeyword.TCPIP_VAR, VarType.TYPE_TCP_IP)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.JODELL_GRIPPER_HOLD, 
                                                [Param(SysFuncKeyword.TCPIP_VAR, VarType.TYPE_TCP_IP)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.JODELL_GRIPPER_RELEASE, 
                                                [Param(SysFuncKeyword.TCPIP_VAR, VarType.TYPE_TCP_IP)], 
                                                []))

        self.__sysfuncList.append(SysFuncData(  SysFuncName.PUB_CRC_ORDER_COMPLETE,          
                                                [   Param(SysFuncKeyword.MQTT_VAR, VarType.TYPE_MQTT), 
                                                    Param(SysFuncKeyword.STORE_ID, VarType.TYPE_INT), 
                                                    Param(SysFuncKeyword.ORDER_ID, VarType.TYPE_INT)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_CRC_ORDER_MENU,          
                                                [], 
                                                [Param(SysFuncKeyword.ORDER_MENU, VarType.TYPE_INT)]))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_CRC_ORDER_MENU_LIST,          
                                                [], 
                                                [Param(SysFuncKeyword.ORDER_MENU_LIST, VarType.TYPE_INT_ARRAY)]))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_CRC_ORDER_QUANTITY,          
                                                [], 
                                                [Param(SysFuncKeyword.ORDER_QUANTITY, VarType.TYPE_INT)]))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_CRC_ORDER_ID,          
                                                [], 
                                                [Param(SysFuncKeyword.ORDER_ID, VarType.TYPE_INT)]))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_CRC_ORDER_NUMBER,          
                                                [], 
                                                [Param(SysFuncKeyword.ORDER_NUM, VarType.TYPE_INT)]))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.RUN_CRC_COMM,          
                                                [   Param(SysFuncKeyword.MQTT_VAR, VarType.TYPE_MQTT), 
                                                    Param(SysFuncKeyword.STORE_ID, VarType.TYPE_INT), 
                                                    Param(SysFuncKeyword.PRINTER_ID, VarType.TYPE_INT), 
                                                    Param(SysFuncKeyword.MAX_ORDER_QUANTITY, VarType.TYPE_INT)],
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.BREW_DELONGHI_ESPRESSO,          
                                                [Param(SysFuncKeyword.DEVICE, VarType.TYPE_BLE)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.BREW_DELONGHI_AMERICANO,          
                                                [Param(SysFuncKeyword.DEVICE, VarType.TYPE_BLE)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.WAKE_UP_DELONGHI,          
                                                [Param(SysFuncKeyword.DEVICE, VarType.TYPE_BLE)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_DELONGHI_STATE_CODE,          
                                                [Param(SysFuncKeyword.DEVICE, VarType.TYPE_BLE)], 
                                                [Param(SysFuncKeyword.STATE_CODE, VarType.TYPE_INT)]))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.IS_DELONGHI_IDLE,          
                                                [Param(SysFuncKeyword.DEVICE, VarType.TYPE_BLE)], 
                                                [Param(SysFuncKeyword.RESULT, VarType.TYPE_BOOL)]))

        self.__sysfuncList.append(SysFuncData(  SysFuncName.SEND_FR_MODBUS_CMD,          
                                                [   Param(SysFuncKeyword.ROBOT_COMM, VarType.TYPE_MODBUS_TCP), 
                                                    Param(SysFuncKeyword.CMD_MEMORY_ADDRESS, VarType.TYPE_INT), 
                                                    Param(SysFuncKeyword.COMMAND, VarType.TYPE_INT), 
                                                    Param(SysFuncKeyword.FEEDBACK_MEMORY_ADDRESS, VarType.TYPE_INT), 
                                                    Param(SysFuncKeyword.START_FEEDBACK, VarType.TYPE_INT), 
                                                    Param(SysFuncKeyword.FIN_FEEDBACK, VarType.TYPE_INT)], 
                                                []))
        
        self.__sysfuncList.append(SysFuncData(  SysFuncName.SEND_PRINT_INFO,          
                                                [   Param(SysFuncKeyword.ORDER_MENU, VarType.TYPE_INT)], 
                                                []))

        self.__sysfuncList.append(SysFuncData(  SysFuncName.SEND_PRINT_CMD,          
                                                [   Param(SysFuncKeyword.MQTT_VAR, VarType.TYPE_MQTT), 
                                                    Param(SysFuncKeyword.ORDER_ID, VarType.TYPE_INT), 
                                                    Param(SysFuncKeyword.PRINTER_ID, VarType.TYPE_INT)], 
                                                []))

        self.__sysfuncList.append(SysFuncData(  SysFuncName.GET_PRINT_STATE,          
                                                [   Param(SysFuncKeyword.MQTT_VAR, VarType.TYPE_MQTT), 
                                                    Param(SysFuncKeyword.PRINTER_ID, VarType.TYPE_INT)], 
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


    def initSysFuncVar(self):
        '''
        ### 시스템 변수 초기화
        '''

        # CRC 시스템 함수 관련 변수들
        self.__crcComm                  :MqttVar    = None
        self.__storeId                  :int        = -1
        self.__orderId                  :int        = -1
        self.__printerId                :int        = -1
        self.__maxOrderNum              :int        = 1
        self.__printerState             :str        = ""
        self.__orderQuantity            :int        = 0
        self.__orderNumber              :int        = -1
        self.__orderPhoneInfo           :str        = ""
        # 주문 내 메뉴
        self.__orderMenuList            :list[int]  = []
        # 메세지 관리 변수
        self.__crcServerMsgQueue        :Queue       = Queue()
        self.__mbrushPrinterMsgQueue    :Queue       = Queue()
        # 주문처리 상태 확인 변수 (True : 처리 중 / False : 대기 중)
        self.__orderState               :bool       = False
        self.__mbrushPrintType          :str        = ""
        self.__isCRCCommThreadRunning   :bool       = False

        self.FR                         = None


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


    
    def publishCRCOrderComplete(self, crcComm : MqttVar, storeId : int, orderId : int):
        '''
        시스템 함수 : CRC 제조완료 구문 발행
        '''
        publishMsg          :str = json.dumps({"code" : "ORDER_COMPLETE", "storeId": storeId, "data": {"orderId": orderId}})
        writeMQTTResult     :bool           = False        

        while True:

            writeMQTTResult = crcComm.write(CRCKey.TOPIC_CRC_RMS, publishMsg)

            if writeMQTTResult == False:
                time.sleep(0.1)
                CDRLog.print("MQTT 변수 write 실패")
            else:
                print(f"publish order complete @@@ !!! {publishMsg}")
                break 

        self.__orderState       = False 
        self.__orderId          = -1
        self.__orderNumber      = -1
        self.__orderQuantity    = 0
        self.__mbrushPrintType  = ""
        self.__orderPhoneInfo   = ""
        self.__orderMenuList    = []   



    def getCRCOrderMenu(self) -> int:
        '''
        시스템 함수 : CRC 시스템으로 주문된 메뉴에 대해, 첫번째 메뉴의 id값 반환
        '''
        orderMenu :int = -1

        if self.__orderMenuList and len(self.__orderMenuList) > 0:

            orderMenu :int = self.__orderMenuList[0]
            del(self.__orderMenuList[0])
        return orderMenu



    def getCRCOrderMenuList(self) -> list[int]:
        '''
        시스템 함수 : CRC 시스템으로 주문된 메뉴에 대해, 모든 메뉴의 id값들을 반환
        '''
        orderMenuList :list[int] = []

        # 최대 주문 가능 개수만큼 -1값을 리스트에 할당.
        for i in range(self.__maxOrderNum):
            orderMenuList.append(-1)

        if self.__orderMenuList:   
            for i in range(len(self.__orderMenuList)):
                orderMenuList[i] = self.__orderMenuList[i]
        print(f'orderMenuList : {orderMenuList}')
        return orderMenuList

        
    
    def getCRCOrderNum(self) -> int:
        '''
        시스템 함수 : CRC 주문 메뉴 총 수량 확인
        '''
        return self.__orderQuantity
    
    
    def getCRCOrderId(self) -> int:
        '''
        시스템 함수 : CRC 주문 Id 확인
        '''
        return self.__orderId
    
    def getCRCOrderNumber(self) -> int:
        '''
        시스템 함수 : CRC 주문 번호 확인
        '''
        return self.__orderNumber
    
    def runCRCCommunication(self, crcComm:MqttVar, storeId : int, printerId : int, maxOrderNum:int) :        
        '''
        시스템 함수 : CRC 상태, 주문 데이터 처리 함수 실행
        '''
        if self.__isCRCCommThreadRunning == True:
            #alreay running...
            return 
        
        self.__crcComm                  = crcComm
        self.__storeId                  = storeId
        self.__printerId                = printerId
        self.__maxOrderNum              = maxOrderNum

        # 해당 함수처리에서 데이터가 'storeId' 항목을 가진 경우, 약속된 storeId 값에 데이터만 처리하도록 필터링을 설정한다.
        self.__crcComm.setSubscribeFilter(MqttFilterData(CRCKey.KEY_STORE_ID, storeId))

        self.__isCRCCommThreadRunning   = True

        threading.Thread(target = self.__crcCommunicationThreadHandler).start()
        threading.Thread(target = self.__crcServerMsgThreadHandler).start()
        threading.Thread(target = self.__mbrushPrinterMsgThreadHandler).start()



    def __crcCommunicationThreadHandler(self):
        '''
        시스템 함수 : 구독중인 CRC 서버 및 mBrush 프린터로부터 전달받은 데이터 처리
        '''

        self.__orderId                  = -1
        self.__orderQuantity            = 0
        self.__orderNumber              = -1
        self.__orderPhoneInfo           = ""
        self.__orderMenuList            = [] # 주문 내 메뉴
        self.__crcServerMsgQueue        = Queue()
        self.__mbrushPrinterMsgQueue    = Queue()
        self.__orderState               = False # 주문처리 상태 확인 변수 (True : 처리 중 / False : 대기 중)

        self.__crcComm.write(CRCKey.TOPIC_CRC_RMS, 
                            json.dumps({
                                CRCKey.KEY_CODE : CRCKey.VALUE_CAFE_START, 
                                CRCKey.KEY_STORE_ID : self.__storeId,
                                CRCKey.KEY_PRINTER_ID : self.__printerId    
                                })
                            )

        readJSonMsg :dict = None
        
        # read 데이터 패킷 정보 모두 초기화 
        self.__crcComm.clearReadPacket()

        while MainData.isRunningTPMProgram and self.__isCRCCommThreadRunning:
            
            # CRC 통신의 경우, 복수의 req가 동시에 수신될 가능성이 있다.
            # 수신 패킷을 정밀하게 파악하기 위해, 리스트에 패킷을 받아 처리한다. 
            readJSonMsg = self.__crcComm.readFirstPacket()            
            
            if readJSonMsg != None:
                
                msgTopic :str = readJSonMsg[MqttVar.KEY_TOPIC]
                try :

                    if msgTopic == CRCKey.TOPIC_CRC_SERVER:
                        
                        self.__crcServerMsgQueue.put(readJSonMsg)

                    elif msgTopic == CRCKey.TOPIC_MBRUSH_PRINTER:
                        self.__mbrushPrinterMsgQueue.put(readJSonMsg)

                except Exception as e :
                    print('Mqtt Rcv Error : ', e)

        CDRLog.print("============ __crcCommunicationThreadHandler terminated...")




    def __crcServerMsgThreadHandler(self):
        '''
        CRC 서버에서 수신된 메세지 처리 스레드\n
        '''
        while MainData.isRunningTPMProgram and self.__isCRCCommThreadRunning:
            
            # 큐에 담긴 데이터가 없으면 skip
            if self.__crcServerMsgQueue.empty() == True:
                continue
            
            reqMsgData  :dict = self.__crcServerMsgQueue.get()

            # 큐 데이터가 'code' key가 없다면 skip
            if not CRCKey.KEY_CODE in reqMsgData:
                continue

            codeValue   :str    = reqMsgData[CRCKey.KEY_CODE]
            resMsgData  :dict   = {}
            
            # CRC 서버의 상태 요청 메세지 처리
            if codeValue == CRCKey.VALUE_CODE_STATUS_CHECK:

                status :str = CRCKey.VALUE_STATUS_ID_READY    

                if self.__orderState == True:
                    status = CRCKey.VALUE_STATUS_ID_WORKING
                
                resMsgData = {
                                CRCKey.KEY_CODE     : CRCKey.VALUE_CODE_STATUS_RES, 
                                CRCKey.KEY_STORE_ID : self.__storeId, 
                                CRCKey.KEY_DATA     : {
                                                        CRCKey.KEY_STATUS_ID : status
                                                        }
                            }

                self.__crcComm.write(CRCKey.TOPIC_CRC_RMS, json.dumps(resMsgData))

                    
            # CRC 서버의 주문 요청 메세지 처리
            elif codeValue == CRCKey.VALUE_CODE_ORDER_REQ:
                CDRLog.print(f"주문 Msg : {reqMsgData}")
                # 제조 중인 상태라면 skip
                if self.__orderState == True:
                    continue
                
                try:
                    self.__orderState = True
                    self.__orderMenuList    = []
                    self.__orderQuantity    = 0

                    orderMenuJson   :dict   = reqMsgData[CRCKey.KEY_DATA][CRCKey.KEY_ORDER_LIST]
                    
                    # 주문된 각각의 메뉴 id값을 self.__orderMenuList 배열에 저장 ------------------
                    # ex. 1000번 메뉴를 1개, 1001번 메뉴를 1개 주문한 경우 배열 데이터가 [1000, 1001]로 생성. 
                    for menuId in orderMenuJson.keys():

                        menuNum:int = orderMenuJson[menuId] 

                        for i in range(menuNum):
                            self.__orderMenuList.append(int(menuId))
                            self.__orderQuantity += 1
                    # ---------------------------------------------------------------------------        



                    # 각인기에 전달할 데이터 저장
                    self.__orderPhoneInfo   = reqMsgData[CRCKey.KEY_PHONE][7:] #끝 4자리 숫자값 
                    self.__mbrushPrintType  = reqMsgData[CRCKey.KEY_PRINT_TYPE]

                    self.__orderId          = int(reqMsgData[CRCKey.KEY_DATA][CRCKey.KEY_ORDER_ID])
                    self.__orderNumber      = int(reqMsgData[CRCKey.KEY_DATA][CRCKey.KEY_ORDER_NUMBER])
                    CDRLog.print(f"주문 id : {self.__orderId}, 주문 수량 : {self.__orderQuantity}, 주문 번호 : {self.__orderNumber}, 주문 메뉴 : {self.__orderMenuList}, 전화 번호 : {self.__orderPhoneInfo}")

                    # 요청 주문 수신 응답 
                    resMsgData = {
                                    CRCKey.KEY_CODE     : CRCKey.VALUE_CODE_ORDER_RES, 
                                    CRCKey.KEY_STORE_ID : self.__storeId, 
                                    CRCKey.KEY_DATA     : {
                                                            CRCKey.KEY_ORDER_ID : self.__orderId
                                                            }
                                }           
                    
                    # JTS 요청사항
                    # 고객주문번호 (taskNumber) 생성 전에 응답이 전달되어 db에 null로 저장 -> 주문 처리 시스템 에러 발생.
                    # 이에, 응답 데이터 회신전 1초 딜레이 요청
                    time.sleep(1)
                    
                    self.__crcComm.write(CRCKey.TOPIC_CRC_RMS, json.dumps(resMsgData))
                    print(f'ORDER_RES : {resMsgData}')  # 250401
                    # 지금은 주문결제앱에서 관련 UI는 비활성화하고 TPM에서 직접 각인 정보를 전달해주는 방식.
                    # if self.__mbrushPrintType == "text":
                    #     # 프린터에 각인 데이터 전송
                    #     self.sendPrintData(1000)

                    #self.__orderState = True #위로 올림

                except Exception as e :
                    self.__orderId = -1
                    self.__orderNumber = -1
                    self.__orderQuantity            = 0
                    self.__orderNumber              = -1
                    self.__orderPhoneInfo           = ""
                    self.__orderMenuList            = [] # 주문 내 메뉴
                    self.__orderState = False
                    CDRLog.print(f"error in ORDER_REQ data parsing: {str(e)}") 
                    traceback.print_exc()

        # 종료 직전에 ERROR 보내고 종료 mini
        status :str = CRCKey.VALUE_STATUS_ID_ERROR    

                
        resMsgData = {
                        CRCKey.KEY_CODE     : CRCKey.VALUE_CODE_STATUS_RES, 
                        CRCKey.KEY_STORE_ID : self.__storeId, 
                        CRCKey.KEY_DATA     : {
                                                CRCKey.KEY_STATUS_ID : status
                                              }
                     }

        self.__crcComm.write(CRCKey.TOPIC_CRC_RMS, json.dumps(resMsgData))

        CDRLog.print("============ __crcServerMsgThreadHandler terminated...")
                


    def sendPrintData(self, orderMenuId:int):

        # 텍스트 각인 타입 주문일 경우에만 각인 정보 전송
        if self.__mbrushPrintType != "text":
            return

        menuNamefirst   : dict  = { CRCKey.KEY_TEXT : "", CRCKey.KEY_COLOR    : "0x000000" }
        menuNameSecond  : dict  = { CRCKey.KEY_TEXT : "", CRCKey.KEY_COLOR    : "0x000000" }

        # 메뉴별 표기 정보 설정
        if orderMenuId == CRCMenuId.HOT_AMERICANO:
            menuNamefirst       = { CRCKey.KEY_TEXT : "Hot",        CRCKey.KEY_COLOR    : "0xff0000" }
            menuNameSecond      = { CRCKey.KEY_TEXT : "Americano",  CRCKey.KEY_COLOR    : "0x000000" }

        elif orderMenuId == CRCMenuId.ICE_AMERICANO:
            menuNamefirst       = { CRCKey.KEY_TEXT : "Ice",        CRCKey.KEY_COLOR    : "0x0000ff" }
            menuNameSecond      = { CRCKey.KEY_TEXT : "Americano",  CRCKey.KEY_COLOR    : "0x000000" }

        elif orderMenuId == CRCMenuId.HOT_ESPRESSO:
            menuNamefirst       = { CRCKey.KEY_TEXT : " ",         CRCKey.KEY_COLOR    : "0xff0000" }
            menuNameSecond      = { CRCKey.KEY_TEXT : "Espresso",  CRCKey.KEY_COLOR    : "0x000000" }
        
        elif orderMenuId == CRCMenuId.BEER:              #250305 mini beer 추가 
            menuNamefirst       = { CRCKey.KEY_TEXT : " ",        CRCKey.KEY_COLOR    : "0x000000" }
            menuNameSecond      = { CRCKey.KEY_TEXT : "BEER",  CRCKey.KEY_COLOR    : "0x000000" }

        # 각인기 텍스트 정보
        printMsg    :dict = {
                                CRCKey.KEY_REQ_ID       : CRCKey.VALUE_SEND_DATA,#"START_PRINT",#CRCKey.VALUE_SEND_DATA,
                                CRCKey.KEY_PRINTER_ID   : self.__printerId,
                                CRCKey.KEY_ORDER_ID     : self.__orderId,#22 #self.__orderId,
                                CRCKey.KEY_PRINTER_MSG  : [
                                                            [
                                                                {
                                                                    CRCKey.KEY_TEXT     : "No." + str(self.__orderNumber),
                                                                    CRCKey.KEY_COLOR    : "0x000000"
                                                                }
                                                            ],
                                                            [
                                                                {
                                                                    CRCKey.KEY_TEXT     : self.__orderPhoneInfo,
                                                                    "color": "0x000000" 
                                                                }
                                                            ],
                                                            [
                                                                menuNamefirst,
                                                                menuNameSecond
                                                            ]
                                                        ]
                            }
        
        self.__crcComm.write("print/rms", json.dumps(printMsg))
        CDRLog.print(f"write MQTT : {printMsg}")   # mini test



    def __mbrushPrinterMsgThreadHandler(self) :
        '''
        mBrush 프린터에서 수신된 메세지 처리 스레드\n
        '''

        while MainData.isRunningTPMProgram and self.__isCRCCommThreadRunning :
            
            if self.__mbrushPrinterMsgQueue.empty() == False:

                reqMsgData  :dict = self.__mbrushPrinterMsgQueue.get()
                
                # 프린터 상태 값 저장
                if CRCKey.KEY_EVENT_ID in reqMsgData:
                    self.__printerState = reqMsgData[CRCKey.KEY_EVENT_ID]        

        CDRLog.print("============ __mbrushPrinterMsgThreadHandler terminated...")

    

    
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
                
                time.sleep(0.1)
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
            



    def sendPrintCmd(self, mqttVar :MqttVar, orderid : int, printerId : int) :
        '''
        각인기 mbrush 실행 명령
        '''
        # Print 명령 전달
        msg_print = {
            "reqId":"START_PRINT",
            "printerId": printerId,
            "orderId": orderid
        }
        msg_str = json.dumps(msg_print)
        
        mqttVar.write("print/rms",msg_str)
        CDRLog.print(f"write MQTT : {msg_print}")   # mini test
        self.__printerState = None

    
    def getPrintState(self, mqttVar:MqttVar, printerId : int) -> str:
        '''
        각인기 mbrush 상태 정보 반환
        '''
        return self.__printerState          

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

