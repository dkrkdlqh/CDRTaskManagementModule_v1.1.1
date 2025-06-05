

def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _SysFuncKeyword(object):

    @constant
    def ADDRESS() -> str:
        return "addr"
    
    @constant
    def PORT() -> str:
        return "port"
    
    @constant
    def TCPIP_VAR() -> str:
        return "tcpIPVar"
    #250522
    @constant
    def FASTECH_VAR() -> str:
        return "fastechVar"
    
    @constant
    def VELOCITY() -> str:
        return "velocity"
    
    @constant
    def DIRECTION() -> str:
        return "direction"
    
    @constant
    def SIGNAL_INDEX() -> str:
        return "signalIndex"    
    
    @constant
    def DATA() -> str:
        return "data"
    
    @constant
    def COLLISION() -> str:
        return "collision"
    
    @constant
    def MQTT_VAR() -> str:
        return "mqttVar"
    
    @constant
    def ORDER_MENU() -> str:
        return "orderMenu"
    
    @constant
    def ORDER_MENU_LIST() -> str:
        return "orderMenuList"
    
    @constant
    def ORDER_QUANTITY() -> str:
        return "orderQuantity"
    
    @constant
    def STORE_ID() -> str:
        return "storeId"
    
    @constant
    def ORDER_ID() -> str:
        return "orderId"
    
    @constant
    def ORDER_NUM() -> str:
        return "orderNum"
    
    @constant
    def DEVICE() -> str:
        return "device"
    
    @constant
    def CMD_MEMORY_ADDRESS() -> str:
        return "cmdMemoryAddr"
    
    @constant
    def FEEDBACK_MEMORY_ADDRESS() -> str:
        return "feedbackMemoryAddr"
    
    @constant
    def STATE_CODE() -> str:
        return "stateCode"
    
    @constant
    def PRINTER_ID() -> str:
        return "printerId"
    
    @constant
    def PRINTER_STATE() -> str:
        return "printerState"
    
    @constant
    def RESULT() -> str:
        return "result"
    
    @constant
    def ROBOT_COMM() -> str:
        return "robotComm"
    
    @constant
    def COMMAND() -> str:
        return "command"
    
    @constant
    def START_FEEDBACK() -> str:
        return "startFeedback"
    
    @constant
    def FIN_FEEDBACK() -> str:
        return "finFeedback"
    
    @constant
    def MAX_ORDER_QUANTITY() -> str:
        return "maxOrderQuantity"
    
    @constant
    def TRAY_ID() -> str:
        return "tray_id"

SysFuncKeyword = _SysFuncKeyword()
