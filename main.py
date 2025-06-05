import sys
import datetime
import logging
import traceback
import os


from mainController import MainController

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("error : create directory")


def createFile(filePath:str):
    try:
        if not os.path.exists(filePath):
            with open(filePath, 'w') as file:
                file.close()
    except OSError:
        print("error : create file")


def errorHandler(errType, value, traceType):

    divider:str = "+" * 70
    timeStr         :str = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    errorTraceMsg   :str = "".join(traceback.format_exception(errType, value, traceType))
    # # 에러 내용 파일에 저장  
    logging.error("\nError occurred at " + timeStr + "\n" + divider + "\n" + errorTraceMsg + divider + "\n\n")

    # # 에러 내용 출력 ..
    print("\nError occurred at " + timeStr + "\n" + divider + "\n" + errorTraceMsg + divider + "\n\n")

    #에러 처리 후, 프로그램 강제 종료
    #os._exit(1)

# 기록용 폴더 및 파일 생성
createFolder("./logs")
createFile("./logs/history.log")


logging.basicConfig(filename="./logs/history.log", level=logging.ERROR, force=True, encoding='utf-8')


if __name__ == "__main__" :
    
    sys.excepthook = errorHandler

    mainController = MainController()
