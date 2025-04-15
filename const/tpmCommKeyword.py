def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)


class _TPMCommKeyword():

    @constant
    def CDR_STR() -> str:
        return "CDR_STR"
    
    @constant
    def CDR_END() -> str:
        return "CDR_END"
    
    @constant
    def KEY_METHOD() -> str:
        return "method"
    
    @constant
    def KEY_PARAMS() -> str:
        return "params"
    
    @constant
    def METHOD_PLAY_PROGRAM() -> str:
        return "playProgram"
    
    @constant
    def METHOD_PAUSE_PROGRAM() -> str:
        return "pauseProgram"
    
    @constant
    def METHOD_RESUME_PROGRAM() -> str:
        return "resumeProgram"
    
    @constant
    def METHOD_STOP_PROGRAM() -> str:
        return "stopProgram"
    
    @constant
    def METHOD_GET_SYS_INFO() -> str:
        return "getSysInfo"
    
    @constant
    def METHOD_REALTIME_INFO() -> str:
        return "realtimeInfo"


TPMCommKeyword = _TPMCommKeyword()