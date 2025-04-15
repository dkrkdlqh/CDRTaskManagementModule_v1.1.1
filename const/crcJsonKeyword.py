
def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _CRCJsonKeyword():

    @constant
    def TOPIC_CRC_SERVER() -> str:
        return "crc/jts"
    
    @constant
    def TOPIC_CRC_RMS() -> str:
        return "crc/rms"
    
    @constant
    def TOPIC_MBRUSH_PRINTER() -> str:
        return "print/mbrush"
    
    @constant
    def KEY_CODE() -> str:
        return "code"
    
    @constant
    def KEY_STORE_ID() -> str:
        return "storeId"
    
    @constant
    def KEY_ORDER_ID() -> str:
        return "orderId"
    
    @constant
    def KEY_ORDER_ID() -> str:
        return "orderId"
    
    @constant
    def KEY_DATA() -> str:
        return "data"
    
    @constant
    def KEY_STATUS_ID() -> str:
        return "statusId"
    
    @constant
    def KEY_ORDER_LIST() -> str:
        return "orderList"
    
    @constant
    def KEY_ORDER_NUMBER() -> str:
        return "orderNumber"
    
    @constant
    def KEY_PHONE() -> str:
        return "phone"
    
    @constant
    def KEY_PRINT_TYPE() -> str:
        return "printType"
    
    @constant
    def KEY_REQ_ID() -> str:
        return "reqId"
    
    @constant
    def KEY_PRINTER_ID() -> str:
        return "printerId"
    
    @constant
    def KEY_PRINTER_MSG() -> str:
        return "printMsg"
    
    @constant
    def KEY_TEXT() -> str:
        return "text"
    
    @constant
    def KEY_COLOR() -> str:
        return "color"
    
    @constant
    def KEY_EVENT_ID() -> str:
        return "eventId"
    
    @constant
    def KEY_EVENT_ID() -> str:
        return "eventId"
    
    @constant
    def VALUE_CAFE_START() -> str:
        return "CAFE_START"
    
    @constant
    def VALUE_CODE_STATUS_CHECK() -> str:
        return "RMS_STATUS_CHECK"
    
    @constant
    def VALUE_CAFE_ERROR() -> str:
        return "CAFE_ERROR"
    
    @constant
    def VALUE_CODE_STATUS_RES() -> str:
        return "STATUS_RES"
    
    @constant
    def VALUE_CODE_ORDER_REQ() -> str:
        return "ORDER_REQ"
    
    @constant
    def VALUE_CODE_ORDER_RES() -> str:
        return "ORDER_RES"
    
    @constant
    def VALUE_STATUS_ID_WORKING() -> str:
        return "WORKING"
    
    @constant
    def VALUE_STATUS_ID_READY() -> str:
        return "READY"
    @constant
    def VALUE_STATUS_ID_ERROR() -> str:
        return "ERROR"
    


    @constant
    def VALUE_PRINTER_STATE_DATA_READY() -> str:
        return "DATA_READY"
    
    @constant
    def VALUE_PRINTER_STATE_PRINT_READY() -> str:
        return "PRINT_READY"
    
    @constant
    def VALUE_SEND_DATA() -> str:
        return "SEND_DATA"

    

CRCJsonKeyword = _CRCJsonKeyword()