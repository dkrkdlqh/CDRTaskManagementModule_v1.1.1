

def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _ValueAssignType(object):

    @constant
    def VAR() -> str:
        return "var"
    
    @constant
    def INPUT() -> str:
        return "input"
    
    

ValueAssignType = _ValueAssignType()
