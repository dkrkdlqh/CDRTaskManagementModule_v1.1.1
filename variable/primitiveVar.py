
from const.mathOperatorType import MathOperatorType


class PrimitiveVar :

    def __init__(self, value, name=None) :

        self.__value = value
        self.name = name

    def __del__(self):
        print('PrimitiveVar instance is deleted.')
        

    def setValue(self, value):
        
        self.__value = value
        

    def setListValue(self, startIndex, endIndex, valueList):

        self.__value[startIndex : endIndex] = valueList
        

    def getValue(self):
        
        return self.__value
    

    def mathOperate(self, operator:str, value):

        if operator == MathOperatorType.PLUS:
            self.plus(value)
        
        elif operator == MathOperatorType.MINUS:
            self.minus(value)

        elif operator == MathOperatorType.MULTIPLY:
            self.multiply(value)

        elif operator == MathOperatorType.DIVIDE:
            self.divide(value)

        elif operator == MathOperatorType.REMAIN:
            self.remain(value)


    def plus(self, value):

        self.__value += value

    
    def minus(self, value):

        self.__value -= value


    def multiply(self, value):

        self.__value *= value

    
    def divide(self, value):

        self.__value /= value


    def remain(self, value):

        self.__value %= value