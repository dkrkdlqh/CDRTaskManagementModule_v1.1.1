import threading

import time
import datetime

from variable.bleVar import BLEVar
from variable.melsecPLCVar import MelsecPLCVar
from variable.modbusTCPVar import ModbusTCPVar
from variable.mqttVar import MqttVar
from variable.tcpipVar import TcpIPVar 

from cdrutils.log import CDRLog

from const.config import Config

from const.crcJsonKeyword import CRCJsonKeyword as CRCKey
from const.delonghiState import DelonghiState
from const.modbusFuncCode import ModbusFuncCode

from data.mainData import MainData
from data.mqttFilterData import MqttFilterData

from manager.tpmSysFuncManager import TPMSysFuncManager
from data.orderData import OrderHandler

from cdrutils.cdrUtil import CDRUtil
from manager.CRCManager import CRCManager



STORE_ID                 :int = 6
PRINTER_ID               :int = 6
MIN_ORDER_CNT           :int = 4

class CRCProcessController():
    '''
    해당 클래스는 '[한기대] 공정교육용 로봇 시스템 - 단독 공정 데모'룰 수행하는 기능이 구현되어있다.
    특이사항 : MIN_ORDER_CNT보다 적은 주문이 남아있으면, 
    '''



    def __init__(self):
        CDRLog.print("[0%] var init Start.")
		# config 변수 선언 ------------------------
        self.__railCount                  :int        = 3
        self.__curRailIndex             :int        = 0
        self.__FRCmdAddr              :int        = 101
        self.__FRFeedbackAddr         :int        = 100
        self.__FRStartFeedback        :int        = 1
        self.__FRFinFeedback          :int        = 0
        
        
		# 일반 변수 선언 --------------------------
        #self.__orderId                  :int        = -1
        #self.__menuId                   :int        = -1
        self.__printerState            :int        = 0

        # 센서 상태 : 감지(1), 미감지(0)
        self.__hasCupOnDeloghi01Tray    :int        = 1
        self.__hasCupOnDeloghi02Tray    :int        = 1
        self.__hasCupOnPickupATray      :int        = 1
        self.__hasCupOnPickupBTray      :int        = 1
        self.__hasCupOnPickupCTray      :int        = 1 #######아직없음
        self.__hasCupOnPickupDTray      :int        = 1 #######아직없음
        
        self.__delonghi01Status         :int        = DelonghiState.NOT_READY
        self.__delonghi02Status         :int        = DelonghiState.NOT_READY
        
        

        self.__tpmSysFuncManager    :TPMSysFuncManager = TPMSysFuncManager() 
        # self.__tpmSysFuncManager.initSysFuncVar() 
        MainData.isRunningTPMProgram = True
        

        
        
        CDRLog.print("[30%] Comm init Start.")
        # # 통신 변수 선언 --------------------------------------------------------
        self.__plcComm              :MelsecPLCVar = MelsecPLCVar(CDRUtil.commVarEventCallback, name="PLC")
        self.__plcComm.connect("192.168.3.60", 9988)
        
        self.__delonghi01Comm       :BLEVar = BLEVar(CDRUtil.commVarEventCallback, name ="1번 드롱기")
        self.__delonghi01Comm.connect("00:A0:50:31:89:32", "00035b03-58e6-07dd-021a-08123a000300", "00035b03-58e6-07dd-021a-08123a000301", "00002902-0000-1000-8000-00805f9b34fb")
        
        self.__delonghi02Comm       :BLEVar = BLEVar(CDRUtil.commVarEventCallback, name = "2번 드롱기")
        self.__delonghi02Comm.connect("00:A0:50:63:19:9f", "00035b03-58e6-07dd-021a-08123a000300", "00035b03-58e6-07dd-021a-08123a000301", "00002902-0000-1000-8000-00805f9b34fb")
        
        #아두이노
        self.__delonghiContainer1  :TcpIPVar = TcpIPVar(CDRUtil.commVarEventCallback, name = "1번 드롱기 컨테이너")
        self.__delonghiContainer1.connect("192.168.3.121", 60000)
        self.__delonghiContainer2  :TcpIPVar = TcpIPVar(CDRUtil.commVarEventCallback, name = "2번 드롱기 컨테이너")
        self.__delonghiContainer2.connect("192.168.3.122", 60000)
        self.__cupDispenser        :TcpIPVar = TcpIPVar(CDRUtil.commVarEventCallback, name = "Cup Dispenser")
        self.__cupDispenser.connect("192.168.3.111", 60000)
  
        ##self.__crcComm              :MqttVar = MqttVar(CDRUtil.commVarEventCallback)
        ##self.__crcComm.connect("b85b26e22ac34763bd9cc18d7f655038.s2.eu.hivemq.cloud", 8883, "admin", "201103crcBroker", ["crc/jts", "print/mbrush"])
        ##self.__crcComm.connect("b85b26e22ac34763bd9cc18d7f655038.s2.eu.hivemq.cloud", 8883, "admin", "201103crcBroker", [f"crc/server/{STORE_ID}", "print/mbrush"])
        ##self.__crcComm.setSubscribeFilter(MqttFilterData(CRCKey.KEY_STORE_ID, self.__tpmSysFuncManager.__storeId))
        self.__crcManager = CRCManager(minOrderCnt=MIN_ORDER_CNT)
        
        self.__crcManager.startCRCCommunication(STORE_ID, PRINTER_ID)        

        # 로봇 통신 변수 선언
        self.__FR5Comm           :ModbusTCPVar = ModbusTCPVar(CDRUtil.commVarEventCallback, name = "FR5")
        self.__FR5Comm.connect("192.168.3.100", 502)

        # self.__DHGripperComm    :TcpIPVar = TcpIPVar(self.commVarEventCallback)
        # self.__DHGripperComm.connect("192.168.3.160", 5000)
        # self.__tpmSysFuncManager.initDHGripperVar(self.__DHGripperComm)    
 
        
        CDRLog.print("[70%] Comm init Complete.")
        while True:
            if ( 
                 self.__plcComm.isConnected()
                 and self.__delonghi01Comm.isConnected()
                 and self.__delonghi02Comm.isConnected()

            ):
                break   
        #time.sleep(15)

        CDRLog.print("[100%] Comm connect Complete. Thread Start ")
        # 음료 제조 쓰레드
        threading.Thread(target = self.__drinkMakingThreadHandler).start()   
        

        # 컵 프린트 쓰레드
        threading.Thread(target = self.__cupPrintThreadHandler).start()
       
        # 드롱기 실시간 상태 체크 쓰레드
        threading.Thread(target = self.__delonghiAndSensorStatusCheckingThreadHandler).start()   
        
        # 키보드 명령 key값 입력 처리 쓰레드
        threading.Thread(target = self.__keyInputThreadHandler).start()    



             
    def __drinkMakingThreadHandler(self):
        '''
        ### 음료 제조 쓰레드 
        '''
        
        while True:

            if MainData.isRunningTPMProgram == False:
                break
            ########### ORDER_STATE_CUP_READY 상태인 주문 가져오기#########################################################
            order = self.__crcManager.orderHandler.getOrderItemByState(self.__crcManager.ORDER_STATE_CUP_READY)
            if order :
            
                #1번 드롱기 트레이 비어있고, 드롱기 제조 가능 상태이면
                if self.__hasCupOnDeloghi01Tray == 0 and self.__delonghi01Status == DelonghiState.READY:
                     order.makeMachine = 1
                #2번 드롱기 트레이 비어있고, 드롱기 제조 가능 상태이면
                elif self.__hasCupOnDeloghi02Tray == 0 and self.__delonghi02Status == DelonghiState.READY:
                     order.makeMachine = 2
                
                if order.makeMachine != -1:
                    # 컵 받고 커피 제조 시작하고 컵을 드롱기 트레이로
                    self.__moveCupFromDispenserToMachine(order.menuId, order.makeMachine)
                    self.__crcManager.orderHandler.updateOrderState(order, self.__crcManager.ORDER_STATE_BREW_START)
                    continue
                # #테스트용    
                # time.sleep(5)
                # self.__printerState = 0
                # CDRLog.print('ORDER_STATE_BREW_START')
                # self.__crcManager.orderHandler.updateOrderState(order, self.__crcManager.ORDER_STATE_BREW_START)
                # continue

            ########### ORDER_STATE_BREW_START 상태인 주문 가져오기#########################################################    
            order = self.__crcManager.orderHandler.getOrderItemByState(self.__crcManager.ORDER_STATE_BREW_START)
            if order :
                if order.makeMachine == 1 and self.__delonghi01Status == DelonghiState.READY:
                    # 제조 완료료 상태로 변경
                    self.__crcManager.orderHandler.updateOrderState(order, self.__crcManager.ORDER_STATE_BREW_COMPLETE)
                    continue
                elif order.makeMachine == 2 and self.__delonghi02Status == DelonghiState.READY:
                    # 제조 완료료 상태로 변경
                    self.__crcManager.orderHandler.updateOrderState(order, self.__crcManager.ORDER_STATE_BREW_COMPLETE)
                    continue
               
                # 테스트용
                # time.sleep(5)
                # CDRLog.print('ORDER_STATE_BREW_COMPLETE')
                # self.__crcManager.orderHandler.updateOrderState(order, self.__crcManager.ORDER_STATE_BREW_COMPLETE)
                # continue
                
                               
            ########## ORDER_STATE_BREW_COMPLETE 상태인 주문 가져오기########################################################    
            order = self.__crcManager.orderHandler.getOrderItemByState(self.__crcManager.ORDER_STATE_BREW_COMPLETE)
            if order :
                if order.makeMachine in [1, 2]:
                    self.__moveCupFromMachineToTray(order.makeMachine, self.__curRailIndex)
                    self.__crcManager.orderHandler.updateOrderState(order, self.__crcManager.ORDER_STATE_PICKUP_ENABLE)
                    continue
                #픽업대A 비어있으면
                #  if self.__hasCupOnPickupATray == 0:
                #      if order.MakeMachine == 1 :
                #          self.__moveCupFromMachineToTray(1, 1) # 1번드롱기에서 제조한 커피를 픽업대A에
                #픽업대B 비어있으면
                #픽업대C 비어있으면
                #픽업대D 비어있으면
                # 제조 완료 상태로 변경
                
                # # 테스트용 
                # time.(5)
                # CDRLog.print('ORDER_STATE_PICKUP_ENABLE')
                # self.__crcManager.orderHandler.updateOrderState(order, self.__crcManager.ORDER_STATE_PICKUP_ENABLE)
        
                # continue
            


            
            



            time.sleep(0.1)

            
        CDRLog.print("============ __drinkMakingThread terminated...")
        
    def __cupPrintThreadHandler(self):
        while True:

            if MainData.isRunningTPMProgram == False:
                break
            
            # 프린터 상태 체크
            if self.__printerState == 0:
                ########## ORDER_STATE_NONE 상태인 주문 가져오기    
                order = self.__crcManager.orderHandler.getOrderItemByState(self.__crcManager.ORDER_STATE_NONE)
                if order :
                
                    self.__printerState = 1
                    # 프린터에 컵 프린트 내용 전달
                    self.__crcManager.publishCRCPrintData(order.orderId, order.menuId)
                    # 프린터에 컵 프린트 시작 명령
                    self.__crcManager.publishCRCPrintStart(order.orderId)
                    # 아두이노 PRINT 시작 명령
                    self.__cupDispenser.write("PRINT")
                    time.sleep(20)
                    CDRLog.print(f'PRINT_DONE  {order.orderId, order.menuId}')
                    self.__crcManager.orderHandler.updateOrderState(order, self.__crcManager.ORDER_STATE_CUP_READY)
            time.sleep(1)         
            
        CDRLog.print("============ __cupPrintThread terminated...")
    
    
    def __delonghiAndSensorStatusCheckingThreadHandler(self):
        '''
        ### 드롱기 실시간 상태 체크 쓰레드
        '''

        while True:
            
            if MainData.isRunningTPMProgram == False:
                break

            # 주기적으로 드롱기 상태 체크    
            self.__delonghi01Status         = self.__tpmSysFuncManager.getDelonghiStateCode(self.__delonghi01Comm)
            self.__delonghi02Status         = self.__tpmSysFuncManager.getDelonghiStateCode(self.__delonghi02Comm)
            
            # PLC 
            sensorStateList:list[int]       = self.__plcComm.read("M000", 4) 
            self.__hasCupOnDeloghi01Tray    = sensorStateList[0]
            self.__hasCupOnDeloghi02Tray    = sensorStateList[1]
            self.__hasCupOnPickupATray      = sensorStateList[2]
            self.__hasCupOnPickupBTray      = sensorStateList[3]
            #self.__hasCupOnPickupCTray      = sensorStateList[4]
            #self.__hasCupOnPickupCTray      = sensorStateList[5]

            self.__cupDispenser.read()

            ###### 1번 드롱기 
            # 찌꺼기 통 가득!
            if self.__delonghi01Status == DelonghiState.ERR_FULL_GROUNDS:
                self.__delonghiContainer1.write("OPEN")
                time.sleep(10)
                self.__delonghiContainer1.write("CLOSE")
            # 찌꺼기 통 열림
            elif self.__delonghi01Status == DelonghiState.ERR_OPENED_GROUNDS_CONTAINER:
                self.__delonghiContainer1.write("CLOSE")
            # 드롱기 휴면 상태    
            elif self.__delonghi01Status == DelonghiState.ERR_POWERED_OFF:
                self.__tpmSysFuncManager.wakeupDeloghi(self.__delonghi01Comm)

            ###### 2번 드롱기 
            # 찌꺼기 통 가득
            if self.__delonghi02Status == DelonghiState.ERR_FULL_GROUNDS:
                self.__delonghiContainer2.write("OPEN")
                time.sleep(10)
                self.__delonghiContainer2.write("CLOSE")
                
            # 찌꺼기 통 열림
            elif self.__delonghi02Status == DelonghiState.ERR_OPENED_GROUNDS_CONTAINER:
                self.__delonghiContainer2.write("CLOSE")

            # 휴면 상태
            elif self.__delonghi02Status == DelonghiState.ERR_POWERED_OFF:
                self.__tpmSysFuncManager.wakeupDeloghi(self.__delonghi02Comm)
            time.sleep(1)


    def __moveCupFromMachineToTray(self, FromIdx:int, ToIndex:int):
        '''
        ### 드롱기에서 컵을 픽업대로 이동
        '''
        #드롱기 1
        if FromIdx == 1 and ToIndex == 0:
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 102, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 110, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 30, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
        elif FromIdx == 1 and ToIndex == 1:
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 102, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 111, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 31, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
        elif FromIdx == 1 and ToIndex == 2:
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 102, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 112, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 32, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            
        #드롱기 2
        elif FromIdx == 2 and ToIndex == 0:
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 202, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 210, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 30, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
        elif FromIdx == 2 and ToIndex == 1:
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 202, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 211, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 31, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
        elif FromIdx == 2 and ToIndex == 2:
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 202, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 212, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 32, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
        else :
            CDRLog.print(f"오류 : 잘못된 인덱스 값입니다. FromIdx : {FromIdx}, ToIndex : {ToIndex}")
            
        self.__moveToNextRail()
            

        



    def __moveCupFromDispenserToMachine(self, MenuId:int, makeMachine:int):
        '''
        ### 컵 디스펜서에서 드롱기로 컵 이동
        '''
        if makeMachine == 1:
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 10, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
        
            if MenuId == 1000:
                self.__tpmSysFuncManager.brewDelonghiAmericano(self.__delonghi01Comm)
            elif MenuId == 1003:
                self.__tpmSysFuncManager.brewDelonghiEspresso(self.__delonghi01Comm)
            elif MenuId == 1010:
                self.__tpmSysFuncManager.brewDelonghiHotWater(self.__delonghi01Comm)
            else:
                CDRLog.print("Invalid MenuId") 
          
            #cup drop
            self.__cupDispenser.write("DISPENSE")

            time.sleep(2)
            self.__printerState = 0
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 100, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 101, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
                       
        elif makeMachine == 2: 
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 10, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
        
            if MenuId == 1000:
                self.__tpmSysFuncManager.brewDelonghiAmericano(self.__delonghi02Comm)
            elif MenuId == 1003:
                self.__tpmSysFuncManager.brewDelonghiEspresso(self.__delonghi02Comm)
            elif MenuId == 1010:
                self.__tpmSysFuncManager.brewDelonghiHotWater(self.__delonghi02Comm)
            else:
                CDRLog.print("Invalid MenuId")    

            #cup drop
            self.__cupDispenser.write("DISPENSE")
            
            time.sleep(2)
            self.__printerState = 0
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 200, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
            
            self.__tpmSysFuncManager.sendFRModbusCmd(self.__FR5Comm, self.__FRCmdAddr, 201, self.__FRFeedbackAddr, self.__FRStartFeedback, self.__FRFinFeedback)
        




    def __moveToNextRail(self):
        '''
        ### 다음 레일로 이동
        '''
        self.__curRailIndex = (self.__curRailIndex + 1) 
        
        if self.__curRailIndex >= self.__railCount:
            self.__curRailIndex = 0
        


    ##################################################################################################################################################################    


    def __keyInputThreadHandler(self):
        '''
        ### 프로그램 종료 키 입력 처리 쓰레드
        '''
        while True:
            
            key = input() 

            if key == Config.KEY_QUIT:
                
                CDRLog.print("+++++++++++++++++++++++++++++++++++++++++++++++++++")    
                CDRLog.print("TMM will be terminated. Goodbye and see you again!!")    
                CDRLog.print("+++++++++++++++++++++++++++++++++++++++++++++++++++")   

                CDRUtil.terminateSystem()
                break
            
            elif key == Config.KEY_ORDERLIST_PRINT:
                CDRLog.print("Current Order List")
                self.__crcManager.orderHandler.listOrderItems()


        CDRLog.print("============ __keyInputThread terminated...")


