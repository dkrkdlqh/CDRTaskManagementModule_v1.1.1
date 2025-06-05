def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _TPMJsonKeyword():

    @constant
    def TREE_PROGRAM() -> str:
        return "program"
    
    @constant
    def TREE_VARIABLE() -> str:
        return "variable"
    
    @constant
    def TREE_FUNC() -> str:
        return "function"
    
    @constant
    def TREE_EVENT() -> str:
        return "event"
    
    @constant
    def DEFAULT_NODE_ID() -> str:
        return "nodeId"
    
    @constant
    def DEFAULT_CMD_ID() -> str:
        return "cmdId"
    
    @constant
    def DEFAULT_CHILD_NODE_LIST() -> str:
        return "childNodeList"
    
    @constant
    def DEFAULT_ENABLE() -> str:
        return "enable"
    
    @constant
    def DEFAULT_FUNC_NAME() -> str:
        return "funcName"
    
    @constant
    def VAR_NAME() -> str:
        return "varName"
    
    @constant
    def VAR_TYPE() -> str:
        return "varType"
    
    @constant
    def VAR_VALUE() -> str:
        return "varValue"
    
    @constant
    def VAR_IP_ADDR() -> str:
        return "varIPAddr"
    
    @constant
    def VAR_IP_PORT() -> str:
        return "varIPPort"
    
    @constant
    def VAR_MQTT_USER_NAME() -> str:
        return "varMQTTUsername"
    
    @constant
    def VAR_MQTT_USER_PW() -> str:
        return "varMQTTUserPW"
    
    @constant
    def VAR_MQTT_SUBSCRIBE_TOPIC() -> str:
        return "varMQTTSubscribeTopic"
    
    @constant
    def VAR_BLE_MAC_ADDR() -> str:
        return "varBLEMacAddress"
    
    @constant
    def VAR_BLE_SERVICE_UUID() -> str:
        return "varBLEServiceUUID"
    
    @constant
    def VAR_BLE_CHARACTERISTIC_UUID() -> str:
        return "varBLECharacteristicUUID"
    
    @constant
    def VAR_BLE_DESCRIPTOR_UUID() -> str:
        return "varBLEDescriptorUUID"
    
    @constant
    def ASSIGN_TYPE() -> str:
        return "assignType"
    
    @constant
    def ASSIGN_VAR_NAME() -> str:
        return "assignVarName"
    
    @constant
    def ASSIGN_VAR_TYPE() -> str:
        return "assignVarType"

    @constant
    def ASSIGN_VAR_ARR_START_INDEX_TYPE() -> str:
        return "assignVarArrStartIndexType"
    
    @constant
    def ASSIGN_VAR_ARR_START_INDEX_VALUE() -> str:
        return "assignVarArrStartIndexValue"
    
    @constant
    def ASSIGN_VAR_ARR_START_INDEX_VAR_NAME() -> str:
        return "assignVarArrStartIndexVarName"
    
    @constant
    def ASSIGN_READ_VAR_NAME() -> str:
        return "assignReadVarName"
    
    @constant
    def ASSIGN_READ_VAR_ARR_INDEX() -> str:
        return "assignReadVarArrIndex"
    
    @constant
    def ASSIGN_VAR_VALUE() -> str:
        return "assignVarValue"
    
    @constant
    def ASSIGN_VAR_MATH_OPERATOR() -> str:
        return "assignVarMathOperator"
    
    @constant
    def WRITE_VAR_NAME() -> str:
        return "writeVarName"
    
    @constant
    def WRITE_VAR_TYPE() -> str:
        return "writeVarType"
    
    @constant
    def WRITE_VAR_VALUE() -> str:
        return "writeVarValue"
    
    @constant
    def WRITE_MQTT_PUBLISH_TOPIC() -> str:
        return "writeMqttPublishTopic"
    
    @constant
    def WRITE_MODBUS_ADDR() -> str:
        return "writeModbusAddr"
    
    @constant
    def WRITE_MODBUS_FUNC_CODE() -> str:
        return "writeModbusFuncCode"
    
    @constant
    def WRITE_MODBUS_VALUE_LIST() -> str:
        return "writeModbusValueList"
    
    @constant
    def WRITE_PLC_ADDR() -> str:
        return "writePLCAddr"
    
    @constant
    def WRITE_PLC_VALUE_LIST() -> str:
        return "writePLCValueList"
    
    @constant
    def WRITE_BLE_VALUE_LIST() -> str:
        return "writeBLEValueList"
    
    @constant
    def READ_VAR_NAME() -> str:
        return "readVarName"
    
    @constant
    def READ_VAR_TYPE() -> str:
        return "readVarType"
    
    @constant
    def SAVE_VAR_NAME() -> str:
        return "saveVarName"
    
    @constant
    def READ_VAR_MODBUS_ADDR() -> str:
        return "readVarModbusAddr"
    
    @constant
    def READ_VAR_MODBUS_FUNC_CODE() -> str:
        return "readVarModbusFuncCode"
    
    @constant
    def READ_VAR_MODBUS_DATA_NUM() -> str:
        return "readVarModbusDataNum"
    
    @constant
    def READ_VAR_PLC_ADDR() -> str:
        return "readVarPLCAddr"
    
    @constant
    def READ_VAR_PLC_DATA_NUM() -> str:
        return "readVarPLCDataNum"
    
    @constant
    def READ_VAR_MQTT_KEY_LIST() -> str:
        return "readVarMQTTKeyList"
    
    @constant
    def READ_VAR_MQTT_VALUE_ARR_INDEX() -> str:
        return "readVarMQTTValueArrIndex"
    
    @constant
    def READ_VAR_MQTT_VALUE_TYPE() -> str:
        return "readVarMQTTValueType"
    
    @constant
    def READ_VAR_BLE_PACKET_INDEX() -> str:
        return "readVarBLEPacketIndex"
    
    @constant
    def IF_LEFT_VAR_NAME() -> str:
        return "ifLeftVarName"
    
    @constant
    def IF_LEFT_VAR_TYPE() -> str:
        return "ifLeftVarType"
    
    @constant
    def IF_LEFT_VAR_PLC_ADDR() -> str:
        return "ifLeftVarPLCAddr"
    
    @constant
    def IF_LEFT_VAR_MODBUS_FUNC_CODE() -> str:
        return "ifLeftVarModbusFuncCode"
    
    @constant
    def IF_LEFT_VAR_MODBUS_ADDR() -> str:
        return "ifLeftVarModbusAddr"
    
    @constant
    def IF_LEFT_VAR_ARR_START_INDEX_TYPE() -> str:
        return "ifLeftVarArrStartIndexType"
    
    @constant
    def IF_LEFT_VAR_ARR_START_INDEX_VALUE() -> str:
        return "ifLeftVarArrStartIndexValue"
    
    @constant
    def IF_LEFT_VAR_ARR_START_INDEX_VAR_NAME() -> str:
        return "ifLeftVarArrStartIndexVarName"
    
    @constant
    def IF_LEFT_VAR_ARR_DATA_LEN() -> str:
        return "ifLeftVarArrDataLen"
    
    @constant
    def IF_LEFT_VAR_MQTT_KEY_LIST() -> str:
        return "ifLeftVarMQTTKeyList"
    
    @constant
    def IF_LEFT_VAR_MQTT_VALUE_TYPE() -> str:
        return "ifLeftVarMQTTValueType"
    
    @constant
    def IF_LEFT_VAR_MQTT_VALUE_ARR_INDEX() -> str:
        return "ifLeftVarMQTTValueArrIndex"
    
    @constant
    def IF_OPERATOR() -> str:
        return "ifOperator"
    
    @constant
    def IF_RIGHT_VAR_TYPE() -> str:
        return "ifRightVarType"
    
    @constant
    def IF_RIGHT_VAR_VALUE() -> str:
        return "ifRightVarValue"
    
    @constant
    def IF_RIGHT_VAR_ARR_START_INDEX() -> str:
        return "ifRightVarArrStartIndex"
    
    @constant
    def EVENT_CYCLE() -> str:
        return "eventCycle"
    
    @constant
    def WAIT_OPTION() -> str:
        return "waitOption"
    
    @constant
    def WAIT_TIME_VALUE() -> str:
        return "waitTimeValue"
    
    @constant
    def LOOP_TYPE() -> str:
        return "loopType"
    
    @constant
    def LOOP_COUNT() -> str:
        return "loopCount"
    
    @constant
    def LOOP_VAR_NAME() -> str:
        return "loopVarName"
    
    @constant
    def BOOK_MARKNAME() -> str:
        return "bookmarkName"
    
    @constant
    def FUNC_NAME() -> str:
        return "funcName"
    
    @constant
    def RETURN_VALUE_LIST() -> str:
        return "returnValueList"
    
    @constant
    def RETURN_NAME() -> str:
        return "returnName"
    
    @constant
    def RETURN_TYPE() -> str:
        return "returnType"
    
    @constant
    def RETURN_VALUE() -> str:
        return "returnValue"
    
    @constant
    def PARAM_VALUE_LIST() -> str:
        return "paramValueList"
    
    @constant
    def PARAM_NAME() -> str:
        return "paramName"
    
    @constant
    def PARAM_TYPE() -> str:
        return "paramType"
    
    @constant
    def PARAM_VALUE() -> str:
        return "paramValue"
    
    #250522
    @constant
    def VAR_BOARD_ID() -> int:
        return "varFastechMotorId"
    
    @constant
    def VAR_BOARD_TYPE() -> str:
        return "varFastechMotorBoardType"


TPMJsonKeyword = _TPMJsonKeyword()