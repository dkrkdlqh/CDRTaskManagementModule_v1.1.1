

def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _Operator(object):

    @constant
    def SMALL() -> str:
        return "<"
    
    @constant
    def SMALL_OR_EQUAL() -> str:
        return "<="
    
    @constant
    def EQUAL() -> str:
        return "=="
    
    @constant
    def NOT_EQUAL() -> str:
        return "!="
    
    @constant
    def BIG() -> str:
        return ">"
    
    @constant
    def BIG_OR_EQUAL() -> str:
        return ">="
    
Operator = _Operator()
