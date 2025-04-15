def constant(func):
    def func_set(self, value):
        raise TypeError

    def func_get(self):
        return func()
    return property(func_get, func_set)



class _DelonghiState():

    @constant
    def NOT_READY() -> int:
        '''
        준비 안된 상태
        '''
        return -1   
    
    @constant
    def READY() -> int:
        '''
        준비 상태
        '''
        return 0   
    
    @constant
    def ERR_OPENED_WATER_TANK() -> int:
        '''
        물탱크 열린 상태
        '''
        return 1    
    
    @constant
    def ERR_EMPTY_WATER() -> int:
        '''
        물 부족 상태
        '''
        return 2    
    
    @constant
    def ERR_OPENED_GROUNDS_CONTAINER() -> int:
        '''
        커피 찌꺼기 통 열린 상태
        '''
        return 3    
    
    @constant
    def ERR_EMPTY_COFFEE_BEANS() -> int:
        '''
        커피 원두 부족 상태
        '''
        return 4    
    
    @constant
    def ERR_FULL_GROUNDS() -> int:
        '''
        커피 찌꺼기 통 가득 상태
        '''
        return 5    
    
    @constant
    def ERR_POLLUTION() -> int:
        '''
        석회 오염 상태
        '''
        return 6    
    
    @constant
    def ERR_POWERED_OFF() -> int:
        '''
        전원 꺼진 상태
        '''
        return 7    
    
    @constant
    def BREWING() -> int:
        '''
        커피 추출 중
        '''
        return 31   


DelonghiState = _DelonghiState()