#coding=utf-8
__author__ = 'shifeixiang'
import logging
import time


class GetDate:
    def get_base_date(self):
        return time.strftime("%Y%m%d", time.localtime())
    def get_base_date_forward_six(self):
        return time.strftime('%Y%m%d',time.localtime())
    def get_base_date_forward_six_real(self):
        return time.strftime('%Y%m%d',time.localtime(time.time() - 6*3600))


class GetRule:
    def get_purchase_multiple(self):
        #return [1,3,9,29,92,293,942]
        return [1,2,4,9,19,41,89,192,416,906,1970]

# 创建一个logger
class PkLog:
    pk_name = ''
    def __init__(self,pk_name):
        PkLog.pk_name = pk_name

    def log(self):
        logger = logging.getLogger(self.pk_name)
        logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler('./log99/log_file/' + GetDate().get_base_date() + '_pk10.log')
        fh.setLevel(logging.DEBUG)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger