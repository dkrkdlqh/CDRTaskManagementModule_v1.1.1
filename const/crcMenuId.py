

def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _CRCMenuId(object):

    @constant
    def HOT_AMERICANO() -> int:
        return 1000
    
    @constant
    def ICE_AMERICANO() -> int:
        return 1001
    
    @constant
    def HOT_ESPRESSO() -> int:
        return 1003
    
    @constant
    def HOT_WATER() -> int:
        return 1010
    
    @constant
    def BEER() -> int:
        return 3000
CRCMenuId = _CRCMenuId()
