# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import random
import datetime

from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误
from django.shortcuts import render_to_response
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from append_purchase_tx_fenfen.models import ProbUser
from append_purchase_tx_fenfen.client_thread  import ThreadControl
from append_purchase_tx_fenfen.purchase_driver import get_driver
from append_purchase_tx_fenfen.models import KillPredict

from log99.pk_log import PkLog,GetDate

pk_logger = PkLog('append_purchase_tx_fenfen.purchase_client_main').log()

class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class SingleDriver(Singleton):
    # def __init__(self, driver):
    #   self.driver = driver
    def get_driver(self):
        return self.driver
    def set_driver(self, driver):
        self.driver = driver

class SingleDriverMultiple(Singleton):
    # def __init__(self, driver):
    #   self.driver = driver
    def get_driver(self):
        return self.driver
    def set_driver(self, driver):
        self.driver = driver


@csrf_exempt   #处理Post请求出错的情况
def control_probuser_thread(request):
    user_name = request.POST['user_name']
    password = ProbUser.objects.get(user_name=user_name).user_password;
    #print "password:",password
    pk_logger.info("user_name:%s",user_name)
    pk_logger.info("password:%s",password)
    control = request.POST['control']

    money_list = request.POST['auto_in_money']
    rule_id = request.POST['in_rule']

    info_dict = {}
    info_dict["user_name"] = user_name
    info_dict["password"] = password
    info_dict["money_list"] = money_list.split(',')
    info_dict["rule_id"] = int(rule_id)

    info_dict["upper_money"] = int(request.POST['in_upper_monery_1'])
    info_dict["lower_money"] = int(request.POST['in_lower_monery_1'])

    pk_logger.info("init money_list:%s",info_dict["money_list"])
    #显示活跃状态
    prob_user = ProbUser.objects.get(user_name=user_name)
    if control == 'start':

        #杀号的driver
        #driver = spider_predict_selenium()
        #info_dict["driver"] = driver

        #购买driver
        #单例模式
        try:
            web_driver = SingleDriver()
            driver = web_driver.get_driver()
            info_dict["purchase_driver"] = driver
        except:
            web_driver = SingleDriver()
            driver = get_driver(user_name,password)
            web_driver.set_driver(driver)
            info_dict["purchase_driver"] = driver
        #状态信息
        c  = ThreadControl()
        #出现错误，则线程不存在，因此启动线程
        try:
            status = c.is_alive(user_name)
            #print "thread is alive? ",status
            pk_logger.warn("thread is alive?:%s",status)
            if status:
                #print "thread is alive,caonot start twice!"
                pk_logger.warn("thread is alive,caonot start twice!")
            else:
                #print "start ..........thread1"
                pk_logger.warn("start ..........thread1")
                c.start(user_name, info_dict)
        except:
            #print "thread is not alive start!!!"
            pk_logger.warn("thread is not alive start!!!")
            c.start(user_name, info_dict)
        prob_user.user_status = 1
        prob_user.save()
    if control == 'stop':
        c  = ThreadControl()
        try :
            c.stop(user_name)
            prob_user.user_status = 0
            prob_user.save()
        except:
            #print "not thread alive"
            pk_logger.warn("not thread alive")
    prob_user_list =  ProbUser.objects.all()
    return render_to_response('append_purchase_tx_fenfen_main.html',{"prob_user_list":prob_user_list, "p_rule":request.POST['in_rule'], "p_monery":money_list,
                                                "p_upper_monery_1":request.POST['in_upper_monery_1'], "p_lower_monery_1":request.POST['in_lower_monery_1']})
    # return render_to_response('qzone_info.html',{"thread_name":th_name, "control":control, "thread_list":thread_list,"info_active":info_active})

