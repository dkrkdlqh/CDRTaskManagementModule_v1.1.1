import threading
import json

from typing import Any 

from const.crcJsonKeyword import CRCJsonKeyword as CRCKey
from const.tpmJsonKeyword import TPMJsonKeyword as TPMKey
from const.programVarType import ProgramVarType
from const.programState import ProgramState
from const.valueAssignType import ValueAssignType
from const.commandId import CommandId
from const.operator import Operator
from const.loopType import LoopType
from const.waitType import WaitType
from const.sysFuncKeyword import SysFuncKeyword
from const.sysFuncName import SysFuncName
from const.event import Event

from variable.tcpipVar import TcpIPVar
from variable.bleVar import BLEVar
from variable.melsecPLCVar import MelsecPLCVar
from variable.modbusTCPVar import ModbusTCPVar
from variable.mqttVar import MqttVar
from variable.primitiveVar import PrimitiveVar

from cdrutils.log import CDRLog
from cdrutils.cdrUtil import CDRUtil

from manager.tpmSysFuncManager import TPMSysFuncManager

from data.mainData import MainData
from data.sysQueueData import SysQueueData

import datetime
import time


class TPMProgramManager():

    def __init__(self, mainQueue:SysQueueData, sysFunManager:TPMSysFuncManager):

        super().__init__()

        self.__mainQueue            :SysQueueData       = mainQueue
        self.__tpmSysFuncManager    :TPMSysFuncManager  = sysFunManager

        self.__initTPMVar()
        


    def __initTPMVar(self):
        '''
        # TPM-TMM 통신에 사용될 TPM 프로그램 상태 변수 초기화
        '''

        self.__curProgramNodeId             :int            = -1
        self.__curFunctionNodeId            :int            = -1
        self.__curEventNodeId               :int            = -1

        self.__programNodeList              :list[dict]     = []
        self.__programNodeDepthList         :list[int]      = []
        self.__eventNodeDepthList           :list[int]      = []
        self.__userFuncNodeDepthList        :list[int]      = []

        # TPM 선언 변수 관리 딕셔너리
        self.__userVarList                  :dict           = {}
        self.__userFuncList                 :dict           = {}
        self.__userEventList                :dict           = {}
        # TPM 모니터링용 일반타입 변수 관리 리스트
        self.__monitoringVarNameList        :list[str]      = []

        self.__ifExecutionListInProgram     :list[bool]     = []
        self.__ifExecutionListInEvent       :list[bool]     = []
        self.__ifExecutionListInUserFunc    :list[bool]     = []

        # loopBreak 명령 신호
        self.__doLoopBreak                  :bool           = False
        # self.__goToBookmarkNodeId           :int            = -1
        # self.__bookmarkSearchMode           :bool           = False    

        # self.__bookmarkNodeDictionary       :dict           = {}
                    



    def __tpmProgramRunningThreadHandler(self, programData:dict):
        '''
        TPM으로 작성된 사용자 프로그램 처리 쓰레드
        '''

        self.__tpmSysFuncManager.initSysFuncVar()   


        self.__programNodeList              = programData[TPMKey.TREE_PROGRAM]
        self.__eventNodeList                = programData[TPMKey.TREE_EVENT]
        self.__userFuncNodeList              = programData[TPMKey.TREE_FUNC]
        self.__monitoringVarNameList        = []

        self.__curEventNodeId               = -1
        self.__curFunctionNodeId            = -1
        self.__curProgramNodeId             = -1

        self.__doLoopBreak                  = False
        # self.__goToBookmarkNodeId           = -1

        # 각 항목에서 마지막 node id 검색
        lastProgramNodeId   :int = self.__getMaxNodeId(self.__programNodeList)
        CDRLog.print(f"[10%] 마지막 프로그램 노드 id값 : {lastProgramNodeId}")
        # 프로그램 노드의 depth 관리 리스트 생성
        self.__programNodeDepthList         = [-1] * (lastProgramNodeId + 1)

        # 모든 program 노드를 검사하여, 노드별 depth 정보와 북마크 정보를 저장. ---------------------------
        for programNode in self.__programNodeList:
            self.__renewalNodeDepthInfo(programNode, self.__programNodeDepthList)
            # self.__checkBookmarkNode(programNode, self.__bookmarkNodeDictionary)

        CDRLog.print(f"[20%] 프로그램 트리의 각 노드별 뎁스 정보 : {self.__programNodeDepthList}")
        # CDRLog.print(f"프로그램 트리의 북마크 노드 위치 정보 : {self.__bookmarkNodeDictionary}")

        # 조건식 depth 관리 리스트 생성 (현 프로그램 데이터의 최고 노드 depth 크기만큼 선언)
        self.__ifExecutionListInProgram = [False] * (max(self.__programNodeDepthList) + 1)
        CDRLog.print(f"[30%] self.__ifExecutionListInProgram : {self.__ifExecutionListInProgram}")
        

        # 모든 Event 노드를 검사하여, 노드별 depth 정보와 북마크 정보를 저장. -----------------------------
        # 각 항목에서 마지막 node id 검색
        lastEventNodeId   :int = self.__getMaxNodeId(self.__eventNodeList)
        # 프로그램 노드의 depth 관리 리스트 생성
        self.__eventNodeDepthList         = [-1] * (lastEventNodeId + 1)

        for eventNode in self.__eventNodeList:
            self.__renewalNodeDepthInfo(eventNode, self.__eventNodeDepthList)

        self.__ifExecutionListInEvent = [False] * (max(self.__eventNodeDepthList) + 1)
        CDRLog.print(f"[40%] self.__ifExecutionListInEvent : {self.__ifExecutionListInEvent}")

        # 모든 User func 노드를 검사하여, 노드별 depth 정보와 북마크 정보를 저장. --------------------------
        # 각 항목에서 마지막 node id 검색
        lastUserFuncNodeId   :int = self.__getMaxNodeId(self.__userFuncNodeList)
        # 프로그램 노드의 depth 관리 리스트 생성
        self.__userFuncNodeDepthList         = [-1] * (lastUserFuncNodeId + 1)

        for userFuncNode in self.__userFuncNodeList:
            self.__renewalNodeDepthInfo(userFuncNode, self.__userFuncNodeDepthList)

        self.__ifExecutionListInUserFunc = [False] * (max(self.__userFuncNodeDepthList) + 1)
        CDRLog.print(f"[50%]self.__ifExecutionListInUserFunc : {self.__ifExecutionListInUserFunc}")


        MainData.isRunningTPMProgram        = True
        CDRLog.print(f"[60%] user vars create start")
        self.__createUserVars(programData[TPMKey.TREE_VARIABLE])
        CDRLog.print(f"[80%] user vars create complete")
        self.__createUserFuncs(programData[TPMKey.TREE_FUNC])
        CDRLog.print(f"[90%] user Func create complete")
        self.__createUserEvents(programData[TPMKey.TREE_EVENT])
        

        # while True:

        #     self.__startProgram(self.__goToBookmarkNodeId)

        #     # goto 명령없으면 정상적으로 프로그램 수행을 모두 완료 했다고 판단하여, 현재의 while에서 break.
        #     # goto 명령있다면 다시 돌아가서 북마크위치에서 프로그램 수행 시작.
        #     if self.__goToBookmarkNodeId == -1:
        #         break
        CDRLog.print(f"[100%] Program Node Run")
        # 순차적으로 프로그램 노드 실행 ---------------------------
        for node in self.__programNodeList :
            
            if MainData.isRunningTPMProgram == False:
                break

            self.__executeProgramNode(node)
        # -------------------------------------------------------
        
        self.__stopProgram()

        CDRLog.print("============ __tpmProgramRunningThreadHandler terminated...")



    # TPM에서 GoTo 명령 노드를 제공할 경우, 해당 함수 사용
    def __startProgram(self, gotoBookmarkNodeId:int):
        
        # goTo 명령이 없는 상태 -> 처음부터 순차적으로 프로그램 노드 실행
        if gotoBookmarkNodeId == -1:    
        
            for node in self.__programNodeList:
                
                if MainData.isRunningTPMProgram == False:
                    break

                # goto 명령이 발생하면 break!
                if self.__goToBookmarkNodeId != -1:
                    break

                self.__executeProgramNode(node)
        
        # goTo 명령 발동된 상태 -> 타겟 북마크 노드로 이동 -> 해당 위치부터 순차적으로 프로그램 노드 실행
        else:
            
            self.__bookmarkSearchMode = True

            for node in self.__programNodeList :
                
                if MainData.isRunningTPMProgram == False:
                    break

                if self.__bookmarkSearchMode == True:
                    
                    self.__searchAndExecuteNode(node) 
                    
                else:

                    # 다시 goto 명령이 발생하면 break!
                    if self.__goToBookmarkNodeId != -1:
                        break

                    self.__executeProgramNode(node)



    
                
    # TPM에서 GoTo 명령 노드를 제공할 경우, 해당 함수 사용
    def __searchAndExecuteNode(self, node:dict):
        '''
        TPM Program Node 실행 함수
        '''
        if MainData.isRunningTPMProgram == False:
            return
        
        # 북마크 서칭 모드 -------------------------------------------
        if self.__bookmarkSearchMode == True:

            curNodeId   :int = node[TPMKey.DEFAULT_NODE_ID]
            cmdId       :str = node[TPMKey.DEFAULT_CMD_ID]
            
            # 타겟 북마크 노드에 도달하면 -> 북마크 노드 id값은 초기화 & 서칭 모드는 off
            if self.__goToBookmarkNodeId == curNodeId:
                self.__goToBookmarkNodeId = -1
                self.__bookmarkSearchMode = False
                
            else:
                childNodeList:list[dict] = node[TPMKey.DEFAULT_CHILD_NODE_LIST]

                if len(childNodeList) > 0:
                    # if/elseIf 노드의 자식들을 서칭할 경우, 조건문 모드를 True로
                    if cmdId == CommandId.IF or cmdId == CommandId.ELIF:
                                
                        nodeDepth = self.__programNodeDepthList[curNodeId]
                        self.__ifExecutionListInProgram[nodeDepth] = True

                    for child in childNodeList:                    
                        self.__searchAndExecuteNode(child) 

                    # 서칭모드에서 if/elseIf 노드의 자식들을 서칭 완료한 경우, 조건문 모드를 다시 False로
                    if self.__bookmarkSearchMode == True:
                        if cmdId == CommandId.IF or cmdId == CommandId.ELIF:
                            nodeDepth = self.__programNodeDepthList[curNodeId]
                            self.__ifExecutionListInProgram[nodeDepth] = False
                
        # 일반 노드 실행 모드 ----------------------------------------
        else:
            
            if MainData.isRunningTPMProgram == False:
                return

            # goto 명령이 발생하면 break!
            if self.__goToBookmarkNodeId != -1:
                return

            self.__executeProgramNode(node)
                    
            


    def __stopProgram(self):
        '''
        프로그램 정지 처리
        '''
        
        MainData.isRunningTPMProgram    = False
        MainData.isPausedTPMProgram     = False

        self.__curProgramNodeId         = -1
        self.__curFunctionNodeId        = -1
        self.__curEventNodeId           = -1
        
        self.__removeAllUserVars()
        self.__removeAllUserFuncs()
        self.__removeAllUserEvents()


        self.__tpmSysFuncManager.initSysFuncVar()

        





    def __getMaxNodeId(self, nodeDataList:list[dict], startNodeId:int = -1) -> int:
        '''
        ### 노드 리스트에서 마지막(가장 큰 값의) NodeId 값 찾기
        '''
        maxNodeId   :int    = startNodeId      
        nodeData    :dict   = {}
        
        for i in range(len(nodeDataList)):

            nodeData = nodeDataList[i]

            if TPMKey.DEFAULT_NODE_ID in nodeData:
                nodeId:int = nodeData[TPMKey.DEFAULT_NODE_ID]
                if nodeId > maxNodeId:
                    maxNodeId = nodeId

            if TPMKey.DEFAULT_CHILD_NODE_LIST in nodeData:
                maxNodeId = self.__getMaxNodeId(nodeData[TPMKey.DEFAULT_CHILD_NODE_LIST], maxNodeId)

        return maxNodeId
    


    def __renewalNodeDepthInfo(self, node:dict, nodeDepthList:list[int], depth:int = 0):
        '''
        ### 노드별 depth 정보 갱신
        '''
        node_id = node[TPMKey.DEFAULT_NODE_ID]
        # print(node_id)
        
        # nodeId가 아직 계층에 기록되지 않았다면 기록
        if nodeDepthList[node_id] == -1:
            nodeDepthList[node_id] = depth
        
        # 자식 노드가 있다면 재귀적으로 처리
        for child in node.get(TPMKey.DEFAULT_CHILD_NODE_LIST, []):
            self.__renewalNodeDepthInfo(child, nodeDepthList, depth + 1)



    def __checkBookmarkNode(self, node:dict, bookmarkNodeDictionary:dict):
        '''
        ### 북마크 노드 정보 저장
        '''
        cmdId = node[TPMKey.DEFAULT_CMD_ID]
       
        # 북마크 노드가 존재한다면, dictionary에 북마크 이름을 key로, 노드id를 value로 저장
        if cmdId == CommandId.BOOKMARK:
            bookmarkNodeDictionary[node[TPMKey.BOOK_MARKNAME]] = node[TPMKey.DEFAULT_NODE_ID]
        
        # 자식 노드가 있다면 재귀적으로 처리
        for child in node.get(TPMKey.DEFAULT_CHILD_NODE_LIST, []):
            self.__checkBookmarkNode(child, bookmarkNodeDictionary)



    def __createUserEvents(self, userEventNodeDataList:list[dict]):
        '''
        ### TPM 사용자 이벤트 생성
        '''

        self.__userEventList    = {}
        eventNode   :dict       = {} 
        eventName   :str        = ""

        for i in range(len(userEventNodeDataList)):
            
            eventNode = userEventNodeDataList[i]
            if eventNode["cmdId"] == "Empty" :
                break

            eventName = f'event_{i}'
            self.__userEventList[eventName] = self.__createEvent(eventName, eventNode, 0)

        for eventName in self.__userEventList.keys():
            threading.Thread(target = self.__userEventList[eventName]).start()



    def __createUserFuncs(self, userFuncNodeDataList:list[dict]):
        '''
        ### TPM 사용자 함수 생성
        '''
        self.__userFuncList = {}

        for function in userFuncNodeDataList:      
            
            if function[TPMKey.DEFAULT_CMD_ID] == "Empty" :
                continue

            funcName            :str        = function[TPMKey.DEFAULT_FUNC_NAME]
            self.__userFuncList[funcName]   = self.__createFunc(function, 0, self.__userVarList)



    def __createFunc(self, function_node, nodeDepth,variables):

        '''
        TPM Function 생성
        '''
        def function():
            for child in function_node[TPMKey.DEFAULT_CHILD_NODE_LIST]:
                self.__executeFuncNode(child)

        return function



    def __createUserVars(self, variableNodeDataList:list[dict]):
        '''
        ### TPM 프로그램 변수 생성
        '''
        self.__userVarList = {}

        for varNodeData in variableNodeDataList:

            if TPMKey.VAR_TYPE in varNodeData:

                varType :str    = varNodeData[TPMKey.VAR_TYPE]
                enable  :bool   = varNodeData[TPMKey.DEFAULT_ENABLE]

                # 활성화 노드에서 정의된 변수만 생성
                if enable == False:
                    continue
                
                if varType == ProgramVarType.TYPE_TCP_IP:
                    
                    varName         :str        = varNodeData[TPMKey.VAR_NAME]
                    varIPAddr       :str        = varNodeData[TPMKey.VAR_IP_ADDR]
                    varIPPort       :int        = varNodeData[TPMKey.VAR_IP_PORT]
                    
                    tcpIpVar        :TcpIPVar   = TcpIPVar(self.commVarEventCallback)
                    self.__userVarList[varName] = tcpIpVar
                    # 통신 변수 생성 및 저장 후, 연결 진행
                    tcpIpVar.connect(varIPAddr, varIPPort)
                
                elif varType == ProgramVarType.TYPE_MODBUS_TCP:
                    
                    varName         :str        = varNodeData[TPMKey.VAR_NAME]
                    varIPAddr       :str        = varNodeData[TPMKey.VAR_IP_ADDR]
                    varIPPort       :int        = varNodeData[TPMKey.VAR_IP_PORT]
                    
                    modbusVar   :ModbusTCPVar   = ModbusTCPVar(self.commVarEventCallback)
                    self.__userVarList[varName] = modbusVar
                    modbusVar.connect(varIPAddr, varIPPort)

                    # # 통신 연결 성공 후, 다음 단계 진행
                    # while MainData.isRunningTPMProgram == True:
                    #     if modbusVar.isConnected() == True:
                    #         break
                
                elif varType == ProgramVarType.TYPE_MELSEC_PLC:
                    
                    varName         :str        = varNodeData[TPMKey.VAR_NAME]
                    varIPAddr       :str        = varNodeData[TPMKey.VAR_IP_ADDR]
                    varIPPort       :int        = varNodeData[TPMKey.VAR_IP_PORT]
                    
                    melsecPLCVar:MelsecPLCVar   = MelsecPLCVar(self.commVarEventCallback)
                    self.__userVarList[varName] = melsecPLCVar
                    melsecPLCVar.connect(varIPAddr, varIPPort)

                    # 통신 연결 성공 후, 다음 단계 진행
                    while MainData.isRunningTPMProgram == True:
                        if melsecPLCVar.isConnected() == True:
                            break

                elif varType == ProgramVarType.TYPE_BLE:
                    
                    varName         :str        = varNodeData[TPMKey.VAR_NAME]
                    varMACAddr      :str        = varNodeData[TPMKey.VAR_BLE_MAC_ADDR]
                    varServUUID     :str        = varNodeData[TPMKey.VAR_BLE_SERVICE_UUID]
                    varCharUUID     :str        = varNodeData[TPMKey.VAR_BLE_CHARACTERISTIC_UUID]
                    varDescUUID     :str        = varNodeData[TPMKey.VAR_BLE_DESCRIPTOR_UUID]

                    bleVar:BLEVar               = BLEVar(self.commVarEventCallback)
                    self.__userVarList[varName] = bleVar
                    bleVar.connect(varMACAddr, varServUUID, varCharUUID,  varDescUUID)

                    # 통신 연결 성공 후, 다음 단계 진행
                    while MainData.isRunningTPMProgram == True:
                        if bleVar.isConnected() == True:
                            break

                elif varType == ProgramVarType.TYPE_MQTT:
                    
                    varName         :str        = varNodeData[TPMKey.VAR_NAME]
                    varIPAddr       :str        = varNodeData[TPMKey.VAR_IP_ADDR]
                    varIPPort       :int        = varNodeData[TPMKey.VAR_IP_PORT]
                    varUserName     :str        = varNodeData[TPMKey.VAR_MQTT_USER_NAME]
                    varUserPW       :str        = varNodeData[TPMKey.VAR_MQTT_USER_PW]

                    rawTopic        :str        = f'[{varNodeData[TPMKey.VAR_MQTT_SUBSCRIBE_TOPIC]}]'
                    stringList      :list[str]  = rawTopic.strip('[]').split(',')
                    topics          :list[str]  = [f'{item}' for item in stringList]
                    
                    mqttVar         :MqttVar    = MqttVar(self.commVarEventCallback)
                    self.__userVarList[varName] = mqttVar

                    # 통신 변수 생성 및 저장 후, 연결 진행
                    mqttVar.connect(varIPAddr, varIPPort, varUserName, varUserPW, topics)

                elif varType == 'dhgripper' :
                    
                    varName         :str        = varNodeData[TPMKey.VAR_NAME]
                    varIPAddr       :str        = varNodeData[TPMKey.VAR_IP_ADDR]
                    varIPPort       :int        = varNodeData[TPMKey.VAR_IP_PORT]
                    
                    self.__userVarList[varName] = TcpIPVar(varIPAddr, varIPPort)
                
                    
                
                elif varType == 'fr' :
                    
                    varName         :str        = varNodeData[TPMKey.VAR_NAME]
                    varIPAddr       :str        = "192.168.3.100" # node[TPMKey.VAR_IP_ADDR]
                    varIPPort       :int        = varNodeData[TPMKey.VAR_IP_PORT]
                    
                    self.__userVarList[varName] = TcpIPVar(varIPAddr, varIPPort)

                else : # 일반 변수 타입
                    
                    varName         :str        = varNodeData[TPMKey.VAR_NAME]
                    varValue                    = varNodeData[TPMKey.VAR_VALUE]

                    self.__userVarList[varName] = PrimitiveVar(varValue)
                    self.__monitoringVarNameList.append(varName)  


    def commVarEventCallback(self, eventId:int, data:Any):

        # 연결된 통신 상태가 갑자기 disconnect
        if eventId == Event.COMM_VAR_DISCONNECTED:

            varName = self.__getCommVarName(data)

            if varName != None:
                jsonData:dict       = {}
                jsonData["eventId"] = eventId
                jsonData["msg"]     = f"{CDRUtil.getCommVarTypeStr(type(data))} 타입 통신변수 '{varName}'의 연결이 끊어졌습니다.\n실행 중인 프로그램을 강제로 종료합니다."
                self.__mainQueue.put(SysQueueData(SysQueueData.ERR_COMM_VAR_CONNECTION, jsonData))
                #mini 250114 임시 테스트
                CDRLog.print(f"{CDRUtil.getCommVarTypeStr(type(data))} 타입 통신변수 '{varName}'의 연결이 끊어졌습니다.\n실행 중인 프로그램을 강제로 종료합니다.")

        elif eventId == Event.COMM_VAR_FAILED_TO_CONNECT:
            
            varName = self.__getCommVarName(data)
           
            if varName != None:
                
                jsonData:dict       = {}
                jsonData["eventId"] = eventId
                jsonData["msg"]     = f"{CDRUtil.getCommVarTypeStr(type(data))} 타입 통신변수 '{varName}'의 연결 작업에 실패했습니다.\n실행 중인 프로그램을 강제로 종료합니다."
                self.__mainQueue.put(SysQueueData(SysQueueData.ERR_COMM_VAR_CONNECTION, jsonData))
                #mini 250114 임시 테스트
                CDRLog.print(f"{CDRUtil.getCommVarTypeStr(type(data))} 타입 통신변수 '{varName}'의 연결이 실패했습니다.\n실행 중인 프로그램을 강제로 종료합니다.")



    def __getCommVarName(self, var:Any) -> str:

        for varName in self.__userVarList.keys():
            
            if self.__userVarList[varName] == var:
                return varName
            
        return None


    def __executeNode(self, treeType, node, nodeDepth):   
        '''
        ### TPM 프로그램의 노드 실행 함수\n
        treeType : Program, Event, Function\n
        node : 실행 노드\n
        nodeDepth : 노드 계층(0~)\n
        '''     
        curTime = datetime.datetime.now()


        # Pause 명령에는 아래의 while문에서 대기.
        while MainData.isRunningTPMProgram == True and MainData.isPausedTPMProgram == True:

            newTime         = datetime.datetime.now()
            elapseTime      = newTime - curTime

            if elapseTime.total_seconds() > 1 :

                CDRLog.print(f"Paused in No.{self.__curProgramNodeId + 1} Node")
                curTime = newTime



        # 노드에 선언된 명령어 id값을 변수에 할당
        cmdId :str = node[TPMKey.DEFAULT_CMD_ID]

        # ------------------------------------------------------------------------------------------------------
        # Assignment 명령어 노드 실행 ---------------------------------------------------------------------------
        if cmdId == CommandId.ASSIGNMENT:

            targetAssignVar :PrimitiveVar   = self.__userVarList[node[TPMKey.ASSIGN_VAR_NAME]]
            mathOperator    :str            = node[TPMKey.ASSIGN_VAR_MATH_OPERATOR]
            assignType      :str            = node[TPMKey.ASSIGN_TYPE]
            readVar         :PrimitiveVar   = None
            indexVar        :PrimitiveVar   = None

            if mathOperator != "": # 연산자 有

                # 타겟 변수에 직접 입력한 값을 연산하여 할당    
                if assignType == ValueAssignType.INPUT: 
                    targetAssignVar.mathOperate(mathOperator, node[TPMKey.ASSIGN_VAR_VALUE])

                # 타겟 변수에 다른 변수의 값을 연산하여 할당 
                elif assignType == ValueAssignType.VAR: 
                    readVar = self.__userVarList[node[TPMKey.ASSIGN_READ_VAR_NAME]]
                    targetAssignVar.mathOperate(mathOperator, readVar.getValue())

            else : # 연산자 無
                
                if assignType == ValueAssignType.INPUT: 
                    
                    # 타겟 배열 변수에 직접 입력한 배열 값을 특정 인덱스부터 할당 
                    if "Array" in node[TPMKey.ASSIGN_VAR_TYPE] :
                        
                        inputValueList:list = node[TPMKey.ASSIGN_VAR_VALUE]
                        
                        startIndexType  :str = node[TPMKey.ASSIGN_VAR_ARR_START_INDEX_TYPE]
                        startIndex      :int = 0
                        
                        if startIndexType == ValueAssignType.INPUT: 
                            startIndex = int(node[TPMKey.ASSIGN_VAR_ARR_START_INDEX_VALUE])

                        elif startIndexType == ValueAssignType.VAR:
                            indexVar    = self.__userVarList[node[TPMKey.ASSIGN_VAR_ARR_START_INDEX_VAR_NAME]] 
                            startIndex  = indexVar.getValue() 

                        endIndex        :int = startIndex + len(inputValueList)
                        targetAssignVar.setListValue(startIndex, endIndex, inputValueList)

                    # 타겟 변수에 직접 입력한 값을 할당 
                    else :
                        targetAssignVar.setValue(node[TPMKey.ASSIGN_VAR_VALUE])

                # 타겟 변수에 다른 변수의 값을 할당 
                elif assignType == ValueAssignType.VAR:
                    
                    readVar = self.__userVarList[node[TPMKey.ASSIGN_READ_VAR_NAME]]
                    targetAssignVar.setValue(readVar.getValue())        
        
            # print(f"targetAssignVar : {node[TPMKey.ASSIGN_VAR_NAME]} -> {targetAssignVar.getValue()}")

        # If 명령어 노드 실행 ---------------------------------------------------------------------------
        elif cmdId == CommandId.IF:

            conditionResult :bool = self.__getConditionResult(node)
            
            if treeType == TPMKey.TREE_PROGRAM:
                self.__ifExecutionListInProgram[nodeDepth]  = conditionResult
            elif treeType == TPMKey.TREE_EVENT:
                self.__ifExecutionListInEvent[nodeDepth]    = conditionResult
            elif treeType == TPMKey.TREE_FUNC:
                self.__ifExecutionListInUserFunc[nodeDepth] = conditionResult
            
            # 조건식이 결과가 참이면, 자식 노드 실행
            if conditionResult == True:
                
                for childNode in node[TPMKey.DEFAULT_CHILD_NODE_LIST]:
                    
                    if MainData.isRunningTPMProgram == False:
                        break

                    #트리타입에 맞게 자식 노드 실행
                    self.__executeTargetTreeNode(treeType, childNode)


        elif cmdId == CommandId.ELIF:
            
            # print(f"---nodeDepth : {nodeDepth}")
            prevConditionResult :bool = False
            if treeType == TPMKey.TREE_PROGRAM:
                prevConditionResult = self.__ifExecutionListInProgram[nodeDepth]
            elif treeType == TPMKey.TREE_EVENT:
                prevConditionResult = self.__ifExecutionListInEvent[nodeDepth]
            elif treeType == TPMKey.TREE_FUNC:
                prevConditionResult = self.__ifExecutionListInUserFunc[nodeDepth]

            # 이전에 위치한 if 또는 else if 조건이 모두 false인 경우에만 진행 
            if prevConditionResult == False:
                
                conditionResult :bool = self.__getConditionResult(node)
                
                if treeType == TPMKey.TREE_PROGRAM:
                    self.__ifExecutionListInProgram[nodeDepth]  = conditionResult
                elif treeType == TPMKey.TREE_EVENT:
                    self.__ifExecutionListInEvent[nodeDepth]    = conditionResult
                elif treeType == TPMKey.TREE_FUNC:
                    self.__ifExecutionListInUserFunc[nodeDepth] = conditionResult
                
                # 조건식이 결과가 참이면, 자식 노드 실행
                if conditionResult == True:
                    
                    for childNode in node[TPMKey.DEFAULT_CHILD_NODE_LIST]:
                        
                        if MainData.isRunningTPMProgram == False:
                            break

                        #트리타입에 맞게 자식 노드 실행
                        self.__executeTargetTreeNode(treeType, childNode)

    
        # Else 명령어 노드 실행 ---------------------------------------------------------------------------
        elif cmdId == CommandId.ELSE:

            prevConditionResult :bool = False
            if treeType == TPMKey.TREE_PROGRAM:
                prevConditionResult = self.__ifExecutionListInProgram[nodeDepth]
            elif treeType == TPMKey.TREE_EVENT:
                prevConditionResult = self.__ifExecutionListInEvent[nodeDepth]
            elif treeType == TPMKey.TREE_FUNC:
                prevConditionResult = self.__ifExecutionListInUserFunc[nodeDepth]


            # 이전에 위치한 if 또는 else if 조건이 모두 false인 경우에만 진행
            if prevConditionResult == False:

                for childNode in node[TPMKey.DEFAULT_CHILD_NODE_LIST]:

                    if MainData.isRunningTPMProgram == False:
                        break
                    
                    #트리타입에 맞게 자식 노드 실행
                    self.__executeTargetTreeNode(treeType, childNode)
        
        # Loop 명령어 노드 실행 ---------------------------------------------------------------------------
        elif cmdId == CommandId.LOOP:

            loopType:str = node[TPMKey.LOOP_TYPE]

            if loopType == LoopType.COUNT:

                for i in range(node[TPMKey.LOOP_COUNT]):

                    if MainData.isRunningTPMProgram == False:
                        break
                    
                    if self.__doLoopBreak == True:
                        self.__doLoopBreak = False 
                        break
                    
                    for childNode in node[TPMKey.DEFAULT_CHILD_NODE_LIST]:

                        if MainData.isRunningTPMProgram == False:
                            break

                        if self.__doLoopBreak == True:
                            break
                        
                        #트리타입에 맞게 자식 노드 실행
                        self.__executeTargetTreeNode(treeType, childNode)

            elif loopType == LoopType.VAR:

                loopCountVar    :PrimitiveVar   = self.__userVarList[node[TPMKey.LOOP_VAR_NAME]]    
                count           :int            = loopCountVar.getValue()
                
                for i in range(0,count):

                    if MainData.isRunningTPMProgram == False:
                        break
                    
                    if self.__doLoopBreak :
                        self.__doLoopBreak =False 
                        break

                    for childNode in node[TPMKey.DEFAULT_CHILD_NODE_LIST]:
                        
                        if MainData.isRunningTPMProgram == False:
                            break

                        if self.__doLoopBreak :
                            break
                        #트리타입에 맞게 자식 노드 실행
                        self.__executeTargetTreeNode(treeType, childNode)

            elif loopType == LoopType.ALWAYS:

                while True:
                    
                    if MainData.isRunningTPMProgram == False:
                        break

                    if self.__doLoopBreak :
                        self.__doLoopBreak = False
                        break

                    for childNode in node[TPMKey.DEFAULT_CHILD_NODE_LIST]:
                        
                        if MainData.isRunningTPMProgram == False:
                            break

                        if self.__doLoopBreak :
                            break
                        
                        #트리타입에 맞게 자식 노드 실행
                        self.__executeTargetTreeNode(treeType, childNode)
        
        # Break 명령어 노드 실행 ---------------------------------------------------------------------------
        elif cmdId == CommandId.BREAK:

            self.__doLoopBreak = True
        
        # Wait 명령어 노드 실행 ---------------------------------------------------------------------------
        elif cmdId == CommandId.WAIT:

            waitOption :str = node[TPMKey.WAIT_OPTION]

            # 입력 시간만큼 대기
            if waitOption == WaitType.TIME:    

                startWaitTime           = datetime.datetime.now()
                targetWaitTime  :float  = node[TPMKey.WAIT_TIME_VALUE]

                while True :
                    
                    if MainData.isRunningTPMProgram == False:
                        break

                    curTime             = datetime.datetime.now()                    
                    waitingTime         = curTime - startWaitTime

                    if waitingTime.total_seconds() > targetWaitTime:
                        break
                    else :
                        # Wait 명령 검사 주기 0.1초
                        time.sleep(0.1)
            
            # 조건식 만족할때까지 대기
            elif waitOption == WaitType.CONDITION:

                while self.__getConditionResult(node) == False:
                    
                    if MainData.isRunningTPMProgram == False:
                        break

                    # Wait 명령 검사 주기 0.1초        
                    time.sleep(0.1)

        
        # CallFunc 명령어 노드 실행 ---------------------------------------------------------------------------
        elif cmdId == CommandId.CALLFUNC:

            funcName:str = node[TPMKey.FUNC_NAME]
            
            # 호출 함수가 시스템 함수인 경우,
            for sysfuncData in self.__tpmSysFuncManager.getSysFuncList():
                
                if sysfuncData.getFuncName() == funcName:
                    
                    self.__runSystemFunc(node)
                    return 0
            
            # 호출 함수가 사용자 함수인 경우
            if funcName in self.__userFuncList:

                self.__userFuncList[funcName]()

                # 사용자 함수 호출 후엔 function 트리 노드 인덱스를 초기화
                self.__curFunctionNodeId = -1
            
        
        # Terminate 명령어 노드 실행 ---------------------------------------------------------------------------
        elif cmdId == CommandId.TERMINATE:

            MainData.isRunningTPMProgram = False

        # GoTo 명령어 노드 실행 ---------------------------------------------------------------------------
        # elif cmdId == CommandId.GOTO:
            
        #     targetBookmarkName :str = node[TPMKey.BOOK_MARKNAME]
            
        #     # 타겟 북마크 이름을 가진 노드가 트리에 존재한다면, GoTo 명령어 발동.
        #     if targetBookmarkName in self.__bookmarkNodeDictionary:
        #         self.__goToBookmarkNodeId     = self.__bookmarkNodeDictionary[targetBookmarkName]
                
        
        # Read 명령어 노드 실행 ---------------------------------------------------------------------------
        elif cmdId == CommandId.READ:

            readType        :str            = node[TPMKey.READ_VAR_TYPE]
            saveVar         :PrimitiveVar   = self.__userVarList[node[TPMKey.SAVE_VAR_NAME]]
            
            if readType == ProgramVarType.TYPE_MODBUS_TCP:

                modbusFuncCode          :str            = node[TPMKey.READ_VAR_MODBUS_FUNC_CODE]
                
                saveVarType             :type           = type(saveVar.getValue())

                readModbusVar           :ModbusTCPVar   = self.__userVarList[node[TPMKey.READ_VAR_NAME]]
                readMemoryAddr          :int            = node[TPMKey.READ_VAR_MODBUS_ADDR]    
                readDataNum             :int            = node[TPMKey.READ_VAR_MODBUS_DATA_NUM]
                readModbusDataValue     :list           = None

                # 데이터 read가 성공할때까지(!= None) 계속 시도
                while MainData.isRunningTPMProgram == True:

                    readModbusDataValue = readModbusVar.read(modbusFuncCode, readMemoryAddr, readDataNum)
                    
                    if readModbusDataValue == None:
                        time.sleep(0.1)
                        CDRLog.print("modbus 변수 read 실패")
                    else:
                        print(f"===== read value is : {readModbusDataValue}")
                        # 저장 변수가 리스트 타입인 경우,
                        if saveVarType == list:
                            saveVar.setValue(readModbusDataValue)
                        # 저장 변수가 리스트 타입이 아닌 경우,
                        else:
                            saveVar.setValue(readModbusDataValue[0])
                        
                        # while문 종료 
                        break

            elif readType == ProgramVarType.TYPE_TCP_IP:

                readTcpIpVar            :TcpIPVar       = self.__userVarList[node[TPMKey.READ_VAR_NAME]]
                readTCPDataValue        :str            = None

                # 데이터 read가 성공할때까지(!= None) 계속 시도
                while MainData.isRunningTPMProgram == True:

                    readTCPDataValue = readTcpIpVar.read()
                    
                    if readTCPDataValue == None:
                        time.sleep(0.1)
                        CDRLog.print("TCP/IP 변수 read 실패")
                    else:
                        saveVar.setValue(readTCPDataValue)
                        # while문 종료
                        break
            
            elif readType == ProgramVarType.TYPE_MQTT:

                readMQTTVar         :MqttVar    = self.__userVarList[node[TPMKey.READ_VAR_NAME]]
                readMQTTDataValue   :dict       = None   
                
                # 이전의 read 데이터 패킷을 모두 초기화 
                readMQTTVar.clearReadPacket()

                # 데이터 read가 성공할때까지(!= None) 계속 시도
                while MainData.isRunningTPMProgram == True:

                    readMQTTDataValue = readMQTTVar.read()

                    if readMQTTDataValue == None:
                        time.sleep(0.1)
                        CDRLog.print("MQTT 변수 read 실패")
                    else:
                        saveVar.setValue(readMQTTDataValue)
                        # while문 종료
                        break

            elif readType == ProgramVarType.TYPE_MELSEC_PLC:

                readMelsecPLCVar        :MelsecPLCVar   = self.__userVarList[node[TPMKey.READ_VAR_NAME]]
                readPLCAddr             :str            = node[TPMKey.READ_VAR_PLC_ADDR]    
                readPLCDataNum          :int            = node[TPMKey.READ_VAR_PLC_DATA_NUM]
                readPLCDataValue        :list[int]      = None

                # 데이터 read가 성공할때까지(!= None) 계속 시도
                while MainData.isRunningTPMProgram == True:

                    readPLCDataValue = readMelsecPLCVar.read(readPLCAddr, readPLCDataNum)

                    if readPLCDataValue == None:
                        time.sleep(0.1)
                        CDRLog.print("PLC 변수 read 실패")
                    else:
                        saveVar.setValue(readPLCDataValue)
                        # while문 종료
                        break

            elif readType == ProgramVarType.TYPE_BLE:

                readBLEVar              :BLEVar         = self.__userVarList[node[TPMKey.READ_VAR_NAME]]
                readBLEDataValue        :bytes          = None   
                readCount               :int            = 0
                
                # read 데이터 패킷을 초기화 
                readBLEVar.clearReadPacket()
                # CDRLog.print(f"{node[TPMKey.READ_VAR_NAME]} 변수 read 시도")
                # 데이터 read가 성공할때까지(!= None) 계속 시도
                while MainData.isRunningTPMProgram == True:

                    readBLEDataValue = readBLEVar.read()

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
                            readBLEVar.reWrite()

                    else:
                        
                        saveVar.setValue(readBLEDataValue)
                        break


        # Write 명령어 노드 실행 ---------------------------------------------------------------------------
        elif cmdId == CommandId.WRITE:

            writeType        :str = node[TPMKey.WRITE_VAR_TYPE]

            if writeType == ProgramVarType.TYPE_MODBUS_TCP:

                modbusFuncCode      :str            = node[TPMKey.WRITE_MODBUS_FUNC_CODE]
                writeModbusVar      :ModbusTCPVar   = self.__userVarList[node[TPMKey.WRITE_VAR_NAME]]
                writeMemoryAddr     :int            = node[TPMKey.WRITE_MODBUS_ADDR]    
                writeDataList       :list           = node[TPMKey.WRITE_MODBUS_VALUE_LIST]
                writeModbusResult   :bool           = False
                
                while MainData.isRunningTPMProgram == True:
                   
                    writeModbusResult = writeModbusVar.write(modbusFuncCode, writeMemoryAddr, writeDataList)

                    if writeModbusResult == False:
                        time.sleep(0.1)
                        CDRLog.print("modbus 변수 write 실패")
                    else:
                        break

            elif writeType == ProgramVarType.TYPE_TCP_IP:

                writeTCPVar         :TcpIPVar       = self.__userVarList[node[TPMKey.WRITE_VAR_NAME]]
                writeData           :str            = node[TPMKey.WRITE_VAR_VALUE]   
                writeTcpIpResult    :bool           = False        

                while MainData.isRunningTPMProgram == True:
                    writeTcpIpResult = writeTCPVar.write(writeData)

                    if writeTcpIpResult == False:
                        time.sleep(0.1)
                        CDRLog.print("TCP/IP 변수 write 실패")
                    else:
                        break    

            elif writeType == ProgramVarType.TYPE_MQTT:

                writeMQTTVar        :MqttVar        = self.__userVarList[node[TPMKey.WRITE_VAR_NAME]]
                writeTopic          :str            = node[TPMKey.WRITE_MQTT_PUBLISH_TOPIC]    
                writeData           :str            = node[TPMKey.WRITE_VAR_VALUE]  
                writeMQTTResult     :bool           = False        

                while MainData.isRunningTPMProgram == True:
                    writeMQTTResult = writeMQTTVar.write(writeTopic, writeData)

                    if writeMQTTResult == False:
                        time.sleep(0.1)
                        CDRLog.print("MQTT 변수 write 실패")
                    else:
                        break    
                
            elif writeType == ProgramVarType.TYPE_MELSEC_PLC:
                
                writeMelsecPLCVar       :MelsecPLCVar   = self.__userVarList[node[TPMKey.WRITE_VAR_NAME]]
                writePLCAddr            :str            = node[TPMKey.WRITE_PLC_ADDR]    
                writePLCDataList        :list[int]      = node[TPMKey.WRITE_PLC_VALUE_LIST]
                writeMelsecPLCResult    :bool           = False        

                while MainData.isRunningTPMProgram == True:
                    writeMelsecPLCResult = writeMelsecPLCVar.write(writePLCAddr, writePLCDataList)

                    if writeMelsecPLCResult == False:
                        time.sleep(0.1)
                        CDRLog.print("Melsec PLC 변수 write 실패")
                    else:
                        break 

            elif writeType == ProgramVarType.TYPE_BLE:
                
                writeBLEVar             :BLEVar         = self.__userVarList[node[TPMKey.WRITE_VAR_NAME]]
                writeBLEValue           :str            = node[TPMKey.WRITE_VAR_VALUE] 

                while MainData.isRunningTPMProgram == True:
                    
                    writeBLEResult:bool = writeBLEVar.write(writeBLEValue)
                    
                    if writeBLEResult == False:

                        time.sleep(0.1)
                    else:
                        break 




    def __executeTargetTreeNode(self, treeType:str, node:dict):
        '''
        ### 노드를 타겟 트리에서 실행
        '''

        if treeType == TPMKey.TREE_PROGRAM :
            self.__executeProgramNode(node)

        elif treeType == TPMKey.TREE_EVENT :
            self.__executeEventNode(node)

        elif treeType == TPMKey.TREE_FUNC :
            self.__executeFuncNode(node)



    def __executeProgramNode(self, node:dict):
        '''
        TPM Program Node 실행 함수
        '''
        if MainData.isRunningTPMProgram == False:
            return
        
        # if self.__goToBookmarkNodeId != -1:
        #     return
        
        # 비활성 노드는 skip
        if node[TPMKey.DEFAULT_ENABLE] == False:
            return   
        
        self.__curProgramNodeId     = node[TPMKey.DEFAULT_NODE_ID]
        nodeDepth                   = self.__programNodeDepthList[self.__curProgramNodeId]

        # CDRLog.print(f"Executing Program nodeId: {self.__curProgramNodeId + 1} with cmdId: {node['cmdId']}, curDepth : {nodeDepth}")
        self.__executeNode(TPMKey.TREE_PROGRAM, node, nodeDepth)



    def __executeFuncNode(self, node:dict):
        '''
        TPM Function Node 실행 함수
        '''
        if MainData.isRunningTPMProgram == False:
            return
        
        # if self.__goToBookmarkNodeId != -1:
        #     return
        
        # 비활성 노드는 skip
        if node[TPMKey.DEFAULT_ENABLE] == False :
            return   
        
        self.__curFunctionNodeId    = node[TPMKey.DEFAULT_NODE_ID]
        nodeDepth                   = self.__userFuncNodeDepthList[self.__curFunctionNodeId]
        
        # CDRLog.print(f"Executing Function nodeId: {self.__curFunctionNodeId + 1} with cmdId: {node['cmdId']}")
        self.__executeNode(TPMKey.TREE_FUNC, node, nodeDepth)   



    def __executeEventNode(self, node:dict):
        '''
        TPM Event Node 실행 함수
        '''
        if MainData.isRunningTPMProgram == False:
            return
        
        # if self.__goToBookmarkNodeId != -1:
        #     return
        
        # 비활성 노드는 skip
        if node[TPMKey.DEFAULT_ENABLE] == False :
            return   
        
        
        self.__curEventNodeId   = node[TPMKey.DEFAULT_NODE_ID]
        nodeDepth               = self.__eventNodeDepthList[self.__curEventNodeId]
        
        # print(f"Executing Event nodeId: {self.__curEventNodeId + 1} with cmdId: {node['cmdId']}, depth : {nodeDepth}")
        self.__executeNode(TPMKey.TREE_EVENT, node, nodeDepth)
    
    

    

    def __createEvent(self, event_name, eventNode, nodeDepth):
        '''
        TPM Event 생성
        '''
        def event():

            while True :
               
                if MainData.isRunningTPMProgram == False:
                    break

                if self.__getConditionResult(eventNode) == True:

                    for child in eventNode[TPMKey.DEFAULT_CHILD_NODE_LIST]:
                        self.__executeEventNode(child) 

                self.__curEventNodeId = -1
                time.sleep(eventNode[TPMKey.EVENT_CYCLE])

            self.__curEventNodeId = -1
            print('Terminate event : ', event_name)

        return event  
        

    def __getProgramState(self) -> str:
        '''
        ### 현재 프로그램 상태 정보 반환
        '''

        programState :str = ProgramState.STOP

        if MainData.isRunningTPMProgram == True:

            programState = ProgramState.PLAY  

            if MainData.isPausedTPMProgram == True:
                programState = ProgramState.PAUSE

        return programState
    


    def __removeAllUserVars(self):
        '''
        선언된 모든 프로그램 변수 제거
        '''
        keyList :list[str] = []
        for varName in self.__userVarList.keys():
            keyList.append(varName)

        for i in range(len(keyList)): 
            #print(f'vars : {keyList[i]}  // {self.__userVarList[keyList[i]]}')  
            del self.__userVarList[keyList[i]]
            
            # varName:str = keyList[i]
            # if varName in self.__userVarList:
            #     del self.__userVarList[varName]

        self.__userVarList.clear()

        # for key in list(self.__userVarList.keys()):
        #     var = self.__userVarList[key]

        #     # 연결 종료 또는 정리 메서드가 존재하면 호출
        #     if hasattr(var, "disconnect"):
        #         try:
        #             print(f"[{key}] disconnect")
        #             var.disconnect()
                    
        #         except Exception as e:
        #             CDRLog.print(f"[{key}] disconnect 에러: {e}")
            
        #     elif hasattr(var, "close"):
        #         try:
        #             var.close()
        #         except Exception as e:
        #             CDRLog.print(f"[{key}] close 에러: {e}")
            
        #     del self.__userVarList[key]

    def __removeAllUserEvents(self):
        '''
        선언된 모든 프로그램 이벤트 제거
        '''
        keyList :list[str] = []
        for eventName in self.__userEventList.keys():
            keyList.append(eventName)

        for i in range(len(keyList)):
            del self.__userEventList[keyList[i]]

        self.__userEventList.clear()



    def __removeAllUserFuncs(self):
        '''
        선언된 모든 프로그램 이벤트 제거
        '''
        keyList :list[str] = []
        for funcName in self.__userFuncList.keys():
            keyList.append(funcName)

        for i in range(len(keyList)):
            del self.__userFuncList[keyList[i]]

        self.__userFuncList.clear()




    def __compare(self, leftVar, rightVar, operator:str) -> bool:

        result  :bool = False

        if operator == Operator.EQUAL :
            if leftVar == rightVar :
                result = True
        
        elif operator == Operator.NOT_EQUAL :
            if leftVar != rightVar :
                result = True  
        
        elif operator == Operator.BIG_OR_EQUAL :
            if leftVar >= rightVar :
                result = True
        
        elif operator == Operator.SMALL_OR_EQUAL :
            if leftVar <= rightVar :
                result = True
        
        elif operator == Operator.BIG :
            if leftVar > rightVar :
                result = True
        
        elif operator == Operator.SMALL :
            if leftVar < rightVar :
                result = True

        return result
    


    def __getConditionResult(self, node:dict) -> bool:

        leftVar                 :PrimitiveVar       = self.__userVarList[node[TPMKey.IF_LEFT_VAR_NAME]]
        rightVar                :PrimitiveVar       = None
        rightVarInputType       :str                = node[TPMKey.IF_RIGHT_VAR_TYPE]
        startIndexVar           :PrimitiveVar       = None
        leftVarStartIndex       :int                = 0
        leftVarEndIndex         :int                = 0
        rightVarStartIndex      :int                = 0
        rightVarEndIndex        :int                = 0
        leftVarValueList        :list               = []
        rigthVarValueList       :list               = []
        leftVarValue                                = None
        rightVarValue                               = None
        operator                :str                = node[TPMKey.IF_OPERATOR]
        result                  :bool               = False

        # 배열 변수 비교의 경우
        if 'Array' in node[TPMKey.IF_LEFT_VAR_TYPE] :

            # 조건문 좌측 변수 설정
            if node[TPMKey.IF_LEFT_VAR_ARR_START_INDEX_TYPE] == ValueAssignType.INPUT :
                leftVarStartIndex = node[TPMKey.IF_LEFT_VAR_ARR_START_INDEX_VALUE]
            
            elif node[TPMKey.IF_LEFT_VAR_ARR_START_INDEX_TYPE] == ValueAssignType.VAR :
                startIndexVar   = self.__userVarList[node[TPMKey.IF_LEFT_VAR_ARR_START_INDEX_VAR_NAME]]
                leftVarStartIndex      = startIndexVar.getValue()

            leftVarEndIndex     = leftVarStartIndex + node[TPMKey.IF_LEFT_VAR_ARR_DATA_LEN]
            leftVarValueList    = leftVar.getValue()[leftVarStartIndex : leftVarEndIndex]


            # 조건문 우측 변수 설정
            if rightVarInputType == ValueAssignType.INPUT :
                
                rigthVarValueList = []
                rightVarValue     = eval(node[TPMKey.IF_RIGHT_VAR_VALUE])  
                
                # 직접 입력한 우항 값을 리스트 형태로 저장
                if type(rightVarValue) == list :
                    rigthVarValueList = rightVarValue
                else:
                    rigthVarValueList.append(rightVarValue)                  

            elif rightVarInputType == ValueAssignType.VAR :

                rightVarStartIndex  = node[TPMKey.IF_RIGHT_VAR_ARR_START_INDEX]
                rightVarEndIndex    = rightVarStartIndex + node[TPMKey.IF_LEFT_VAR_ARR_DATA_LEN]

                rightVar            = self.__userVarList[node[TPMKey.IF_RIGHT_VAR_VALUE]]
                rigthVarValueList   = rightVar.getValue()[rightVarStartIndex : rightVarEndIndex]


            # 조건 검사 결과 반환
            result = self.__compare(leftVarValueList, rigthVarValueList, operator)


        # 일반 변수 비교의 경우
        else :

            leftVarValue = leftVar.getValue()
            
            if rightVarInputType == ValueAssignType.VAR:
                rightVar        = self.__userVarList[node[TPMKey.IF_RIGHT_VAR_VALUE]]
                rightVarValue   = rightVar.getValue()
            
            elif rightVarInputType == ValueAssignType.INPUT :
                rightVarValue = node[TPMKey.IF_RIGHT_VAR_VALUE]

            # print(f"leftVarValue : {leftVarValue}")
            # print(f"rightVarValue : {rightVarValue}")

            Conditional_statement = f"leftVarValue {operator} rightVarValue"

            # 조건 검사 결과 반환
            result = eval(Conditional_statement)   


        return result
    



    def __runSystemFunc(self, node : dict) :
        '''
        시스템 함수 실행 함수 : 수정 필요부
        '''
        #########################################################################
        # 시스템 함수 등록 시, 아래의 형식에 따라 추가 필요!
        #########################################################################

        funcName            :str            = node[TPMKey.FUNC_NAME]
        paramValueList      :list[dict]     = []
        returnValueList     :list[dict]     = []

        if TPMKey.PARAM_VALUE_LIST in node:
            paramValueList = node[TPMKey.PARAM_VALUE_LIST]

        if TPMKey.RETURN_VALUE_LIST in node:
            returnValueList = node[TPMKey.RETURN_VALUE_LIST]

        if funcName == SysFuncName.RUN_RWRP_COMM:

            host    :str = ""
            port    :int = -1

            for param in paramValueList:

                if param[TPMKey.PARAM_NAME] == SysFuncKeyword.ADDRESS:
                    host = param[TPMKey.PARAM_VALUE]
                
                elif param[TPMKey.PARAM_NAME] == SysFuncKeyword.PORT:
                    port = param[TPMKey.PARAM_VALUE]

            self.__tpmSysFuncManager.runRWRPCommunicator(host, port)

        
        elif funcName == SysFuncName.FR_CONNECT:
            
            addr    :str = ""

            for param in paramValueList:

                if param[TPMKey.PARAM_NAME] == SysFuncKeyword.ADDRESS:
                    addr = param[TPMKey.PARAM_VALUE]

            self.__tpmSysFuncManager.connectToFR(addr)

        
        elif funcName == SysFuncName.FR_READ:

            for param in returnValueList :

                # param["returnValue"] =  self.__tpmSysFuncManager.readFRData()
                print(f"self.__tpmSysFuncManager.readFRData() : {self.__tpmSysFuncManager.readFRData()}")
        

        elif funcName == SysFuncName.FR_STOP_MOTION:

            self.__tpmSysFuncManager.stopFRMotion()


        elif funcName == SysFuncName.DH_GRIPPER_INIT:
            
            tcpIPVar    :TcpIPVar = None

            for param in paramValueList :
                
                if TPMKey.PARAM_NAME in param == False or TPMKey.PARAM_VALUE in param == False:
                    continue

                paramName               = param[TPMKey.PARAM_NAME]
                paramValue              = param[TPMKey.PARAM_VALUE]

                if paramName == SysFuncKeyword.TCPIP_VAR:
                    tcpIPVar = self.__userVarList[paramValue]    

            self.__tpmSysFuncManager.initDHGripperVar(tcpIPVar)

        
        elif funcName == SysFuncName.DH_GRIPPER_HOLD:

            tcpIPVar    :TcpIPVar = None

            for param in paramValueList :
                
                if TPMKey.PARAM_NAME in param == False or TPMKey.PARAM_VALUE in param == False:
                    continue

                paramName               = param[TPMKey.PARAM_NAME]
                paramValue              = param[TPMKey.PARAM_VALUE]

                if paramName == SysFuncKeyword.TCPIP_VAR:
                    tcpIPVar = self.__userVarList[paramValue]    

            self.__tpmSysFuncManager.holdDHGripper(tcpIPVar)


        elif funcName == SysFuncName.DH_GRIPPER_RELEASE:

            tcpIPVar    :TcpIPVar = None

            for param in paramValueList :
                
                if TPMKey.PARAM_NAME in param == False or TPMKey.PARAM_VALUE in param == False:
                    continue

                paramName               = param[TPMKey.PARAM_NAME]
                paramValue              = param[TPMKey.PARAM_VALUE]

                if paramName == SysFuncKeyword.TCPIP_VAR:
                    tcpIPVar = self.__userVarList[paramValue]    

            self.__tpmSysFuncManager.releaseDHGripper(tcpIPVar)
        
        #mini gripper 250109    
        elif funcName == SysFuncName.JODELL_GRIPPER_INIT:

            tcpIPVar    :TcpIPVar = None

            for param in paramValueList :
                
                if TPMKey.PARAM_NAME in param == False or TPMKey.PARAM_VALUE in param == False:
                    continue

                paramName               = param[TPMKey.PARAM_NAME]
                paramValue              = param[TPMKey.PARAM_VALUE]

                if paramName == SysFuncKeyword.TCPIP_VAR:
                    tcpIPVar = self.__userVarList[paramValue]    

            self.__tpmSysFuncManager.initJodellGripper(tcpIPVar)        
            
        elif funcName == SysFuncName.JODELL_GRIPPER_HOLD:

            tcpIPVar    :TcpIPVar = None

            for param in paramValueList :
                
                if TPMKey.PARAM_NAME in param == False or TPMKey.PARAM_VALUE in param == False:
                    continue

                paramName               = param[TPMKey.PARAM_NAME]
                paramValue              = param[TPMKey.PARAM_VALUE]

                if paramName == SysFuncKeyword.TCPIP_VAR:
                    tcpIPVar = self.__userVarList[paramValue]    

            self.__tpmSysFuncManager.holdJodellGripper(tcpIPVar)        
            
        elif funcName == SysFuncName.JODELL_GRIPPER_RELEASE:

            tcpIPVar    :TcpIPVar = None

            for param in paramValueList :
                
                if TPMKey.PARAM_NAME in param == False or TPMKey.PARAM_VALUE in param == False:
                    continue

                paramName               = param[TPMKey.PARAM_NAME]
                paramValue              = param[TPMKey.PARAM_VALUE]

                if paramName == SysFuncKeyword.TCPIP_VAR:
                    tcpIPVar = self.__userVarList[paramValue]    

            self.__tpmSysFuncManager.releaseJodellGripper(tcpIPVar)    
        
        
        elif funcName == SysFuncName.PUB_CRC_ORDER_COMPLETE:
            
            mqttVar         :MqttVar    = None
            storeId         :int        = -1
            orderId         :int        = -1
            paramName                   = None
            paramValue                  = None
            
            for param in paramValueList :

                paramName   = param[TPMKey.PARAM_NAME]
                paramValue  = param[TPMKey.PARAM_VALUE]

                if paramName == SysFuncKeyword.MQTT_VAR:

                    mqttVar     = self.__userVarList[paramValue]

                elif paramName == SysFuncKeyword.STORE_ID:
                    
                    # str 타입이면, 변수
                    if type(paramValue) == str :
                        storeIdVar  :PrimitiveVar   = self.__userVarList[paramValue] 
                        storeId                     = storeIdVar.getValue()
                    else :
                        storeId                     = paramValue

                elif paramName == SysFuncKeyword.ORDER_ID:          
                    
                    # str 타입이면, 변수
                    if type(paramValue) == str :
                        orderIdVar  :PrimitiveVar   = self.__userVarList[paramValue]
                        orderId                     = orderIdVar.getValue()
                    else :
                        orderId                     = paramValue              
            
            self.__tpmSysFuncManager.publishCRCOrderComplete(mqttVar, storeId, orderId)

        elif funcName == SysFuncName.GET_CRC_ORDER_MENU:

            returnVar   :PrimitiveVar = self.__userVarList[returnValueList[0][TPMKey.RETURN_VALUE]]    
            returnVar.setValue(self.__tpmSysFuncManager.getCRCOrderMenu())

        
        elif funcName == SysFuncName.GET_CRC_ORDER_MENU_LIST:

            returnVar   :PrimitiveVar = self.__userVarList[returnValueList[0][TPMKey.RETURN_VALUE]] 
            returnVar.setValue(self.__tpmSysFuncManager.getCRCOrderMenuList())
        

        elif funcName == SysFuncName.GET_CRC_ORDER_QUANTITY: #주문 갯수

            returnVar   :PrimitiveVar = self.__userVarList[returnValueList[0][TPMKey.RETURN_VALUE]] 
            returnVar.setValue(self.__tpmSysFuncManager.getCRCOrderNum())


        elif funcName == SysFuncName.GET_CRC_ORDER_NUMBER: #주문 번호(ID랑은 다른 번호)

            returnVar   :PrimitiveVar = self.__userVarList[returnValueList[0][TPMKey.RETURN_VALUE]] 
            returnVar.setValue(self.__tpmSysFuncManager.getCRCOrderNumber())            


        elif funcName == SysFuncName.GET_CRC_ORDER_ID:

            for param in returnValueList:
                
                paramName   = param[TPMKey.RETURN_NAME]
                paramValue  = param[TPMKey.RETURN_VALUE]

                if paramName == SysFuncKeyword.ORDER_ID:

                    returnVar   :PrimitiveVar = self.__userVarList[paramValue] 
                    returnVar.setValue(self.__tpmSysFuncManager.getCRCOrderId())


        elif funcName == SysFuncName.RUN_CRC_COMM:
            
            mqttVar         :MqttVar    = None
            storeId         :int        = -1
            printerId       :int        = -1
            paramName                   = None
            paramValue                  = None

            for param in paramValueList:
                
                if TPMKey.PARAM_NAME in param == False or TPMKey.PARAM_VALUE in param == False:
                    continue

                paramName               = param[TPMKey.PARAM_NAME]
                paramValue              = param[TPMKey.PARAM_VALUE]

                if paramName == SysFuncKeyword.MQTT_VAR:
                    mqttVar = self.__userVarList[paramValue]
                
                elif paramName == SysFuncKeyword.STORE_ID:
                    
                    # str 타입이면, 변수
                    if type(paramValue) == str :
                        storeIdVar  :PrimitiveVar   = self.__userVarList[paramValue] 
                        storeId                     = storeIdVar.getValue()
                    else :
                        storeId                     = paramValue

                elif paramName == SysFuncKeyword.PRINTER_ID:
                    # str 타입이면, 변수
                    if type(paramValue) == str :
                        printerIdVar  :PrimitiveVar   = self.__userVarList[paramValue] 
                        printerId                     = printerIdVar.getValue()
                    else :
                        printerId                     = paramValue

                elif paramName == SysFuncKeyword.MAX_ORDER_QUANTITY:
                    # str 타입이면, 변수
                    if type(paramValue) == str :
                        maxOrderNumVar  :PrimitiveVar   = self.__userVarList[paramValue] 
                        maxOrderNum                     = maxOrderNumVar.getValue()
                    else :
                        maxOrderNum                     = paramValue

            self.__tpmSysFuncManager.runCRCCommunication(mqttVar, storeId, printerId, maxOrderNum)
 
        
        elif funcName == SysFuncName.GET_RWRP_COLLISION:

            returnVar   :PrimitiveVar = self.__userVarList[returnValueList[0][TPMKey.RETURN_VALUE]]
            returnVar.setValue(self.__tpmSysFuncManager.getRWRPCollsion())

            print(f"get collision : {returnVar.getValue()}")


        elif funcName == SysFuncName.GET_DELONGHI_STATE_CODE:

            bleVar  :BLEVar = None    

            for param in paramValueList:
                
                if param[TPMKey.PARAM_NAME] == SysFuncKeyword.DEVICE:
                    bleVar = self.__userVarList[param[TPMKey.PARAM_VALUE]]
            
            returnVar   :PrimitiveVar = self.__userVarList[returnValueList[0][TPMKey.RETURN_VALUE]] 
            returnVar.setValue(self.__tpmSysFuncManager.getDelonghiStateCode(bleVar))
            

        elif funcName == SysFuncName.BREW_DELONGHI_ESPRESSO:
            
            bleVar  :BLEVar = None  

            for param in paramValueList:
                if param[TPMKey.PARAM_NAME] == SysFuncKeyword.DEVICE:
                    bleVar = self.__userVarList[param[TPMKey.PARAM_VALUE]]

            self.__tpmSysFuncManager.brewDelonghiEspresso(bleVar)


        elif funcName == SysFuncName.BREW_DELONGHI_AMERICANO:
            
            bleVar  :BLEVar = None  

            for param in paramValueList:
                if param[TPMKey.PARAM_NAME] == SysFuncKeyword.DEVICE:
                    bleVar = self.__userVarList[param[TPMKey.PARAM_VALUE]]

            self.__tpmSysFuncManager.brewDelonghiAmericano(bleVar)

        
        elif funcName == SysFuncName.IS_DELONGHI_IDLE:
            
            bleVar  :BLEVar = None  

            for param in paramValueList:
                if param[TPMKey.PARAM_NAME] == SysFuncKeyword.DEVICE:
                    bleVar = self.__userVarList[param[TPMKey.PARAM_VALUE]]

            returnVar   :PrimitiveVar = self.__userVarList[returnValueList[0][TPMKey.RETURN_VALUE]] 
            returnVar.setValue(self.__tpmSysFuncManager.isDelonghiIdle(bleVar))


        elif funcName == SysFuncName.WAKE_UP_DELONGHI:
            
            bleVar  :BLEVar = None  

            for param in paramValueList:
                if param[TPMKey.PARAM_NAME] == SysFuncKeyword.DEVICE:
                    bleVar = self.__userVarList[param[TPMKey.PARAM_VALUE]]
            
            self.__tpmSysFuncManager.wakeupDeloghi(bleVar)
            
        
        elif funcName == SysFuncName.SEND_FR_MODBUS_CMD:

            frModbusComm        :ModbusTCPVar   = None
            cmdMemoryAddr       :int            = -1
            feedbackMemoryAddr  :int            = -1
            cmdValue            :int            = -1    
            startFeedback       :int            = -1
            finFeedback         :int            = -1        

            # 로봇 명령 간소화
            for param in paramValueList:

                paramName               = param[TPMKey.PARAM_NAME]
                paramValue              = param[TPMKey.PARAM_VALUE]

                if paramName == SysFuncKeyword.ROBOT_COMM:
                    frModbusComm = self.__userVarList[paramValue]

                if paramName == SysFuncKeyword.CMD_MEMORY_ADDRESS:
                    
                    if param["assignType"] == ValueAssignType.INPUT:
                        cmdMemoryAddr                      = param[TPMKey.PARAM_VALUE]

                    elif param["assignType"] == ValueAssignType.VAR:
                        cmdMemoryAddrVar :PrimitiveVar     = self.__userVarList[paramValue]
                        cmdMemoryAddr                      = cmdMemoryAddrVar.getValue()

                elif paramName == SysFuncKeyword.COMMAND:

                    if param["assignType"] == ValueAssignType.INPUT:
                        cmdValue = param[TPMKey.PARAM_VALUE]

                    elif param["assignType"] == ValueAssignType.VAR:
                        cmdValueVar :PrimitiveVar       = self.__userVarList[paramValue]
                        cmdValue                        = cmdValueVar.getValue()

                elif paramName == SysFuncKeyword.FEEDBACK_MEMORY_ADDRESS:

                    if param["assignType"] == ValueAssignType.INPUT:
                        feedbackMemoryAddr = param[TPMKey.PARAM_VALUE]

                    elif param["assignType"] == ValueAssignType.VAR:
                        feedbackMemoryAddrVar :PrimitiveVar       = self.__userVarList[paramValue]
                        feedbackMemoryAddr                        = feedbackMemoryAddrVar.getValue()

                elif paramName == SysFuncKeyword.START_FEEDBACK:

                    if param["assignType"] == ValueAssignType.INPUT:
                        startFeedback = param[TPMKey.PARAM_VALUE]

                    elif param["assignType"] == ValueAssignType.VAR:
                        startFeedbackValueVar :PrimitiveVar         = self.__userVarList[paramValue]
                        startFeedback                               = startFeedbackValueVar.getValue()

                elif paramName == SysFuncKeyword.FIN_FEEDBACK:
                        
                    if param["assignType"] == ValueAssignType.INPUT:
                        finFeedback = param[TPMKey.PARAM_VALUE]

                    elif param["assignType"] == ValueAssignType.VAR:
                        finFeedbackValueVar :PrimitiveVar       = self.__userVarList[paramValue]
                        finFeedback                             = finFeedbackValueVar.getValue()
            
            self.__tpmSysFuncManager.sendFRModbusCmd(frModbusComm, cmdMemoryAddr, cmdValue, feedbackMemoryAddr, startFeedback, finFeedback)
            

        elif funcName == SysFuncName.SEND_PRINT_INFO:

            orderMenuId         :int            = -1    
            
            for param in paramValueList:

                paramName               = param[TPMKey.PARAM_NAME]
                paramValue              = param[TPMKey.PARAM_VALUE]

                if paramName == SysFuncKeyword.ORDER_MENU:
                    
                    if param["assignType"] == ValueAssignType.INPUT:  
                        orderMenuId                     = paramValue

                    elif param["assignType"] == ValueAssignType.VAR:    
                        orderMenuIdVar  :PrimitiveVar   = self.__userVarList[paramValue]
                        orderMenuId                     = orderMenuIdVar.getValue()  

            self.__tpmSysFuncManager.sendPrintData(orderMenuId)


        elif funcName == SysFuncName.SEND_PRINT_CMD:
            
            mqttVar         :MqttVar    = None
            orderId         :int        = -1
            printerId       :int        = -1
            paramName                   = None
            paramValue                  = None

            for param in paramValueList:

                paramName   = param[TPMKey.PARAM_NAME]
                paramValue  = param[TPMKey.PARAM_VALUE]

                if paramName == SysFuncKeyword.MQTT_VAR:
                    mqttvar = self.__userVarList[paramValue]

                if paramName == SysFuncKeyword.ORDER_ID:
                    
                    if param["assignType"] == ValueAssignType.INPUT:  
                        orderId                     = paramValue

                    elif param["assignType"] == ValueAssignType.VAR:    
                        orderIdVar  :PrimitiveVar   = self.__userVarList[paramValue]
                        orderId                     = orderIdVar.getValue()  

                if paramName == SysFuncKeyword.PRINTER_ID:
                    
                    if param["assignType"] == ValueAssignType.INPUT:  
                        printerId                     = paramValue

                    elif param["assignType"] == ValueAssignType.VAR:    
                        printerIdVar  :PrimitiveVar   = self.__userVarList[paramValue]
                        printerId                     = printerIdVar.getValue()  

            self.__tpmSysFuncManager.sendPrintCmd(mqttvar, orderId, printerId)


        elif funcName == SysFuncName.GET_PRINT_STATE:

            mqttVar         :MqttVar    = None
            orderId         :int        = -1
            printerId       :int        = -1
            paramName                   = None
            paramValue                  = None

            for param in paramValueList:

                paramName   = param[TPMKey.PARAM_NAME]
                paramValue  = param[TPMKey.PARAM_VALUE]

                if paramName == SysFuncKeyword.MQTT_VAR:
                    mqttvar = self.__userVarList[paramValue]

                if paramName == SysFuncKeyword.PRINTER_ID:
                    
                    if param["assignType"] == ValueAssignType.INPUT:  
                        printerId                     = paramValue

                    elif param["assignType"] == ValueAssignType.VAR:    
                        printerIdVar  :PrimitiveVar   = self.__userVarList[paramValue]
                        printerId                     = printerIdVar.getValue()  

            returnVar   :PrimitiveVar = self.__userVarList[returnValueList[0][TPMKey.RETURN_VALUE]] 
            returnVar.setValue(self.__tpmSysFuncManager.getPrintState(bleVar, printerId))
        
        elif funcName == SysFuncName.ORDER_UI_SENDDATA:            
            tcpIPVar    :TcpIPVar = None
            paramName   = None
            paramValue  = None
            TrayID      = None
            Data   :int = None

            for param in paramValueList :
                
                if TPMKey.PARAM_TYPE in param == False or TPMKey.PARAM_VALUE in param == False:
                    continue
         
                paramName               = param[TPMKey.PARAM_NAME]
                paramValue              = param[TPMKey.PARAM_VALUE]
                #CDRLog.print(f'{paramName} // {paramValue}')
                if paramName == SysFuncKeyword.TCPIP_VAR:
                    tcpIPVar = self.__userVarList[paramValue]    
                elif paramName == SysFuncKeyword.TRAY_ID:
                    TrayID   = paramValue
                elif paramName == SysFuncKeyword.ORDER_ID:
                    if param["assignType"] == ValueAssignType.INPUT:  
                        Data                     = paramValue

                    elif param["assignType"] == ValueAssignType.VAR:    
                        orderIdVar  :PrimitiveVar   = self.__userVarList[paramValue]
                        Data                     = orderIdVar.getValue()  
                    

            self.__tpmSysFuncManager.order_UI_SendData(tcpIPVar, TrayID, Data)    
            

    # ============================================================================================================
    # ============================================================================================================
    # 외부 호출 함수 ==============================================================================================
    # ============================================================================================================
    # ============================================================================================================

    def playProgram(self, programData:dict):

        if  MainData.isRunningTPMProgram == True:
            CDRLog.print('Program is Already Running')
        
        else:   
            threading.Thread(target=self.__tpmProgramRunningThreadHandler, args=(programData,)).start()


    def makeRealtimeProgramInfoData(self) -> dict:

        realtimeInfoData :dict                                  = {}

        if MainData.isRunningTPMProgram == True:

            programRealtimeInfoData :dict                                   = {}
            programRealtimeInfoData["state"]                                = self.__getProgramState()
            
            if self.__curProgramNodeId == -1:
                programRealtimeInfoData["currentProgramNodeId"]         = -1
            else:
                programRealtimeInfoData["currentProgramNodeId"]         = self.__curProgramNodeId + 1

            if self.__curFunctionNodeId == -1:
                programRealtimeInfoData["currentFunctionNodeId"]        = -1
            else:
                programRealtimeInfoData["currentFunctionNodeId"]        = self.__curFunctionNodeId + 1

            if self.__curEventNodeId == -1:
                programRealtimeInfoData["currentEventNodeId"]           = -1
            else:
                programRealtimeInfoData["currentEventNodeId"]           = self.__curEventNodeId + 1

            programRealtimeInfoData["varInfo"]                          = self.getMonitoringVarInfo()

            realtimeInfoData["program"]                                 = programRealtimeInfoData

        return realtimeInfoData
    

    def getMonitoringVarInfo(self) -> list[dict]:

        varInfo:list[dict] = []
        for varName in self.__monitoringVarNameList:
            varData:PrimitiveVar = self.__userVarList[varName]
            varInfo.append({"varName" : varName, "value" : varData.getValue()})

        return varInfo
    