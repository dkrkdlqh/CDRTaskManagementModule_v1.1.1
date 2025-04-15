

def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _MathOperatorType(object):

    @constant
    def PLUS() -> str:
        return "plus"
    
    @constant
    def MINUS() -> str:
        return "minus"
    
    @constant
    def MULTIPLY() -> str:
        return "multiply"
    
    @constant
    def DIVIDE() -> str:
        return "divide"
    
    @constant
    def REMAIN() -> str:
        return "remain"
    
    

MathOperatorType = _MathOperatorType()
