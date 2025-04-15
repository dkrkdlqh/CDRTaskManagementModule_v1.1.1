def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)


class _Config(object):

    @constant
    def VERSION() -> str:
        return "1.1.0"
    
    @constant
    def TPM_SERVER_IP() -> str:
        return "127.0.0.1"
    
    @constant
    def TPM_SERVER_PORT() -> int:
        return 200
    
    @constant
    def PROGRAM_FILE_PATH() -> str:
        return "tpmProgram.json"
    
    @constant
    def DEBUG_MODE() -> bool:
        return True
    
    @constant
    def KEY_QUIT() -> str:
        return "q"
    
    @constant
    def KEY_PLAY_DEFAULT_PROGRAM() -> str:
        return "p"
    
    @constant
    def KEY_STOP_DEFAULT_PROGRAM() -> str:
        return "s"
    

Config = _Config()
    