#主页面
def auto_admin(request):
    # ProbTotals.objects.all().delete()
    # thread_list =  ProbUser.objects.get(thread_name=th_name)
    prob_user_list =  ProbUser.objects.all()
    for prob_user in prob_user_list:
        c  = ThreadControl()
        try:
            #查看是否处于活跃状态
            status = c.is_alive(prob_user.user_name)
            if status:
                #设置状态为1
                prob_user.user_status = 1
                prob_user.save()
            else:
                #设置状态为0
                prob_user.user_status = 0
                prob_user.save()
        except:
            pk_logger.info("%s not start",prob_user.user_name)
            #print prob_user.user_name, " not start"
            prob_user.user_status = 0
            prob_user.save()
    return render_to_response('append_purchase_tx_fenfen_main.html',{"prob_user_list":prob_user_list})


#抓取，保存，自动购买
def get_predict_kill_and_save(interval):
    #购买流程
    purchase_flag_confirm = True
    while(purchase_flag_confirm):
        purchase_flag_minute = int(time.strftime("%M", time.localtime())) % 10
        purchase_flag_second = int(time.strftime("%S", time.localtime()))
        if 1:
            result_info = get_server_request_info()
            if 1:
                #判断是否获取接口数据正确
                if result_info:
                    last_id = int(result_info['last_lottery_id'])
                    predict_id = int(result_info['predict_lottery_id'])
                    pk_logger.info("last_id,predict_id:%d, %d", last_id, predict_id)
                    #判断是否成功拿到predict
                    if predict_id > last_id:
                        #判断是否是最新一期并且之前为购买
                        current_predicts = KillPredict.objects.filter(lottery_id = predict_id)
                        current_is_xiazhu = 0
                        for current_predict in current_predicts:
                            current_is_xiazhu = current_predict.is_xiazhu
                        # save_predict_time = datetime.datetime.strptime(result_info['save_predict_time'],'%Y%m%d %H:%M:%S')
                        # current_time = datetime.datetime.now()
                        print "result_info:",result_info
                        print "current_predicts.is_xiazhu:",current_is_xiazhu
                        # if (current_time - save_predict_time).seconds > 12000:
                        #     pk_logger.info("unfounded new predict,purchase faild!")
                        #     purchase_flag_confirm = False
                        pk_logger.info("current_is_xiazhu:%d", current_is_xiazhu)
                        if current_is_xiazhu == 0:
                            purchase_number_list = result_info['predict_number_list']
                            #获取投注倍数索引
                            purchase_number_money_index = result_info['purchase_number_money_index']

                            money_list = interval['money_list']
                            pk_logger.info("start purchase, xiazhu money:%s",money_list)
                            #获取购买元素列表个数
                            purchase_element_list,buy_money_list = get_xiazhu_message_cai99(purchase_number_list,purchase_number_money_index, money_list)
                            if len(purchase_element_list) > 0:
                                # 购买
                                purchase_result = start_purchase(purchase_element_list, interval, buy_money_list)
                                input_money = len(purchase_element_list) * 1
                                if purchase_result:
                                    pk_logger.info("purchase sucess!, input money:%s",input_money)
                                    p = KillPredict.objects.get(lottery_id=predict_id)
                                    p.is_xiazhu = 1
                                    p.input_money = input_money
                                    p.save()
                                    pk_logger.info("save xiazhu args sucess!")
                                    purchase_driver = interval['purchase_driver']

                                    #取消余额不足
                                    try:
                                        #'/html/body/div[3]/div[2]/div/div/div/div/div[3]/button[1]'
                                        purchase_driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div/div/div[3]/button[1]').click()
                                        print "yu e buzu!"
                                    except:
                                        print "yu e chongzu!"
                                    time.sleep(1)
                                    #删除
                                    try:

                                        purchase_driver.find_element_by_xpath('//*[@id="lt_cf_clear"]').click()
                                        time.sleep(1)
                                        #'/html/body/div[3]/div[2]/div/div/div/div/div[3]/button[2]'
                                        purchase_driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div/div/div[3]/button[2]').click()
                                        time.sleep(1)
                                        print "delete ok"
                                    except:
                                        print "delete error"
                                else:
                                    #print "purchase faild!"
                                    pk_logger.info("purchase faild!")
                            else:
                                #print 'no element in purchase_element_list '
                                pk_logger.info("no element in purchase_element_list")

                            purchase_flag_confirm = False
                        else:
                            pk_logger.info("wait time until predict ok!")
                            time.sleep(5)
                    else:
                        #purchase_flag_confirm = False
                        pk_logger.info("wait time until shahao message save ok")
                        time.sleep(3)
                else:
                    pk_logger.info("get server interface error!")
                    purchase_flag_confirm = False
                    time.sleep(1)
        else:
            time.sleep(1)
            purchase_flag_confirm = False
            #print "purchase time is no region!"
            pk_logger.info("purchase time is no region!")


