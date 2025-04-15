def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)


class _SysFuncName():

    @constant
    def FR_CONNECT() -> str:
        return "FR_Connect"
    
    @constant
    def FR_STOP_MOTION() -> str:
        return "FR_StopMotion"
    
    @constant
    def FR_READ() -> str:
        return "FR_Read"
    
    @constant
    def RUN_RWRP_COMM() -> str:
        return "Run_RWRP_Communicator"
    
    @constant
    def GET_RWRP_COLLISION() -> str:
        return "getRWRPCollsion"
    
    @constant
    def DH_GRIPPER_INIT() -> str:
        return "initDHGripper"
    
    @constant
    def DH_GRIPPER_HOLD() -> str:
        return "holdDHGripper"
    
    @constant
    def DH_GRIPPER_RELEASE() -> str:
        return "releaseDHGripper"
    
    #mini gripper 250109
    @constant
    def JODELL_GRIPPER_INIT() -> str:
        return "initJodellGripper"
    
    @constant
    def JODELL_GRIPPER_HOLD() -> str:
        return "holdJodellGripper"
    
    @constant
    def JODELL_GRIPPER_RELEASE() -> str:
        return "releaseJodellGripper"
    
    @constant
    def PUB_CRC_ORDER_COMPLETE() -> str:
        return "publishCRCOrderComplete"
    
    @constant
    def GET_CRC_ORDER_MENU() -> str:
        return "getCRCOrderMenu"
    
    @constant
    def GET_CRC_ORDER_MENU_LIST() -> str:
        return "getCRCOrderMenuList"
    
    @constant
    def GET_CRC_ORDER_QUANTITY() -> str:
        return "getCRCOrderQuantity"
    
    @constant
    def GET_CRC_ORDER_ID() -> str:
        return "getCRCOrderId"
    

    @constant
    def RUN_CRC_COMM() -> str:
        return "runCRCCommunication"
    
    @constant
    def BREW_DELONGHI_ESPRESSO() -> str:
        return "brewDelonghiEspresso"
    
    @constant
    def BREW_DELONGHI_AMERICANO() -> str:
        return "brewDelonghiAmericano"
    
    @constant
    def WAKE_UP_DELONGHI() -> str:
        return "wakeupDeloghi"
    
    @constant
    def GET_DELONGHI_STATE_CODE() -> str:
        return "getDelonghiStateCode"
    
    @constant
    def IS_DELONGHI_IDLE() -> str:
        return "isDelonghiIdle"
    
    @constant
    def SEND_FR_MODBUS_CMD() -> str:
        return "sendFRModbusCmd"
    
    @constant
    def SEND_PRINT_INFO() -> str:
        return "sendPrintInfo"
    
    @constant
    def SEND_PRINT_CMD() -> str:
        return "sendPrintCmd"
    
    @constant
    def GET_PRINT_STATE() -> str:
        return "getPrintState"
    
    @constant
    def ORDER_UI_SENDDATA() -> str:
        return "order_UI_SendData"

    @constant
    def GET_CRC_ORDER_NUMBER() -> str:
        return "getCRCOrderNumber"
    
SysFuncName = _SysFuncName()

    

