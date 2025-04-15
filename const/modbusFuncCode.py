

def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _ModbusFuncCode(object):

    @constant
    def READ_COILS() -> str:
        return "Coils [01]"
    
    @constant
    def READ_HOLDING_REGISTERS() -> str:
        return "Holding Registers [03]"
    
    @constant
    def READ_INPUT_REGISTERS() -> str:
        return "Input Registers [04]"
    
    @constant
    def WRITE_MULTI_COILS() -> str:
        return "Multiple Coils [15]"
    
    @constant
    def WRITE_MULTI_REGISTERS() -> str:
        return "Multiple Registers [16]"
    
    @constant
    def WRITE_SINGLE_COILS() -> str:
        return "SC"
    
    @constant
    def WRITE_SINGLE_REGISTERS() -> str:
        return "SR"
    
    

ModbusFuncCode = _ModbusFuncCode()