#购买
def start_purchase(purchase_element_list, interval, buy_money_list):
    #计算历史总盈利
    gain_all_money = 0
    # current_date = time.strftime('%Y%m%d',time.localtime(time.time()))
    current_date = GetDate().get_base_date_forward_six()

    sum_objects_predict = KillPredict.objects.filter(kill_predict_date = current_date)
    for gain in sum_objects_predict:
        if (gain.gain_money):
            gain_all_money = gain_all_money + gain.gain_money
    #print "gain_all_money:",gain_all_money
    pk_logger.info("calc gain_all_money:%d", gain_all_money)
    #开始购买
    try:
        interval['purchase_driver'] = reload_pk10_driver(interval['purchase_driver'], interval)
        purchase_driver = interval['purchase_driver']

        #time.sleep(1)
        purchase_driver.find_element_by_xpath('//*[@id="lt_cf_clear"]/a').click()
        time.sleep(1)
        purchase_driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div/div/div[3]/button[2]').click()
        time.sleep(1)
        print "delete ok"

        try:
            money_index = 0
            for purchase_element in purchase_element_list:

                pk_logger.info("start purchase purchase_element:%s",purchase_element)
                pk_logger.info("current xaizhu money:%d",int(buy_money_list[money_index]))
                sub_element = purchase_driver.find_element_by_xpath(purchase_element)
                #追加下注
                sub_element.click()
                time.sleep(1)
                set_money_element = purchase_driver.find_element_by_xpath('//*[@id="lt_sel_times"]')
                set_money_element.send_keys(str(int(buy_money_list[money_index])))
                time.sleep(1)
                #添加注单
                confirm_button = purchase_driver.find_element_by_xpath('//*[@id="lt_sel_insert"]')
                confirm_button.click()
                time.sleep(1)
                money_index = money_index + 1

            #投注
            commit_button = purchase_driver.find_element_by_xpath('//*[@id="lt_buy"]')
            commit_button.click()
            time.sleep(1)
            pk_logger.info("commit ok")
            #确定
            submit_button =  purchase_driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div/div/div[3]/button[2]')
            #submit_button = purchase_driver.find_element_by_xpath('//*[@id="myLayer_1"]/tbody/tr/td/div[3]/a[2]')
            submit_button.click()
            time.sleep(1)
            pk_logger.info("purchase ok")
            return True
        except:
            pk_logger.error("purchase driver error time is invalid!!!")
            return False
    except:
        pk_logger.error("reload pk10 error !!!")
        return False


