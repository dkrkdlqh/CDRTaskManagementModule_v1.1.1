import paho.mqtt.client as paho
import ssl
import time

from typing import Callable, Any

from const.event import Event

from data.mqttFilterData import MqttFilterData
from data.mainData import MainData

from cdrutils.cdrUtil import CDRUtil
from cdrutils.log import CDRLog




class MqttVar :

    KEY_TOPIC   :str = "topic"

    def __init__(self, eventCallback:Callable[[int, Any], None]) :
    
        self.__eventCallback            :Callable[[int, Any], None] = eventCallback
        self.__mqttClient               :paho.Client                = None   
        
        self.__readPacket               :dict                       = None 
        self.__readPacketList           :list[dict]                 = []

    

    def __del__(self) :
        if self.__mqttClient != None:
            self.__mqttClient.loop_stop()  # loop를 확실히 중단!
            self.__mqttClient.disconnect()
            self.__mqttClient.on_message = None  # 메시지 콜백도 제거해줘서 안전하게!
            self.__mqttClient = None

        CDRLog.print('MQTTVar instance is deleted.')



    def connect(self, addr:str, port:int, userId:str, userPW:str, topics : list, filter:MqttFilterData = None):
        
        try :
            
            self.__mqttTopics        :list                       = topics   
            self.__mqttFilter        :MqttFilterData             = filter

            self.__mqttClient = paho.Client(paho.CallbackAPIVersion.VERSION2)
            self.__mqttClient.tls_set(tls_version = ssl.PROTOCOL_TLS)
            self.__mqttClient.username_pw_set(userId, userPW)
            self.__mqttClient.on_connect        = self.onMQTTConnect
            self.__mqttClient.on_disconnect     = self.onMQTTDisconnect
            self.__mqttClient.on_subscribe      = self.onMQTTSubscribe
            self.__mqttClient.on_message        = self.onMqttMsgCallback
            
            self.__mqttClient.connect(addr,port)
            self.__mqttClient.loop_start()

        except :
            
            # 서버 연결 실패 -> 이벤트 발생
            if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                self.__eventCallback(Event.COMM_VAR_FAILED_TO_CONNECT, self)

            self.__mqttClient = None
        
    def disconnect(self):
        if self.__mqttClient is not None:
            self.__mqttClient.loop_stop()
            self.__mqttClient.on_message = None
            self.__mqttClient = None

    def setSubscribeFilter(self, filter:MqttFilterData):
        '''
        구독 데이터 필터 설정
        '''

        self.__mqttFilter = filter



    def write(self, topic:str, msg:str) :
        
        try : 
            if self.__mqttClient != None:

                self.__mqttClient.publish(topic, msg, 1)
                return True
            
            else:
                return False            
        except :
            return False
        


    def clearReadPacket(self):

        self.__readPacketList   = []
        self.__readPacket       = None



    def read(self) -> dict:
        '''
        단일 변수에 저장된 패킷 읽기
        '''
        if self.__readPacket == None:
            return None
        else:
            # read된 패킷 정보는 재사용 안되도록 호출 뒤에 초기화
            returnValue:dict = self.__readPacket.copy()
            self.__readPacket = None
        
            return returnValue
    


    def readFirstPacket(self) -> dict:
        '''
        리스트 변수에 저장된 첫번째 패킷 읽기
        '''

        if self.__readPacketList == None or len(self.__readPacketList) == 0:
            return None
        
        else:
            # CDRLog.print(f"get mqtt packet from list.... remains : {len(self.__readPacketList) - 1}")
            return self.__readPacketList.pop(0)
        
      

    def isConnected(self) -> bool:

        if self.__mqttClient != None and self.__mqttClient.is_connected() == True:
            return True
        else:
            return False
        


    def onMQTTConnect(self, client, userdata, flags, rc, properties = None):
        
        for topic in self.__mqttTopics :
            
            self.__mqttClient.subscribe(topic, 1)



    def onMQTTDisconnect(self, client, userdata, flags, rc , properties = None):
        '''
        # MQTT 연결 해제 함수
        '''
        if self.__mqttClient is not None: 
            self.__mqttClient.loop_stop()
            self.__mqttClient.on_message = None
            self.__mqttClient = None
        CDRLog.print("MqttVar disconnect B")  # 로그용!
        # 프로그램 실행 중에 mqtt 통신이 disconnect 된 상황 -> 의도하지 않은 에러 상황으로 판단하여, 이벤트 발생! 
        if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
            self.__eventCallback(Event.COMM_VAR_DISCONNECTED, self)




    def onMQTTSubscribe(self, client, userdata, mid, granted_qos, properties = None):
        '''
        # MQTT topic 구독 함수
        '''
        CDRLog.print("MQTT Subscribed")



    def onMqttMsgCallback(self, client, userdata, msg : paho.MQTTMessage):       
        '''
        # MQTT 메세지 수신 콜백 함수
        '''    

        # 수신 메세지를 json형식으로 변환
        msgDict:dict = CDRUtil.strToJson(msg.payload.decode())
        
        # 예외처리 : 필터가 존재하고, read된 데이터가 필터의 key값을 가지고 있고, 데이터와 필터의 value값이 다르면 skip
        if self.__mqttFilter != None:    
            
            key     :str    = self.__mqttFilter.getKey()
            value           = self.__mqttFilter.getValue()
            
            if key in msgDict: 
                
                if msgDict[key] != value:
                    return
        
            msgDict[MqttVar.KEY_TOPIC]      = msg.topic
            
            self.__readPacket               = msgDict
            
            # 리스트의 read 패킷 개수가 100개가 넘지 않도록 조절 
            if len(self.__readPacketList) > 100:
                self.__readPacketList.pop(0)

            self.__readPacketList.append(msgDict.copy())