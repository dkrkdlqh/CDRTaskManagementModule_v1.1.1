def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _CommandId(object):

    @constant
    def ROOT() -> str:
        return "Root"

    @constant
    def EMPTY() -> str:
        return "Empty"
    
    @constant
    def VARIABLE() -> str:
        return "Variable"
    
    @constant
    def EVENT() -> str:
        return "Event"
    
    @constant
    def ASSIGNMENT() -> str:
        return "Assignment"
    
    @constant
    def WRITE() -> str:
        return "Write"
    
    @constant
    def READ() -> str:
        return "Read"
    
    @constant
    def IF() -> str:
        return "If"
    
    @constant
    def ELIF() -> str:
        return "Else if"
    
    @constant
    def ELSE() -> str:
        return "Else"
    
    @constant
    def WAIT() -> str:
        return "Wait"
    
    @constant
    def LOOP() -> str:
        return "Loop"
    
    @constant
    def BREAK() -> str:
        return "Break"
    
    @constant
    def BOOKMARK() -> str:
        return "Bookmark"
    
    @constant
    def GOTO() -> str:
        return "GoTo"
    
    @constant
    def TERMINATE() -> str:
        return "Terminate"
    
    @constant
    def FUNCITON() -> str:
        return "Function"
    
    @constant
    def CALLFUNC() -> str:
        return "CallFunc"
    
    

CommandId = _CommandId()
