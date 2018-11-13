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
from selenium.webdriver.support.ui import Select

from append_purchase_tx_fenfen.models import ProbUser
from append_purchase_tx_fenfen.client_thread  import ThreadControl
from append_purchase_tx_fenfen.purchase_driver import get_driver
from append_purchase_tx_fenfen.models import KillPredict


from log99.pk_log import PkLog,GetDate,GetRule

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
    pk_logger.info("user_name:%s",user_name)
    pk_logger.info("password:%s",password)
    control = request.POST['control']

    #money_list = request.POST['auto_in_money']
    rule_id = request.POST['in_rule']
    in_money = request.POST['in_money']

    info_dict = {}
    info_dict["user_name"] = user_name
    info_dict["password"] = password
    #info_dict["money_list"] = money_list.split(',')

    info_dict["upper_money"] = int(request.POST['in_upper_monery_1'])
    info_dict["lower_money"] = int(request.POST['in_lower_monery_1'])

    info_dict["in_money"] = int(in_money)
    info_dict["rule_id"] = int(rule_id)

    #pk_logger.info("init money_list:%s",info_dict["money_list"])
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
    return render_to_response('append_purchase_tx_fenfen_main.html',{"prob_user_list":prob_user_list, "p_rule":request.POST['in_rule'], "p_monery":in_money,
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
                        #判断是否是最新一期并且之前未购买，防止重复购买
                        current_predicts = KillPredict.objects.filter(lottery_id = predict_id)
                        current_is_xiazhu = 0
                        for current_predict in current_predicts:
                            current_is_xiazhu = current_predict.is_xiazhu
                        print "result_info:",result_info
                        print "current_predicts.is_xiazhu:",current_is_xiazhu
                        pk_logger.info("current_is_xiazhu:%d", current_is_xiazhu)
                        if current_is_xiazhu == 0:
                            #通过购买历史获取倍数
                            current_date = GetDate().get_base_date()
                            #killpredicts = KillPredict.objects.filter(kill_predict_date = current_date).order_by("-lottery_id")
                            killpredicts = KillPredict.objects.filter(kill_predict_date = current_date, is_xiazhu = 1).order_by("-lottery_id")

                            front_multiple = 1
                            back_multiple = 1
                            is_xiazhu_list = []
                            front_multiple_list = []
                            front_hit_list = []
                            back_multiple_list = []
                            back_hit_list = []

                            purchase_rule_list = GetRule().get_purchase_multiple()
                            # if interval["rule_id"] == 1:
                            #     pk_logger.info("---------------rule 1")
                            #     pk_logger.info("---------------front_hit_list:%s",front_hit_list)
                            #     pk_logger.info("---------------front_multiple_list:%s",front_multiple_list)
                            #
                            #     for killpredict in killpredicts:
                            #         front_multiple_list.append(killpredict.front_multiple)
                            #         front_hit_list.append(killpredict.front_hit)
                            #         is_xiazhu_list.append(killpredict.is_xiazhu)
                            #
                            #
                            #     if len(front_hit_list) == 3:
                            #         if front_hit_list[1] == 1:
                            #             front_multiple = 1
                            #         #上期未中，上上期中了，停止2期
                            #         elif front_hit_list[2] == 1:
                            #             front_multiple = 1
                            #         else:
                            #             front_multiple = 0
                            #
                            #     if len(front_hit_list) > 3:
                            #         if front_hit_list[1] == 1:
                            #             front_multiple = 1
                            #         #上期未中，上上期中了，停止2期
                            #         elif front_hit_list[2] == 1:
                            #             front_multiple = 0
                            #         #上期未中，上上期未中，上上上期中， 停止1期
                            #         elif front_hit_list[3] == 1:
                            #             front_multiple = 0
                            #         #上期未中，上上期未中，上上上未期， 追加
                            #         else:
                            #             purchase_index = int(purchase_rule_list.index(front_multiple_list[3]))
                            #             if purchase_index == len(purchase_rule_list) - 1:
                            #                     front_multiple = 1
                            #             else:
                            #                 try:
                            #                     front_multiple = purchase_rule_list[int(purchase_rule_list.index(front_multiple_list[3])) + 1]
                            #                 except:
                            #                     front_multiple = 1
                            #
                            #
                            # else:
                            #     pk_logger.info("---------------rule 2")
                            #     for killpredict in killpredicts:
                            #         back_multiple_list.append(killpredict.back_multiple)
                            #         back_hit_list.append(killpredict.back_hit)
                            #         is_xiazhu_list.append(killpredict.is_xiazhu)


                            #获取下注倍数
                            # index_predict_sort = 0
                            # front_multiple = 1
                            # pk_logger.info("---------------rule_id:%d",interval["rule_id"])
                            # if interval["rule_id"] == 1:
                            #     pk_logger.info("---------------rule 1")
                            #     for killpredict in killpredicts:
                            #         #预测一期除外
                            #         if index_predict_sort == 1:
                            #             #上一期命中，倍数为1
                            #             if killpredict.front_hit == 1:
                            #                 pk_logger.info("---------------last hit")
                            #                 front_multiple = 1
                            #                 break
                            #         if index_predict_sort == 2:
                            #             #上上一期命中，本期不买，倍数为0
                            #             if killpredict.front_hit == 1:
                            #                 pk_logger.info("---------------last last hit")
                            #                 front_multiple = 0
                            #                 break
                            #         if index_predict_sort == 3:
                            #             if killpredict.front_hit == 1:
                            #                 purchase_rule_list = GetRule().get_purchase_multiple()
                            #                 purchase_index = purchase_rule_list.index(int(killpredict.front_multiple))
                            #                 pk_logger.info("---------------purchase_rule_list:%s",purchase_rule_list)
                            #                 #越界初始化
                            #                 if purchase_index == len(purchase_rule_list) - 1:
                            #                     front_multiple = 1
                            #                 else:
                            #                     try:
                            #                         pk_logger.info("---------------add increase,last purchase is:%d",killpredict.front_multiple)
                            #                         front_multiple = purchase_rule_list[purchase_rule_list.index(int(killpredict.front_multiple)) + 1]
                            #                     except:
                            #                         pk_logger.info("not exists %d",int(killpredict.front_multiple))
                            #                         front_multiple = 1
                            #             else:
                            #                 front_multiple = 1
                            #             break
                            #
                            #         index_predict_sort = index_predict_sort + 1
                            # else:
                            #     pk_logger.info("---------------rule 2")

                            pk_logger.info("last front_multiple:%s",front_multiple)
                            index_predict_sort = 0
                            back_multiple = 1


                            purchase_number_list = result_info['predict_number_list']
                            #获取投注倍数索引
                            purchase_number_money_index = [int(front_multiple), 0, 0, 0, int(back_multiple)]

                            in_money = interval['in_money']
                            pk_logger.info("start purchase, xiazhu money:%s",in_money)
                            rule_id = interval['rule_id']
                            #获取购买元素列表个数
                            purchase_element_list,buy_money = get_xiazhu_message_cai99(purchase_number_list,purchase_number_money_index, in_money, rule_id)
                            if len(purchase_element_list) > 0 and buy_money > 0:
                                # 购买
                                purchase_result = start_purchase(purchase_element_list, interval, buy_money)
                                input_money = len(purchase_element_list) * 1
                                if purchase_result:
                                    pk_logger.info("purchase sucess!, input money:%s",input_money)
                                    p = KillPredict.objects.get(lottery_id=predict_id)
                                    p.is_xiazhu = 1
                                    p.input_money = input_money
                                    p.front_multiple = front_multiple
                                    p.back_multiple = back_multiple
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
                                pk_logger.info("no element in purchase_element_list  or stop purchase")

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
def start_purchase(purchase_element_list, interval, buy_money):
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

        #设置倍数
        purchase_driver.find_element_by_xpath('/html/body/div/div[2]/div[4]/div/div[4]/div[5]/input').clear()
        time.sleep(1)
        print "clear money ok"

        purchase_driver.find_element_by_xpath('/html/body/div/div[2]/div[4]/div/div[4]/div[5]/input').send_keys(str(buy_money))
        time.sleep(1)
        print "set money ok"

        try:
            pk_logger.info("current xaizhu money:%d",int(buy_money))
            for purchase_element in purchase_element_list:

                pk_logger.info("start purchase purchase_element:%s",purchase_element)
                purchase_driver.find_element_by_xpath(purchase_element).click()
                time.sleep(1)


            #添加到投注
            purchase_driver.find_element_by_xpath('/html/body/div/div[2]/div[4]/div/div[4]/div[5]/span/button[1]').click()
            print "add touzhu "
            time.sleep(1)

            #确认投注
            purchase_driver.find_element_by_xpath('/html/body/div/div[2]/div[4]/div/div[4]/div[6]/div[2]/span[1]/button').click()
            print "add confirm"
            # print purchase_driver.page_source
            time.sleep(3)

            #提交
            purchase_driver.find_element_by_class_name('ngdialog-buttons').find_element_by_tag_name('button').click()
            print "purchase ok"
            time.sleep(3)
            pk_logger.info("purchase ok")
            return True
        except:
            pk_logger.error("purchase driver error time is invalid!!!")
            return False
    except:
        pk_logger.error("reload pk10 error !!!")
        return False


#根据预测list转换成要购买的元素
def get_xiazhu_message_cai99(purchase_number_str,purchase_number_money_index,xiazhu_money, rule_id):
    buy_element_list = []
    buy_money = xiazhu_money

    # purchase_number_str = '0,9|2|4|7,9|2|10|6,3|4|5|6|7|9,8|1|2|10,1|2|5|7|8|9,1|3|6|8|9|10'

    purchase_number_list = purchase_number_str.split(',')
    print "purchase_number_list",purchase_number_list
    if rule_id == 1:
        buy_money = xiazhu_money * purchase_number_money_index[0]
        temp_list = purchase_number_list[0].split('|')
        for temp in temp_list:
            xpath = '/html/body/div/div[2]/div[4]/div/div[4]/div[2]/div/p[1]/button[' + str(int(temp) + 1) + ']'
            buy_element_list.append(xpath)
    if rule_id == 2:
        buy_money = xiazhu_money * purchase_number_money_index[-1]
        temp_list = purchase_number_list[-1].split('|')
        for temp in temp_list:
            xpath = '/html/body/div/div[2]/div[4]/div/div[4]/div[2]/div/p[1]/button[' + str(int(temp) + 1) + ']'
            buy_element_list.append(xpath)

    return buy_element_list,buy_money



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
        while(1):
            #刷新开奖
            try:
                purchase_driver.find_element_by_xpath('/html/body/div/div[2]/div[3]/div/div/div[4]/p[1]/label/i').click()
                print "flush ok"
                time.sleep(5)
                avolid = int(str(purchase_driver.find_element_by_xpath('/html/body/div/div[2]/div[3]/div/div/div[3]/p[2]').text).split(':')[-1])
                if avolid > 20:
                    break
                else:
                    print "time is unenough"
                    time.sleep(3)
            except:
                print "wait flush"
                time.sleep(3)
        try:
            if interval["rule_id"] == 1:
                #后二
                purchase_driver.find_element_by_xpath('/html/body/div/div[2]/div[4]/div/div[1]/a[6]').click()
                print "back 2 ok"
                time.sleep(1)
            else:
                purchase_driver.find_element_by_xpath('/html/body/div/div[2]/div[4]/div/div[1]/a[7]').click()
                print "forhead 2 ok"
                time.sleep(1)

            #组选

            purchase_driver.find_element_by_xpath('/html/body/div/div[2]/div[4]/div/div[2]/p[2]/button[1]').click()
            print "zuxuan ok "
            time.sleep(1)

            #选择单位

            Select(purchase_driver.find_element_by_xpath('/html/body/div/div[2]/div[4]/div/div[4]/div[5]/select')).select_by_index(3)
            print "danwei ok"
            time.sleep(1)

        except:
            pk_logger.error("flush error,exit")
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
