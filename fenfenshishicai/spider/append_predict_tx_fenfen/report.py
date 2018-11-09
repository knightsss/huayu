#coding=utf-8
__author__ = 'shifeixiang'

from django.views.decorators.csrf import csrf_exempt    #用于处理post请求出现的错误
from django.shortcuts import render_to_response
import time
from append_purchase_tx_fenfen.models import KillPredictTotal
from append_purchase_tx_fenfen.models import KillPredict
from append_purchase_tx_fenfen.models import PredictLottery
import datetime
from append_predict_tx_fenfen.spider_pk10 import get_html_result,get_lottery_id_number,load_lottery_predict
from append_predict_tx_fenfen.predict_main import calculate_percisoin


from log99.pk_log import PkLog,GetDate

pk_logger = PkLog('append_predict_tx_fenfen.report').log()

def predict_report(request):
    current_date = GetDate().get_base_date_forward_six()
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=current_date)
    #print "obj_pro",obj_pro_predict
    return render_to_response('append_predict_list.html',{"obj_pro_predict":obj_pro_predict})

#更新，处理lottery_number为空的情况
def control_predict_report(request):
    try:
        in_date= request.POST['in_date']
    except:
        in_date = time.strftime('%Y%m%d',time.localtime(time.time()))

    KillPredictTotal.objects.all().delete()
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=in_date)
    target_count = 0
    all_count = 0
    gain_all_money = 0
    xiazhu_all_money = 0
    #检查是否有lottery_num为空的情况
    all_record_count = len(obj_pro_predict)
    record_index = 0
    for sub_predict in obj_pro_predict:
        lottery_id = sub_predict.lottery_id
        lottery_number = sub_predict.lottery_number
        kill_predict_number = sub_predict.kill_predict_number
        xiazhu_money = sub_predict.xiazhu_money
        # print "lottery_number:",type(sub_predict.lottery_number)
        if lottery_number == '' and record_index < (all_record_count-1):
            #print "no lottery_num"
            pk_logger.info("no lottery_num")
            html_json = get_html_result()
            if html_json == '':
                pass
            else:
                load_lottery_predict(html_json)
                pk_logger.info("lottery_id: %d", lottery_id)
                #print "lottery_id",lottery_id
                if lottery_id == 0:
                    #print "no predict record in history"
                    pk_logger.info("no predict record in history")
                else:
                    #获取该期的开奖号码
                    lottery_num, lottery_time = get_lottery_id_number(lottery_id)
                    #print "lottery_num:",lottery_num
                    pk_logger.info("lottery_num: %s", lottery_num)
                    if (lottery_num):
                        #计算命中率并更新models
                        calculate_percisoin(lottery_id, lottery_num, kill_predict_number, lottery_time, xiazhu_money)
                    else:
                        pk_logger.info("pay interface lottery id request faild")
                        #print "pay interface lottery id request faild"

        record_index = record_index + 1

    #遍历所有当天对象
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=in_date)
    base_hour = 8
    every_hour_all_total = 0
    every_hour_target_total = 0
    every_hour_gain_all_money = 0
    every_hour_xiazhu_all_money = 0
    for sub_predict in obj_pro_predict:
        gain_all_money = gain_all_money + sub_predict.gain_money
        xiazhu_all_money = xiazhu_all_money + sub_predict.input_money

        predict_num_list_all = sub_predict.kill_predict_number.split(',')
        predict_num_list = []
        for elet in predict_num_list_all:
            tmp_list = elet.split('|')
            predict_num_list.append(tmp_list)

        lottery_num_list = sub_predict.lottery_number.split(',')
        # print "lottery_num_list:",lottery_num_list

        #最后一行不做统计
        if len(predict_num_list) == len(lottery_num_list):

            current_kill_predict_time = sub_predict.kill_predict_time
            # print "current_kill_predict_time:", current_kill_predict_time
            try:
                date_time = datetime.datetime.strptime(current_kill_predict_time,'%Y%m%d %H:%M:%S')
                # print "date_time:", date_time
                current_hour = date_time.hour
                # print "current_hour:", current_hour
            except:
                current_hour = 9
                pk_logger.info("no time")
                #print "no time"

            calc_monery_flag = 1
            for i in range(len(lottery_num_list)):
                if  '0' in predict_num_list[i]:
                    pass
                else:
                    # print " result_data[i],purchase_number_list[i]:", str(int(lottery_num_list[i])),predict_num_list[i]
                    if str(int(lottery_num_list[i])) in predict_num_list[i]:
                        target_count = target_count +  1
                    all_count = all_count + len(predict_num_list[i])
                    #设置间隔时间，1表示每小时统计一次
                    if (current_hour-base_hour) > 1:
                        if every_hour_all_total>0:
                            p = KillPredictTotal(kill_predict_date=in_date, predict_total=every_hour_all_total, target_total=every_hour_target_total,
                                                 predict_accuracy=float(float(every_hour_target_total)/float(every_hour_all_total)), predict_column_desc=int(current_hour)-1,
                                                 gain_all_money=every_hour_gain_all_money, xiazhu_all_money=every_hour_xiazhu_all_money)
                            p.save()

                        every_hour_all_total = 0
                        every_hour_target_total = 0
                        every_hour_gain_all_money = 0
                        every_hour_xiazhu_all_money = 0

                        base_hour = current_hour - 1
                        if str(int(lottery_num_list[i])) in predict_num_list[i]:
                            every_hour_target_total = every_hour_target_total + 1
                        every_hour_all_total = every_hour_all_total + len(predict_num_list[i])
                        if calc_monery_flag == 1:
                            every_hour_gain_all_money = every_hour_gain_all_money + sub_predict.gain_money
                            every_hour_xiazhu_all_money = every_hour_xiazhu_all_money + sub_predict.input_money
                            calc_monery_flag = 0
                    else:
                        if str(int(lottery_num_list[i])) in predict_num_list[i]:
                            every_hour_target_total = every_hour_target_total + 1
                        every_hour_all_total = every_hour_all_total + len(predict_num_list[i])
                        if calc_monery_flag == 1:
                            every_hour_gain_all_money = every_hour_gain_all_money + sub_predict.gain_money
                            every_hour_xiazhu_all_money = every_hour_xiazhu_all_money + sub_predict.input_money
                            calc_monery_flag = 0
    if every_hour_all_total>0:
        p = KillPredictTotal(kill_predict_date=in_date, predict_total=every_hour_all_total, target_total=every_hour_target_total,
                                                 predict_accuracy=float(float(every_hour_target_total)/float(every_hour_all_total)), predict_column_desc=int(base_hour)+1,
                                                 gain_all_money=every_hour_gain_all_money, xiazhu_all_money=every_hour_xiazhu_all_money)
        p.save()

    if all_count > 0:
        p = KillPredictTotal(kill_predict_date=in_date, predict_total=all_count, target_total=target_count, predict_accuracy=float(float(target_count)/float(all_count)), predict_column_desc='总数',
                             gain_all_money=gain_all_money, xiazhu_all_money=xiazhu_all_money )
        p.save()
    obj_pro_predict_total = KillPredictTotal.objects.all()

    return render_to_response('append_predict_list.html',{"obj_pro_predict":obj_pro_predict, "obj_pro_predict_total":obj_pro_predict_total,  "p_date":in_date})


