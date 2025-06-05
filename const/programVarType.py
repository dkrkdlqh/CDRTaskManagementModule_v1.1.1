

def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _ProgramVarType(object):

    @constant
    def TYPE_INT() -> str:
        return "Int"
    
    @constant
    def TYPE_FLOAT() -> str:
        return "Float"
    
    @constant
    def TYPE_STR() -> str:
        return "String"
    
    @constant
    def TYPE_BOOL() -> str:
        return "Bool"
    
    @constant
    def TYPE_INT_ARRAY() -> str:
        return "Int Array"
    
    @constant
    def TYPE_FLOAT_ARRAY() -> str:
        return "Float Array"
    
    @constant
    def TYPE_STR_ARRAY() -> str:
        return "String Array"
    
    @constant
    def TYPE_BOOL_ARRAY() -> str:
        return "Bool Array"

    @constant
    def TYPE_TCP_IP() -> str:
        return "TCP/IP"
    
    @constant
    def TYPE_MODBUS_TCP() -> str:
        return "ModbusTCP"
    
    @constant
    def TYPE_MQTT() -> str:
        return "MQTT"
    
    @constant
    def TYPE_MELSEC_PLC() -> str:
        return "MELSEC PLC"
    
    @constant
    def TYPE_BLE() -> str:
        return "BLE"
    #250522
    @constant
    def TYPE_FASTECH_MOTOR() -> str:
        return "FASTECH MOTOR"
    @constant
    def TYPE_DIRECTION() -> str:
        return "Direction"
    @constant   
    def TYPE_VELOCITY() -> str:
        return "Velocity"

ProgramVarType = _ProgramVarType()
