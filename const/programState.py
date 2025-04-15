

def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    
    return property(func_get, func_set)



class _ProgramState(object):

    @constant
    def PLAY() -> str:
        return "play"
    
    @constant
    def PAUSE() -> str:
        return "pause"
    
    @constant
    def STOP() -> str:
        return "stop"
    
    

ProgramState = _ProgramState()