def get_yanshi_report_max_incerease(request):
    if 1:
        #in_date= request.POST['in_date']
        in_date=request.GET.get('date')
    else:
        in_date = time.strftime('%Y%m%d',time.localtime(time.time()))
        in_date = "20180708"

    pk_logger.info("===============日期:%s",in_date.encode('utf-8'))
    KillPredictTotal.objects.all().delete()
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=in_date)
    gain_total_money = 0
    sub_gian_total_money = 0
    gain = 0
    xiazhu_money = 1
    for sub_predict in obj_pro_predict:
        #分解预测号码
        predict_num_list_all = sub_predict.predict_number_all.split(',')
        predict_num_list = []
        for elet in predict_num_list_all:
            tmp_list = elet.split('|')
            predict_num_list.append(tmp_list)
        #print "predict_num_list_all:",predict_num_list_all

        #分解中奖号码
        lottery_num_list = sub_predict.lottery_number.split(',')
        #print "lottery_num_list:",lottery_num_list

        #找百分比最大值
        percent_all_list = sub_predict.percent_all_list_desc.replace("[","").replace("]","").split(",")
        percent_float_all_list = []
        for percent in percent_all_list:
            percent_float_all_list.append(float(percent))
        #print "percent_float_all_list：",percent_float_all_list
        percent_index = percent_float_all_list.index(min(percent_float_all_list))
        #print "percent_index:",percent_index
        #最后一行不做统计
        calc_index = 0
        total = 0
        target_total = 0
        if len(predict_num_list) == len(lottery_num_list):
            for i in range(len(predict_num_list)):
                if calc_index == percent_index:
                    #print " last money:",xiazhu_money
                    #获取下注金额
                    base_xiazhu_money = xiazhu_money
                    lengths = len(set(predict_num_list[calc_index]))
                    xiazhu_money, next_xiahzu_all = get_xiazhu_money_baoben(xiazhu_money, sub_gian_total_money, gain, lengths)
                    total = total + len(set(predict_num_list[calc_index]))

                    if str(int(lottery_num_list[calc_index])) in set(predict_num_list[calc_index]):
                        target_total = target_total + 1
                    pk_logger.info("开奖号码:%s, 本期总下注:%s, 命中数:%s, 下注金额:%s",sub_predict.lottery_id,total,target_total,xiazhu_money)

                calc_index = calc_index + 1
        gain = (9.9 * target_total - total) * xiazhu_money
        gain_total_money = gain_total_money + gain
        sub_gian_total_money = sub_gian_total_money + gain
        pk_logger.info("本期盈利:%s, 追加循环盈利:%s",gain,sub_gian_total_money)
        if sub_gian_total_money > 0 or (sub_gian_total_money - next_xiahzu_all ) < -400:
            sub_gian_total_money = 0
    pk_logger.info("总盈利:%s",gain_total_money)

    return render_to_response('test.html',{"obj_pro_kill_predict":obj_pro_predict})
