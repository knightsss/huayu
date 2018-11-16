#coding=utf-8
__author__ = 'shifeixiang'

import urllib2
import time
import simplejson
from append_purchase_tx_fenfen.models import PredictLottery
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from log99.pk_log import PkLog,GetDate
from bs4 import BeautifulSoup

pk_logger = PkLog('append_predict_tx_fenfen.spider_pk10').log()

def get_html_result(interval):
    predict_driver = interval['driver']

    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }
    #接口
    #current_date = time.strftime('%Y%m%d',time.localtime(time.time()))
    # url = "http://api.api68.com/pks/getPksHistoryList.do?date=" + current_date + "&lotCode=10001"
    flag = True
    count = 0
    while(flag):
        try:
            predict_driver.get('http://pay4.hbcchy.com/lotterytrend/chart/16')
            time.sleep(3)
            html = predict_driver.page_source
            # try:
            #     WebDriverWait(predict_driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME , "lottery-numbers")))
            #     pk_logger("start get url ok")
            #     time.sleep(1)
            #     html = predict_driver.page_source
            # except:
            #     print "not found issue-numbers"
            #     time.sleep(3)
            #     html = ''
            return html
        except:
            if count > 2:
                flag = False
            #print 'spider pay interface faild! please exit process......  over purchase!!!'
            pk_logger.error( 'spider pay interface faild! please exit process......  over purchase!!!')
            time.sleep(10)
        count = count + 1
    return ''


def load_lottery_predict(html_json):
    current_date = GetDate().get_base_date()
    #PredictLottery.objects.filter(lottery_date=current_date).delete()
    #pk_logger.info("hours is:%s",current_date)
    obj_pro_predict = PredictLottery.objects.filter(lottery_date=current_date).order_by("-lottery_id")
    if len(obj_pro_predict)>1399:
        print "delete PredictLottery all"
        PredictLottery.objects.filter(lottery_date=current_date).delete()

    lottery_id = '0'
    last_lottery_id = '0'
    for pro_predict in obj_pro_predict:
        last_lottery_id = pro_predict.lottery_id
        break
    print "last_lottery_id:",last_lottery_id
    soup = BeautifulSoup(html_json)
    index = 0
    exit_flag = False
    time.sleep(3)
    # print "soup",soup.find(id='J-chart-content')
    for resultTable in soup.find(id='J-chart-content').find_all('tr'):
        #print "resultTable",resultTable
        ids = resultTable.find(class_='issue-numbers')
        date_ids = unicode(ids.string).encode('utf-8').strip()
        lottery_date = date_ids.split('-')[0]
        lottery_id = lottery_date + date_ids.split('-')[1]
        # print "lottery_date:",lottery_date
        # print "lottery_id:",lottery_id
        # time.sleep(1)
        lottery_numbers = resultTable.find(class_='lottery-numbers')
        lottery_numbers = unicode(lottery_numbers.string).encode('utf-8').strip()
        lottery_number = ''
        for i in lottery_numbers:
            lottery_number = lottery_number + i + ','
        # lottery_numbers[0]
        lottery_number = lottery_number[:-1]
        # print "lottery_id, last_lottery_id",int(lottery_id),"  ", int(last_lottery_id)
        if int(last_lottery_id) < int(lottery_id):
            p = PredictLottery(lottery_month=lottery_date[0:6], lottery_date =lottery_date, lottery_time = lottery_id, lottery_id = lottery_id, lottery_number = lottery_number)
            p.save()
            pk_logger.info("lottery id, lottery num: %s, %s",lottery_id, lottery_number)
    return lottery_id




def get_lottery_id_number(lottery_id):
    try:
        lottery = PredictLottery.objects.get(lottery_id=lottery_id)
        return lottery.lottery_number, lottery.lottery_time
    except:
        return 0,'0'


def get_date_lottery(lottery_date):
    lotterys = PredictLottery.objects.filter(lottery_date = lottery_date)
    for lottery in lotterys:
        print lottery.lottery_id, lottery.lottery_number


if __name__ == '__main__':
    # lottery_id = 12
    # lottery_number = get_lottery_id_number(lottery_id)
    html_json = get_html_result()
    load_lottery_predict(html_json)