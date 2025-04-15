def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _LoopType(object):

    @constant
    def ALWAYS() -> str:
        return "always"
    
    @constant
    def COUNT() -> str:
        return "count"
    
    @constant
    def VAR() -> str:
        return "var"
    
    

LoopType = _LoopType()