import math

#增长（n*(n+1))/2增长
def get_xiazhu_money(xiazhu_money, gain_money_total, last_xiazhu_money ,lengths):

    #print "--",xiazhu_money, ' ', gain_money_total, '  ', last_xiazhu_money, '  ',lengths
    if gain_money_total < -1 and gain_money_total > -400:
        #上一期命中，递增下注
        if last_xiazhu_money < 0:
            #平方增长
            #xiahu_money_result = math.pow((math.sqrt(last_xiazhu_predict.xiazhu_money) + 1),2)
            #n(n+1)/2增长
            xiahu_money_result = int(math.ceil(math.sqrt(xiazhu_money * 2)) + xiazhu_money)
        #否则保持不变
        else:
            # calc_xainzhu = math.ceil(math.fabs(gain_money_total/(10 - current_purchase_length)))
            # xiahu_money_result = min(last_xiazhu_predict.xiazhu_money,calc_xainzhu)
            #若本期不购买，则下注金额使用上一期
            calc_xainzhu = math.ceil(math.fabs(gain_money_total/(10-lengths)))
            #pk_logger.info("calc_xainzhu:%d, last_xiazhu:%d",calc_xainzhu, xiazhu_money)
            xiahu_money_result = max(min(xiazhu_money,calc_xainzhu),2)
    else:
        xiahu_money_result = 1
    return xiahu_money_result


def get_xiazhu_money_baoben(xiazhu_money, gain_money_total, last_xiazhu_money ,lengths):


    #print "--",xiazhu_money, ' ', gain_money_total, '  ', last_xiazhu_money, '  ',lengths
    if gain_money_total < -1 :
        #上一期命中，递增下注
        if last_xiazhu_money < 0:
            #平方增长
            #xiahu_money_result = math.pow((math.sqrt(last_xiazhu_predict.xiazhu_money) + 1),2)
            #n(n+1)/2增长
            xiahu_money_result = math.ceil(math.fabs(gain_money_total/(10-lengths)))
            #xiahu_money_result = int(math.ceil(math.sqrt(xiazhu_money * 2)) + xiazhu_money)
        #否则保持不变
        else:
            # calc_xainzhu = math.ceil(math.fabs(gain_money_total/(10 - current_purchase_length)))
            # xiahu_money_result = min(last_xiazhu_predict.xiazhu_money,calc_xainzhu)
            #若本期不购买，则下注金额使用上一期

            #pk_logger.info("calc_xainzhu:%d, last_xiazhu:%d",calc_xainzhu, xiazhu_money)
            xiahu_money_result = 1
    else:
         xiahu_money_result = 1

    next_xiahzu_all = xiazhu_money * lengths

    if  (gain_money_total - next_xiahzu_all) < -400:
        xiahu_money_result = 1
    return xiahu_money_result,next_xiahzu_all



#获取最新10条数据
def get_last_ten_report(request):
    current_date = GetDate().get_base_date_forward_six()
    obj_pro_predict = KillPredict.objects.filter(kill_predict_date=current_date)
    #print "obj_pro",obj_pro_predict
    return render_to_response('last_ten_report_list.html',{"obj_pro_predict":obj_pro_predict})

def get_lottery_msg(request):
    current_date = GetDate().get_base_date_forward_six()
    obj_pro_predict = PredictLottery.objects.filter(lottery_date=current_date)
    #print "obj_pro",obj_pro_predict
    return render_to_response('test.html',{"obj_pro_predict":obj_pro_predict})


def get_kill_predict_msg(request):
    current_date = GetDate().get_base_date_forward_six()
    pk_logger.info("current_date report:%s",current_date)
    obj_pro_kill_predict = KillPredict.objects.filter(kill_predict_date=current_date)
    #print "obj_pro_kill_predict",obj_pro_kill_predict
    return render_to_response('test.html',{"obj_pro_kill_predict":obj_pro_kill_predict})