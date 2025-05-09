import threading
import json
import time
from queue import Queue
from variable.mqttVar import MqttVar
from const.crcJsonKeyword import CRCJsonKeyword as CRCKey
from const.crcMenuId import CRCMenuId
from data.orderData import OrderHandler
from data.orderData import OrderItem

from cdrutils.log import CDRLog
from data.mainData import MainData
from cdrutils.cdrUtil import CDRUtil

class CRCManager:
    
    ORDER_STATE_NONE                :int = -1
    ORDER_STATE_MAKE_READY          :int = 0    #TPM용
    ORDER_STATE_CUP_READY           :int = 0
    ORDER_STATE_BREW_START          :int = 1
    ORDER_STATE_BREW_COMPLETE       :int = 2
    ORDER_STATE_PICKUP_ENABLE       :int = 3
    
    
    def __init__(self, minOrderCnt : int = 1):
        self.__crcComm      : MqttVar = None
        self.orderHandler               :OrderHandler = OrderHandler()
        self.__storeId      : int = -1
        self.__printerId    : int = -1
 
        self.__crcServerMsgQueue: Queue = Queue()
        self.__mbrushPrinterMsgQueue: Queue = Queue()
        self.__isCRCCommThreadRunning: bool = False
        
        self.__printerState  : str        = "" # 프린터 상태
        #TPM에서 사용할때는 __minOrderCount = 1로 사용하여, 주문을 한개씩만 받아서 처리하도록 한다.
        self.__minOrderCount : int = minOrderCnt 


    def startCRCCommunication(self,  storeId : int, printerId : int):
        """
        CRC 통신 관련 스레드 시작
        """
        if self.__isCRCCommThreadRunning == True:
            #alreay running...
            return 
        self.__storeId = storeId
        self.__printerId = printerId   
        
        self.__crcComm              :MqttVar = MqttVar(CDRUtil.commVarEventCallback)
        self.__crcComm.connect("b85b26e22ac34763bd9cc18d7f655038.s2.eu.hivemq.cloud", 8883, "admin", "201103crcBroker", [f"crc/server/{self.__storeId}", "print/mbrush"])
      
        self.__crcComm.write(CRCKey.TOPIC_CRC_RMS, json.dumps({"code" : "ORDER_START", "storeId": storeId, "data": {"printerId": printerId}}))

        self.__isCRCCommThreadRunning = True
        # CRC 통신 관련 스레드
        threading.Thread(target=self.__crcCommunicationThreadHandler).start()
        # CRC 서버 메시지 처리 스레드
        threading.Thread(target=self.__crcServerMsgThreadHandler).start()
        # mBrush 프린터 메시지 처리 스레드
        threading.Thread(target=self.__mbrushPrinterMsgThreadHandler).start()
        # CRC RMS 메시지 전송 스레드
        threading.Thread(target=self.__crcRmsMsgThreadHandler).start()
        # 주문 관리 쓰레드
        threading.Thread(target = self.__orderWatchdogThreadHandler).start()   
        

    def stopCRCCommunication(self):
        """
        CRC 통신 관련 스레드 종료
        """
        self.__isCRCCommThreadRunning = False
    

    def __crcCommunicationThreadHandler(self):
        """
        CRC 서버 및 mBrush 프린터로부터 전달받은 데이터 처리
        """


        while MainData.isRunningTPMProgram and self.__isCRCCommThreadRunning:
            readJSonMsg = self.__crcComm.readFirstPacket()
            if readJSonMsg:
                msgTopic = readJSonMsg.get("topic", "")
                if msgTopic == f"{CRCKey.TOPIC_CRC_SERVER}/{self.__storeId}":
                    self.__crcServerMsgQueue.put(readJSonMsg)
                elif msgTopic == CRCKey.TOPIC_MBRUSH_PRINTER:
                    self.__mbrushPrinterMsgQueue.put(readJSonMsg)

        self.__crcServerMsgQueue.queue.clear()
        self.__mbrushPrinterMsgQueue.queue.clear()
        CDRLog.print("============ __crcCommunicationThreadHandler terminated...")

    def __crcServerMsgThreadHandler(self):
        """
        CRC 서버에서 수신된 메시지 처리
        """
        while MainData.isRunningTPMProgram and self.__isCRCCommThreadRunning:
            if self.__crcServerMsgQueue.empty():
                continue

            reqMsgData = self.__crcServerMsgQueue.get()
            if CRCKey.KEY_CODE not in reqMsgData:
                continue

            codeValue = reqMsgData[CRCKey.KEY_CODE]
            if codeValue == CRCKey.VALUE_CODE_ORDER_LIST_RES:
                try:
                    orderList = reqMsgData[CRCKey.KEY_DATA][CRCKey.KEY_ORDER_LIST]
                    for order in orderList:
                        orderId = order[CRCKey.KEY_ORDER_ID]
                        orderDetails = order[CRCKey.KEY_ORDER_DETAILS]
                        orderNumber = order[CRCKey.KEY_ORDER_NUMBER]
                        phone = order[CRCKey.KEY_PHONE][7:] #끝 4자리 숫자값 
                        printType = order[CRCKey.KEY_PRINT_TYPE]

                        for menuId in orderDetails:
                            self.orderHandler.addOrderItem(
                                orderId=orderId,
                                orderNumber=orderNumber,
                                menuId=menuId,
                                orderPhoneInfo=phone,
                                mbrushPrintType=printType
                            )
                        self.orderHandler.listOrderItems()
                        CDRLog.print(f"Order received: ID={orderId}, Details={orderDetails}, Number={orderNumber}, Phone={phone}, PrintType={printType}")
                        #time.sleep(1)
                        resMsgData = {
                            CRCKey.KEY_CODE: CRCKey.VALUE_CODE_ORDER_RES,
                            CRCKey.KEY_STORE_ID: self.__storeId,
                            CRCKey.KEY_DATA: {CRCKey.KEY_ORDER_ID: orderId}
                        }
                        self.__crcComm.write(CRCKey.TOPIC_CRC_RMS, json.dumps(resMsgData))
                        CDRLog.print(f'ORDER_RES : {resMsgData}')
                except Exception as e:
                    CDRLog.print(f"Error processing ORDER_LIST_RES: {str(e)}")
                    CDRLog.print(f"Received data: {reqMsgData}")

    def __mbrushPrinterMsgThreadHandler(self):
        """
        mBrush 프린터에서 수신된 메시지 처리
        """
        while MainData.isRunningTPMProgram and self.__isCRCCommThreadRunning:
            if not self.__mbrushPrinterMsgQueue.empty():
                reqMsgData = self.__mbrushPrinterMsgQueue.get()
                if CRCKey.KEY_EVENT_ID in reqMsgData:
                    self.__printerState = reqMsgData[CRCKey.KEY_EVENT_ID]

        CDRLog.print("============ __mbrushPrinterMsgThreadHandler terminated...")

    def __crcRmsMsgThreadHandler(self):
        """
        CRC RMS 상태 메시지 전송 처리
        """
        timer_Status = 0
        
        self.__crcComm.write(
            CRCKey.TOPIC_CRC_RMS,
            json.dumps({
                CRCKey.KEY_CODE: CRCKey.VALUE_CAFE_START,
                CRCKey.KEY_STORE_ID: self.__storeId,
                CRCKey.KEY_PRINTER_ID: self.__printerId
            })
        )
        
        while MainData.isRunningTPMProgram and self.__isCRCCommThreadRunning:
            current_time = time.time()
            #10초에 한번씩
            if current_time - timer_Status >= 10:
                timer_Status = current_time
                # RMS 상태 전송
                status = CRCKey.VALUE_STATUS_ID_READY #if not self.__orderState else CRCKey.VALUE_STATUS_ID_WORKING
                stateMsgData = {
                    CRCKey.KEY_CODE: CRCKey.VALUE_CODE_STATUS_RES,
                    CRCKey.KEY_STORE_ID: self.__storeId,
                    CRCKey.KEY_DATA: {CRCKey.KEY_STATUS_ID: status}
                }
                self.__crcComm.write(CRCKey.TOPIC_CRC_RMS, json.dumps(stateMsgData))

            time.sleep(0.1)
            
        # 종료 시점에 상태를 ERROR로 설정
        status = CRCKey.VALUE_STATUS_ID_ERROR
        resMsgData = {
            CRCKey.KEY_CODE: CRCKey.VALUE_CODE_STATUS_RES,
            CRCKey.KEY_STORE_ID: self.__storeId,
            CRCKey.KEY_DATA: {CRCKey.KEY_STATUS_ID: status}
        }
        self.__crcComm.write(CRCKey.TOPIC_CRC_RMS, json.dumps(resMsgData))
        CDRLog.print("============ __crcRmsMsgThreadHandler terminated...")
        
    def __orderWatchdogThreadHandler(self):         
        timer_OrderCheck = 0

        while MainData.isRunningTPMProgram:
            current_time = time.time()
            #3초에 한번씩
            if current_time - timer_OrderCheck >= 3:
                timer_OrderCheck = current_time
                # ORDER_STATE_PICKUP_ENABLE 상태인 주문 가져오기  
                while self.orderHandler.getOrderCount() > 0:
                    order = self.orderHandler.getOrderItemByState(self.ORDER_STATE_PICKUP_ENABLE)
                    if not order:
                        break
                    orderId_Check = order.orderId
                    self.orderHandler.removeOrderItem(order) # 완료된 주문 삭제
                    if self.orderHandler.getOrderItemById(orderId_Check) == None:
                        self.publishCRCOrderComplete(orderId_Check) # 완료 메세지 전송
                        
                # 주문이 self.__minOrderCount개 미만일 경우에만 주문 요청 
                if self.orderHandler.getOrderCount() < self.__minOrderCount: 
                    self.publishCRCOrderRequest(1) # 주문 요청 메세지 전송
            
        CDRLog.print("============ __orderWatchdogThreadHandler terminated...")      
        
        
        
        
    def publishCRCOrderComplete(self,  orderId : int):
        '''
        시스템 함수 : CRC 제조완료 구문 발행
        '''
        publishMsg          :str = json.dumps({"code" : "ORDER_COMPLETE", "storeId": self.__storeId, "data": {"orderId": orderId}})
        writeMQTTResult     :bool           = False        

        while True:

            writeMQTTResult = self.__crcComm.write(CRCKey.TOPIC_CRC_RMS, publishMsg)

            if writeMQTTResult == False:
                time.sleep(0.1)
                CDRLog.print("MQTT 변수 write 실패")
            else:
                CDRLog.print(f"publish order complete @@@ !!! {publishMsg}")
                break 

        # self.__orderState       = False 
        # self.__orderId          = -1
        # self.__orderNumber      = -1
        # self.__orderQuantity    = 0
        # self.__mbrushPrintType  = ""
        # self.__orderPhoneInfo   = ""
        # self.__orderMenuList    = []   
        
        
    def publishCRCPrintData(self, orderId :int, orderMenuId:int  ):
        order = self.orderHandler.getOrderItemById(orderId)
        if order is None:
            CDRLog.print(f"Order with ID {orderId} not found.")
            return
        
        # 텍스트 각인 타입 주문일 경우에만 각인 정보 전송
        if order.mbrushPrintType != "text":
            time.sleep(1)
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
                                CRCKey.KEY_ORDER_ID     : order.orderId,#22 #self.__orderId,
                                CRCKey.KEY_PRINTER_MSG  : [
                                                            [
                                                                {
                                                                    CRCKey.KEY_TEXT     : "No." + str(order.orderNumber),
                                                                    CRCKey.KEY_COLOR    : "0x000000"
                                                                }
                                                            ],
                                                            [
                                                                {
                                                                    CRCKey.KEY_TEXT     : order.orderPhoneInfo,
                                                                    CRCKey.KEY_COLOR    : "0x000000"
                                                                }
                                                            ],
                                                            [
                                                                menuNamefirst,
                                                                menuNameSecond
                                                            ]
                                                        ]
                            }
        
        self.__crcComm.write(CRCKey.TOPIC_MBRUSH_RMS, json.dumps(printMsg))
        CDRLog.print(f"write MQTT : {printMsg}")   # mini test

    def publishCRCOrderRequest(self,  Quantity : int):
        reqMsgData = {
                        CRCKey.KEY_CODE: "ORDER_LIST_REQ",
                        CRCKey.KEY_STORE_ID: self.__storeId,
                        CRCKey.KEY_DATA: {"orderQuantity": Quantity}
                     }
        self.__crcComm.write(CRCKey.TOPIC_CRC_RMS, json.dumps(reqMsgData))
            

    #sendPrintCmd
    def publishCRCPrintStart(self, orderid : int) :
        '''
        각인기 mbrush 실행 명령
        '''
        # Print 명령 전달
        msg_print = {
            "reqId":"START_PRINT",
            "printerId": self.__printerId,
            "orderId": orderid
        }
        msg_str = json.dumps(msg_print)
        
        self.__crcComm.write("print/rms",msg_str)
        CDRLog.print(f"write MQTT : {msg_print}")   # mini test
        self.__printerState = None

    #getPrintState
    def getCRCPrintState(self) -> str:
        '''
        각인기 mbrush 상태 정보 반환
        '''
        return self.__printerState     