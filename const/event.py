def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _Event(object):

    @constant
    def COMM_VAR_DISCONNECTED() -> int:
        return 2001
    
    @constant
    def COMM_VAR_FAILED_TO_CONNECT() -> int:
        return 2002
    

Event = _Event()
