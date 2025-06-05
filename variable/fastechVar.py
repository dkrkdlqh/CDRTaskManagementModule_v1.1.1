import sys
import os
import platform
import time

from cdrutils.log import CDRLog 
from const.event import Event
from typing import Callable, Any
from data.mainData import MainData

from variable.include_x64.FAS_EziMOTIONPlusE import *
from variable.include_x64.MOTION_DEFINE import *
from variable.include_x64.ReturnCodes_Define import *
from variable.include_x64.MOTION_EziSERVO2_DEFINE import *

class FastechVar:

    def __init__(self, eventCallback:Callable[[int, Any], None], nBdID=1, name=None) :

        self.__eventCallback    :Callable[[int], None]  = eventCallback
        self.BoardID = nBdID
        self.name = name
        self.ip_addr: str | None = None
        self.EZI_AXISSTATUS = None
        
    def __del__(self) :

        self.close()
        CDRLog.print('FastechVar instance is deleted.')
        
    

    def connect(self, addr : str, Id : int, boardType : str = 'MOTION2') -> bool:
        bSuccess = True
        self.ip_addr = addr
        self.BoardID = Id
        if boardType == 'MOTION2':
            self.EZI_AXISSTATUS = EZISERVO2_AXISSTATUS
            
        byIP = [int(x) for x in addr.split('.')]
        if FAS_ConnectTCP(byIP[0], byIP[1], byIP[2], byIP[3], self.BoardID) == 0:
            CDRLog.print("FASTECH Connection Fail!")
            bSuccess = False


        if bSuccess:
            CDRLog.print("FASTECH Connected successfully.")
        else:
            # 서버 연결 실패 -> 이벤트 발생
            if MainData.isRunningTPMProgram == True and self.__eventCallback != None:
                self.__eventCallback(Event.COMM_VAR_FAILED_TO_CONNECT, self)


    def setServoOn(self) -> bool:
        status_result, axis_status = FAS_GetAxisStatus(self.BoardID)
        if status_result != FMM_OK:
            CDRLog.print("Function(FAS_GetAxisStatus) was failed.")
            return False

        if (axis_status & self.EZI_AXISSTATUS.FFLAG_SERVOON) == 0:
            if FAS_ServoEnable(self.BoardID, 1) != FMM_OK:
                CDRLog.print("Function(FAS_ServoEnable) was failed.")
                return False

            while (axis_status & self.EZI_AXISSTATUS.FFLAG_SERVOON) == 0:
                time.sleep(0.001)
                status_result, axis_status = FAS_GetAxisStatus(self.BoardID)
                if status_result != FMM_OK:
                    CDRLog.print("Function(FAS_GetAxisStatus) was failed.")
                    return False
                if (axis_status & self.EZI_AXISSTATUS.FFLAG_SERVOON) != 0:
                    CDRLog.print("Servo ON")
        else:
            CDRLog.print("Servo is already ON")
        return True

    def setServoOff(self) -> bool:
        status_result, axis_status = FAS_GetAxisStatus(self.BoardID)
        if status_result != FMM_OK:
            CDRLog.print("Function(FAS_GetAxisStatus) was failed.")
            return False

        if (axis_status & self.EZI_AXISSTATUS.FFLAG_SERVOON) != 0:
            if FAS_ServoEnable(self.BoardID, 0) != FMM_OK:
                CDRLog.print("Function(FAS_ServoEnable) was failed.")
                return False

            while (axis_status & self.EZI_AXISSTATUS.FFLAG_SERVOON) != 0:
                time.sleep(0.001)
                status_result, axis_status = FAS_GetAxisStatus(self.BoardID)
                if status_result != FMM_OK:
                    CDRLog.print("Function(FAS_GetAxisStatus) was failed.")
                    return False
                if (axis_status & self.EZI_AXISSTATUS.FFLAG_SERVOON) == 0:
                    CDRLog.print("Servo OFF")
        else:
            CDRLog.print("Servo is already OFF")
        return True
    def moveIncPos(self, pulse : int , velocity : int) -> bool:
        """
        축을 지정된 펄스만큼 이동
        :param pulse: 이동할 펄스 수
        :param velocity: 이동 속도 (양수)
        """
        nIncPos = pulse
        nVelocity = velocity
        
        if FAS_MoveSingleAxisIncPos(self.BoardID, nIncPos, nVelocity) != FMM_OK:
            CDRLog.print("Function(FAS_MoveSingleAxisIncPos) was failed.")
            return False

        CDRLog.print(f"Move Inc Pos : {nIncPos} / {nVelocity}")
        return True
    
    def moveVelocity(self, Dir: int, TargetVeloc : int) -> bool:
        """
        축을 지정된 속도로 이동
        :param Dir: 이동 방향 (1: 양방향, 0: 음방향)
        :param TargetVeloc: 목표 속도 (양수)
        """
        nTargetVeloc = TargetVeloc
        nDirect = Dir

        if FAS_MoveVelocity(self.BoardID, nTargetVeloc, nDirect) != FMM_OK:
            CDRLog.print("Function(FAS_MoveVelocity) was failed.")
            return False

        CDRLog.print(f"Move Velocity : {nTargetVeloc} / {nDirect}")

        return True
    
    def moveStop(self) -> bool:
        """
        축의 이동을 중지
        """
        if FAS_MoveStop(self.BoardID) != FMM_OK:
            CDRLog.print("Function(FAS_MoveStop) was failed.")

            return False
        while True:
            time.sleep(0.001)
            status_result, axis_status = FAS_GetAxisStatus(self.BoardID)
            if status_result == FMM_OK and axis_status & self.EZI_AXISSTATUS.FFLAG_MOTIONING == 0:
                CDRLog.print("Move Stop!")
                break
        return True
    
    def moveOrigin(self) -> bool:
        """
        축을 원점(Origin)으로 이동
        :return: 성공 시 True, 실패 시 False
        """
        if FAS_MoveOriginSingleAxis(self.BoardID) != FMM_OK:
            CDRLog.print("Function(FAS_MoveOriginSingleAxis) was failed.")
            return False
        

    def getIoInput(self,Index : int) -> int | None:
        """
        입력 포트 상태를 읽어옴
        :return: 입력 포트 상태 (int), 실패 시 None
        
        SERVO2_IN_BITMASK_LIMITP = 0x00000001  #Limit +
        SERVO2_IN_BITMASK_LIMITN = 0x00000002  #Limit -
        SERVO2_IN_BITMASK_ORIGIN = 0x00000004  #Origin
        """
        if Index == 1:
            dwInputMask = SERVO2_IN_BITMASK_LIMITP
        elif Index == 2:
            dwInputMask = SERVO2_IN_BITMASK_LIMITN
        elif Index == 3:
            dwInputMask = SERVO2_IN_BITMASK_ORIGIN
        else:
            CDRLog.print("getIoInput - Invalid Index")
            return None
    
        status_result, io_input = FAS_GetIOInput(self.BoardID)
        if status_result != FMM_OK:
            CDRLog.print("Function(FAS_GetIOInput) was failed.")
            return None

        if io_input & dwInputMask:
            #print("INPUT PIN DETECTED.")
            return 1 #True
        else:
            #print("INPUT PIN NOT DETECTED.")
            return 0 #False



    def close(self):
        """
        FastechVar 객체를 닫고 연결을 종료
        """
        CDRLog.print("FastechVar close")
        FAS_Close(self.BoardID)


    # def check_drive_err(self) -> bool:
    #     status_result, axis_status = FAS_GetAxisStatus(self.nBdID)
    #     if status_result != FMM_OK:
    #         print("Function(FAS_GetAxisStatus) was failed.")
    #         return False

    #     if axis_status & EZISERVO2_AXISSTATUS.FFLAG_ERRORALL:
    #         if FAS_ServoAlarmReset(self.nBdID) != FMM_OK:
    #             print("Function(FAS_ServoAlarmReset) was failed.")
    #             return False
    #     return True