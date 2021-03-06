#coding=utf-8
__author__ = 'shifeixiang'
import time
import threading
import datetime
import append_predict_tx_fenfen.predict_main

from log99.pk_log import PkLog

pk_logger = PkLog('append_predict_tx_fenfen.thread').log()

class Spider(threading.Thread):
    # __metaclass__ = Singleton
    thread_stop = False
    thread_num = 0
    interval = {}
    behavior = None
    def run(self):
        self.behavior(self,self.thread_num,self.interval)
    def stop(self):
        self.thread_stop = True

class ThreadControl():
    thread_stop = False
    current_thread = {}
    def start(self,thread_num,interval):
        spider = Spider()
        spider.behavior = loaddata
        spider.thread_num = thread_num
        spider.interval = interval
        spider.start()
        self.current_thread[str(thread_num)] = spider
    #判断进程是否活跃
    def is_alive(self,thread_num):
        tt = self.current_thread[str(thread_num)]
        return tt.isAlive()
    #获取当前线程名称
    # def get_name(self):
    def stop(self,thread_num):
        #print "stop"
        pk_logger.info("stop")
        spider = self.current_thread[str(thread_num)]
        spider.stop()

def loaddata(c_thread,thread_num,interval):
    base_date = time.strftime("%Y%m%d", time.localtime())
    count = 0
    #初次启动开始购买---可以通过购买记录来初始化last_minute
    last_minute = -1
    while not c_thread.thread_stop:
        flag_date = time.strftime("%H:%M:%S", time.localtime())
        # print "flag_date:",flag_date

        current_minute = (datetime.datetime.now()).minute
        current_hour = (datetime.datetime.now()).hour
        current_date = time.strftime("%Y%m%d %H:%M:%S", time.localtime())
        jump_flag_date = time.strftime("%H:%M:%S", time.localtime())
        if jump_flag_date > '23:02:00' or jump_flag_date < '00:58:00':
            time.sleep(60)
        else:
            pk_logger.info("start predict")
            append_predict_tx_fenfen.predict_main.spider_save_predict(interval)
            time.sleep(1)
    #print "exit!"
    pk_logger.info("exit")
    time.sleep(10)
    interval['driver'].quit()
