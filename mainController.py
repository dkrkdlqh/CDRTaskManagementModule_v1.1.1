import threading
import sys
import time
import json

from cdrutils.log import CDRLog


from queue import Queue

from manager.tpmCommManager import TPMCommManager
from manager.tpmProgramManager import TPMProgramManager
from manager.tpmSysFuncManager import TPMSysFuncManager

from data.mainData import MainData
from data.sysQueueData import SysQueueData
from data.sysFuncData import SysFuncData

from const.config import Config
from const.tpmCommKeyword import TPMCommKeyword
from const.loopType import LoopType
from const.event import Event

from cdrutils.cdrUtil import CDRUtil





class MainController():

    def __init__(self):
        CDRLog.Log("#### START ####")
        # 메인 컨트롤러 쓰레드에 요청하는 데이터를 관리하는 큐 
        self.__mainQueue                        :Queue                  = Queue()
        
        # tmp 통신 쓰레드에 요청하는 데이터를 관리하는 큐
        # self.__tmpQueue                      :Queue                  = Queue()    

        self.__lastPingTime                     :float                  = 0.0
    
        # self.__isRunningMainController          :bool = True
        
        # 프로그램 종료 변수
        self.terminate_sig = False
        
        self.__tpmSysFuncManager    :TPMSysFuncManager  = TPMSysFuncManager()
        self.__tpmProgramManager    :TPMProgramManager  = TPMProgramManager(self.__mainQueue, self.__tpmSysFuncManager)

        self.__tpmCommManager       :TPMCommManager     = TPMCommManager(self.__mainQueue)
        self.__tpmCommManager.openServer()

        threading.Thread(target=self.__computeThreadHandler).start() 
        threading.Thread(target=self.__keyInputThreadHandler).start()



    def __computeThreadHandler(self):
        '''
        ### 주요 연산 처리를 담당하는 쓰레드
        '''
        
        while True:

            # TMM 종료 이벤트 발생
            if MainData.isTerminatedTMMProcess == True:
                break
            
            readJsonData    :dict           = None
            writeJsonData   :dict           = None
            curTime         :float          = time.time()
            
            
            if self.__mainQueue.empty() == False:
            
                sysQueueData    :SysQueueData   = self.__mainQueue.get()  
                queueId         :str            = sysQueueData.getId()

                if queueId == SysQueueData.RECEIVE_TPM_DATA:

                    readJsonData = sysQueueData.getData()

                    if TPMCommKeyword.KEY_METHOD in readJsonData:

                        reqMethod   :str = readJsonData[TPMCommKeyword.KEY_METHOD]

                        # TPM 프로그램 실행 명령 ---------------------------------------------------------
                        if reqMethod == TPMCommKeyword.METHOD_PLAY_PROGRAM:
                            
                            with open(Config.PROGRAM_FILE_PATH, 'w') as file:
                                file.write(json.dumps(readJsonData[TPMCommKeyword.KEY_PARAMS]))

                            CDRLog.print(f'{Config.PROGRAM_FILE_PATH} write complete')

                            programData :dict = CDRUtil.loadJsonFile(Config.PROGRAM_FILE_PATH)
                            
                            # TPM에서 전달 받은 코드 실행
                            self.__tpmProgramManager.playProgram(programData)

                        # TPM 프로그램 일시정지 명령 -----------------------------------------------------
                        elif reqMethod == TPMCommKeyword.METHOD_PAUSE_PROGRAM:
                            
                            MainData.isPausedTPMProgram = True
                            
                            # 프로그램 실행 요청에 대한 응답 전달
                            self.__sendResponse(reqMethod)
                        
                        # TPM 프로그램 재개 명령 ---------------------------------------------------------
                        elif reqMethod == TPMCommKeyword.METHOD_RESUME_PROGRAM:
                            
                            MainData.isPausedTPMProgram = False
                            
                            # 프로그램 실행 요청에 대한 응답 전달
                            self.__sendResponse(reqMethod)
                        
                        # TPM 프로그램 정지 명령 ---------------------------------------------------------
                        elif reqMethod == TPMCommKeyword.METHOD_STOP_PROGRAM:
                            
                            MainData.isRunningTPMProgram = False

                            # 프로그램 실행 요청에 대한 응답 전달
                            self.__sendResponse(reqMethod)
                        
                        # 시스템 정보 요청 명령 ----------------------------------------------------------
                        elif reqMethod == TPMCommKeyword.METHOD_GET_SYS_INFO:
                            
                            sysFuncList             :list[SysFuncData]  = self.__tpmSysFuncManager.getSysFuncList()    
                            sysFuncJsonDataList     :list[dict]         = []                        

                            for i in range(len(sysFuncList)):
                                sysFuncJsonDataList.append(sysFuncList[i].toJson())

                            sysInfoJsonData    :dict = {
                                                            "method" : reqMethod, 
                                                            "values" : 
                                                            {
                                                                "version"       : Config.VERSION,
                                                                "sysFuncList"   : sysFuncJsonDataList
                                                            }, 
                                                        }

                            self.__tpmCommManager.writeCommData(sysInfoJsonData)

                            # 해당 데이터 보내고 실시간 데이터 주기적으로 전송하기
                            self.__lastPingTime = curTime

                elif queueId == SysQueueData.CLOSED_TPM_SERVER:

                    if self.__tpmCommManager != None:
                        self.__tpmCommManager.openServer()

                elif queueId == SysQueueData.ERR_COMM_VAR_CONNECTION:
                    
                    # 에러 발생 -> 현재 진행 중인 프로그램 종료
                    MainData.isRunningTPMProgram = False

                    writeJsonData           = {}
                    writeJsonData[TPMCommKeyword.KEY_METHOD] = TPMCommKeyword.METHOD_REALTIME_INFO
                    writeJsonData[TPMCommKeyword.KEY_PARAMS] = {"sysEvent" : sysQueueData.getData()}

                    self.__tpmCommManager.writeCommData(writeJsonData)
                    self.__lastPingTime = curTime

            
            if self.__lastPingTime != 0.0 and (curTime - self.__lastPingTime) > 1:

                # 주기적으로(1초) TPM에 실시간 데이터 전송
                
                writeJsonData               = {}
                writeJsonData[TPMCommKeyword.KEY_METHOD]     = TPMCommKeyword.METHOD_REALTIME_INFO
                writeJsonData[TPMCommKeyword.KEY_PARAMS]     = self.__tpmProgramManager.makeRealtimeProgramInfoData()
            
                self.__tpmCommManager.writeCommData(writeJsonData)
                self.__lastPingTime = curTime
            #/if
        # /while

        CDRLog.print("============ __mainControlThread terminated...")



    def __sendResponse(self, methodName:str):
        '''
        ### 응답 메세지 전송
        '''

        returnData:dict = {}
        returnData[TPMCommKeyword.KEY_METHOD] = methodName
        self.__tpmCommManager.writeCommData(returnData)


    def __keyInputThreadHandler(self) :
        '''
        ### 프로그램 종료 키 입력 처리 쓰레드
        '''
        while True:
            
            # TMM 종료 이벤트 발생
            if MainData.isTerminatedTMMProcess == True:
                break

            key = input() 
            if key == Config.KEY_QUIT:
                
                CDRLog.print("+++++++++++++++++++++++++++++++++++++++++++++++++++")    
                CDRLog.print("TMM will be terminated. Goodbye and see you again!!")    
                CDRLog.print("+++++++++++++++++++++++++++++++++++++++++++++++++++")   
                
                # self.__tpmCommManager.closeServer()
                # TMM 종료 선언
                MainData.isRunningTPMProgram    = False
                MainData.isTerminatedTMMProcess = True

                # del self.__tpmProgramManager
                # del self.__tpmSysFuncManager
                # del self.__tpmCommManager
                
                sys.exit()
                break

            elif key == Config.KEY_PLAY_DEFAULT_PROGRAM:

                CDRLog.print("+++++++++++++++++++++++++++++++++++++++++++++++++++")    
                CDRLog.print("Play program")    
                CDRLog.print("+++++++++++++++++++++++++++++++++++++++++++++++++++") 

                programData :dict = CDRUtil.loadJsonFile(Config.PROGRAM_FILE_PATH)
                            
                # TPM에서 전달 받은 코드 실행
                self.__tpmProgramManager.playProgram(programData)

            elif key == Config.KEY_STOP_DEFAULT_PROGRAM:
                
                CDRLog.print("+++++++++++++++++++++++++++++++++++++++++++++++++++")    
                CDRLog.print("Stop Program")    
                CDRLog.print("+++++++++++++++++++++++++++++++++++++++++++++++++++") 

                MainData.isRunningTPMProgram = False

        CDRLog.print("============ __keyInputThread terminated...")



    