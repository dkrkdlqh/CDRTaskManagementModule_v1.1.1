

def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _WaitType(object):

    @constant
    def TIME() -> str:
        return "time"
    
    @constant
    def CONDITION() -> str:
        return "condition"
    
    

WaitType = _WaitType()
