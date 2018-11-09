#coding=utf-8
__author__ = 'shifeixiang'

import urllib2
import time
import simplejson
from append_purchase_tx_fenfen.models import PredictLottery

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
                # page = urllib2.urlopen(url)
            time.sleep(3)
            html = predict_driver.page_source
            #html_json = simplejson.loads(html)
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
    pk_logger.info("hours is:%s",current_date)
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
    for resultTable in soup.find(id='J-chart-content').find_all('tr'):
        #print "resultTable",resultTable
        ids = resultTable.find(class_='issue-numbers')
        date_ids = unicode(ids.string).encode('utf-8').strip()
        lottery_date = date_ids.split('-')[0]
        lottery_id = date_ids.split('-')[1]
        # print "lottery_date:",lottery_date
        # print "lottery_id:",lottery_id
        lottery_numbers = resultTable.find(class_='lottery-numbers')
        lottery_numbers = unicode(lottery_numbers.string).encode('utf-8').strip()
        lottery_number = ''
        for i in lottery_numbers:
            lottery_number = lottery_number + i + ','
        # lottery_numbers[0]
        lottery_number = lottery_number[:-1]
        # print "lottery_number",lottery_number
        if int(last_lottery_id) < int(lottery_id):
            p = PredictLottery(lottery_month=lottery_date[0:6], lottery_date =lottery_date, lottery_time = lottery_id, lottery_id = lottery_id, lottery_number = lottery_number)
            p.save()

        # if index == 1:
        #     tbodys = resultTable.find_all('tbody')
        #     for tbody in tbodys:
        #         for tr in tbody.find_all('tr'):
        #             td_index = 0
        #             for td in tr.find_all('td'):
        #                 if td_index== 0:
        #                     lottery_id = unicode(td.string).encode('utf-8').strip()
        #                     #pk_logger.info("lottery_id-lottery_id:%s",lottery_id)
        #                     lottery_month = lottery_id[0:6]
        #                     lottery_date = lottery_id[0:8]
        #                 if td_index == 1:
        #                     lottery_numbers = ''
        #                     base_number = ['0','1','2','3','4','5','6','7','8','9']
        #                     for span in td.find_all('span'):
        #                         lottery_number = unicode(span.string).encode('utf-8').strip()
        #                         #print "lottery_number....:",lottery_number
        #                         if lottery_number in base_number:
        #                             lottery_numbers = lottery_numbers + lottery_number + ','
        #                         else:
        #                             exit_flag = True
        #                             break
        #                     lottery_numbers = lottery_numbers[:-1]
        #                     #pk_logger.info("lottery_numbers....:%s",lottery_numbers)
        #                     if lottery_numbers == '':
        #                         #print "pass....."
        #                         pass
        #                     else:
        #                         #pk_logger.info("lottery_id-lottery_id222:%s",lottery_id)
        #                         if int(last_lottery_id) < int(lottery_id):
        #                             #time.sleep(1)
        #                             p = PredictLottery(lottery_month=lottery_month, lottery_date =lottery_date, lottery_time = lottery_id, lottery_id = lottery_id, lottery_number = lottery_numbers)
        #                             p.save()
        #                 td_index = td_index + 1
        #             if(exit_flag):
        #                 break
        #         if(exit_flag):
        #             break
        #     if(exit_flag):
        #         break
        # index = index + 1
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