#根据预测list转换成要购买的元素
def get_xiazhu_message_cai99(purchase_number_str,purchase_number_money_index,input_xiazhu_money_list):
    buy_element_list = []
    buy_money_list = []
    # purchase_number_str = '0,9|2|4|7,9|2|10|6,3|4|5|6|7|9,8|1|2|10,1|2|5|7|8|9,1|3|6|8|9|10'
    # purchase_number_list = purchase_number_str.split(',')

    #分解购买单双号
    print "purchase_number_list",purchase_number_str
    purchase_number_list = purchase_number_str.replace(" ","").replace('[',"").replace(']',"").split(',')
    print "purchase_number_list",purchase_number_list

    #分解下注索引
    print "purchase_number_money_index",purchase_number_money_index
    purchase_number_money_list = purchase_number_money_index.replace(" ","").replace('[',"").replace(']',"").split(',')
    print "purchase_number_money_list:",purchase_number_money_list
    print "input_xiazhu_money_list:",input_xiazhu_money_list

    for index in range(len(purchase_number_list)):
        if purchase_number_list[index] == '-1':
            pass
        else:
            buy_money_list.append(input_xiazhu_money_list[int(purchase_number_money_list[index])])
            #万位
            #//*[@id="lt_selector"]/div[1]/div/div[1]/div[3]/ul/li[5]   奇
            #//*[@id="lt_selector"]/div[1]/div/div[1]/div[3]/ul/li[6]   偶

            #千位
            #//*[@id="lt_selector"]/div[1]/div/div[2]/div[3]/ul/li[5]
            #//*[@id="lt_selector"]/div[1]/div/div[2]/div[3]/ul/li[6]
            if purchase_number_list[index] == '1':

                #xpath = '//*[@id="itmStakeInput2' + column + '1' + value + '"]'
                xpath = '//*[@id="lt_selector"]/div[1]/div/div[' + str(index+1) + ']/div[3]/ul/li[5]'
                #print "xpath:",xpath
                buy_element_list.append(xpath)
            if purchase_number_list[index] == '0':
                xpath = '//*[@id="lt_selector"]/div[1]/div/div[' + str(index+1) + ']/div[3]/ul/li[6]'
                #print "xpath:",xpath
                buy_element_list.append(xpath)
                #buy_element_list.append('//*[@id="a_B' + str(index+1) + '_' + str(purchase_number) + '"]/input')
    return buy_element_list,buy_money_list



def restart_pk10_driver(purchase_driver,interval):

    if 1:
        purchase_driver = get_driver(interval['user_name'],interval['password'])
        try:
            element = WebDriverWait(purchase_driver, 15).until(EC.presence_of_element_located((By.ID , "inw_1_1")))
            pk_logger.info("click 1-10 ok")
        except:
            pk_logger.error("click 1-10 error,wait 5s")
            time.sleep(5)
            restart_pk10_driver(purchase_driver, interval)
    else:
        pk_logger.error("reload pk10 error,exit")
        time.sleep(2)
        purchase_driver.quit()
        pk_logger.error("reload pk10 error,restart")
        time.sleep(5)
        #'http://mem4.bbafon311.lbjthg.com/Index.aspx'
        #'http://mem4.bbafon311.lbjthg.com/'
        purchase_driver = get_driver(interval['user_name'],interval['password'])
        reload_pk10_driver(purchase_driver, interval)

    return purchase_driver

def reload_pk10_driver(purchase_driver,interval):

    #1-10
    if 1:
        #purchase_url = purchase_driver.current_url
        #pk_logger.info("purchase_url:%s",purchase_url)
        purchase_driver.get('https://28c99.com/bettingHall/betScreen?lotId=54&pid=507')
        time.sleep(1)
        try:
            #定位胆
            element_1_10 = purchase_driver.find_element_by_xpath('//*[@id="tabbar-div-s2"]/span[7]/span')
            element_1_10.click()
        except:
            pk_logger.warn("not found dinwgeidan.")
        try:
            element = WebDriverWait(purchase_driver, 15).until(EC.presence_of_element_located((By.ID , "lt_selector")))
            pk_logger.info("find inw_1_1 ok")
        except:
            pk_logger.error("find inw_1_1 error,exit")
            time.sleep(10)
            reload_pk10_driver(purchase_driver, interval)
        #interval['user_name'],interval['password']


    #pk_logger.info("click 1-10 ok")
    return purchase_driver

import json
import urllib2
def get_server_request_info():
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    url = 'http://127.0.0.1:8006/get_append_predict_data/'
    request_flag = True
    count = 0
    while(request_flag):
        try:
            req = urllib2.Request(url = url, headers = headers)
            page = urllib2.urlopen(req, timeout=10)
            html = page.read()
            result_info = html
            info_dict = json.loads(result_info)
            request_flag = False
            return info_dict
        except:
            #print "request server faild!"
            pk_logger.error(" get server request info request server faild!")
            time.sleep(3)
            if count > 2:
                request_flag = False
            count = count + 1
    return {}


def get_lottery_msg(request):
    current_date = GetDate().get_base_date_forward_six()
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=current_date)
    #print "obj_pro",obj_pro_predict
    return render_to_response('test.html',{"obj_pro_predict":obj_pro_predict})
