from const.config import Config
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import os

class CDRLog:
    #mini 250114 log에 save기능 추가
    def __init__(self, log_file: str, when: str = "midnight", interval: int = 1, backup_count: int = 7, level: int = logging.INFO, log_format: str = None):
        """
        날짜별로 로그 파일을 관리하는 로거 초기화
        :param log_file: 로그 파일 기본 경로 (예: "logs/app.log")
        :param when: 새로운 로그 파일을 생성할 시간 기준 (기본값: 'midnight')
        :param interval: 시간 간격 (기본값: 1, 단위는 when)
        :param backup_count: 유지할 백업 파일 개수 (기본값: 7)
        :param level: 로깅 레벨 (기본값: logging.INFO)
        :param log_format: 로그 포맷 (기본값: None, 기본 포맷 사용)
        """
        # 로그 파일의 폴더 경로 추출
        log_dir = os.path.dirname(log_file)

        # 폴더가 없으면 생성
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        self.logger = logging.getLogger(log_file)  # 로거 이름을 파일명으로 설정
        self.logger.setLevel(level)
        self.logger.propagate = False
        # 이미 핸들러가 추가된 경우 중복 추가 방지
        if not self.logger.hasHandlers():
            # 기본 로그 포맷 설정
            log_format = log_format or "%(asctime)s - %(levelname)s - %(message)s"
            formatter = logging.Formatter(log_format)

            # TimedRotatingFileHandler 설정
            file_handler = TimedRotatingFileHandler(
                log_file,
                when=when,
                interval=interval,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            
            # 날짜별 로그를 생성하는 로거
        # log_file = "logs/app.log"  # logs 폴더에 로그 파일 생성
        # self.logger = CDRLog(log_file).get_logger()

    def get_logger(self) -> logging.Logger:
        """로거 객체 반환"""
        return self.logger
    
    @classmethod
    def print(self, msg:object) :
        '''
        ### CDR Log
        '''
        if Config.DEBUG_MODE == True:
            current_time = datetime.now()
            print(f"[CDRLog] {current_time} >> {msg}")  #mini 250107
            self.Log(f"[CDRLog] {msg}")
        #    print(f"[CDRLog] {msg}")
        
    @classmethod
    def Log(self, msg:object) :             
        '''
        ### CDR Log - log파일에만 남고, 콘솔에는 표시 X
        '''
        log_file = "logs/app.log" 
        logger = CDRLog(log_file).get_logger()
        if Config.DEBUG_MODE == True:
            logger.info(msg)

        