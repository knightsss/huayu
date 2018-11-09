#coding=utf-8
__author__ = 'shifeixiang'


import time
from selenium import webdriver
from bs4 import BeautifulSoup
from append_purchase_tx_fenfen.models import KillPredict

from log99.pk_log import PkLog

pk_logger = PkLog('append_predict_tx_fenfen.predict_driver').log()

#获取predict driver
def spider_predict_selenium():

    chromedriver = "E:\\python\\webdriver\\chrome\\chromedriver37.exe"
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
    driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options )
    driver.get("https://www.1399p.com/pk10/shdd")
    return driver

#获取10个名次的soup 列表
def get_soup_list(driver):
    soup_list = []
    count = 0
    flag = True
    while(flag):
        try:
            driver.get("https://www.1399p.com/pk10/shdd")
            time.sleep(2)
            # print 'click select'
            # driver.find_element_by_class_name('colorWorld_selectJtou').click()
            # time.sleep(1)
            # print 'click 100'
            # driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div[1]/div/div/div/div/span[4]').click()
            # time.sleep(2)
            for i in range(10):
                driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/div/div[2]/div[2]/span[' + str(i+1) + ']/span').click()
                time.sleep(3)
                soup = BeautifulSoup(driver.page_source)
                soup_list.append(soup)
            return soup_list
        except:
            driver.quit()
            #print "spider predict faild!"
            pk_logger.error("spider predict faild!")
            time.sleep(3)
            driver = spider_predict_selenium()
            if count > 2:
                flag = False
        count = count + 1

    return []

#基于一个名次soup 获取预测号码列表 ，杀号率列表，期号
def get_kill_purchase_list(soup):
    count = 1
    percent_list = []
    number_list = []
    number_str_all_list = []
    prev_number_list = []
    hit_number = 0
    for tr in soup.find(class_='lotteryPublic_tableBlock').find_all('tr'):
        if count == 1:
            # print count,'---------------'
            p_percent = 0
            for td in tr.find_all(class_='font_red'):
                if p_percent < 10:
                    value = float(str(td.string).strip().replace("%",""))
                    percent_list.append(value)
                    # print value
                p_percent = p_percent + 1
        if count == 5:
            # print count,'---------------'
            p_number = 0
            for td in tr.find_all('td'):
                if p_number == 0:
                    protty_id = td.string
                if p_number > 1 and p_number < 12:
                    # print int(td.string)
                    value = int(td.string)
                    number_list.append(value)
                    number_str_all_list.append(str(value))
                p_number = p_number + 1
        #前一期
        if count == 6:
            # print count,'---------------'
            p_number = 0
            for td in tr.find_all('td'):
                if p_number == 0:
                    pre_protty_id = td.string
                if p_number == 1:
                    hit_number = td.string
                if p_number > 1 and p_number < 12:
                    # print int(td.string)
                    value = int(td.string)
                    # prev_number_list.append(value)
                    prev_number_list.append(str(value))
                p_number = p_number + 1
        count = count + 1
    # print "hit number, prev_number_list ", hit_number, prev_number_list
    kill_flag = False
    if hit_number in prev_number_list:
        pass
    else:
        kill_flag = True
    return protty_id,percent_list,number_list,number_str_all_list,kill_flag


#号码处理，排名前5的号码过滤，排名最小的3个提取。 并排除在前5个号码中存在的
def max_min_deal(percent_list,number_list, kill_list, purchase_list):
    #杀掉号码
    for i in range(5):
        max_percent = max(percent_list)
        index = percent_list.index(max_percent)
        percent_list.remove(max_percent)
        # print max_percent
        # print index
        number_value = number_list.pop(index)
        kill_list.append(number_value)
        # print number_value
    #预留号码
    for i  in range(3):
        min_percent = min(percent_list)
        index = percent_list.index(min_percent)
        percent_list.remove(min_percent)
        # print min_percent
        # print index
        number_value = number_list.pop(index)
        purchase_list.append(number_value)
        # print number_value
    last_number = list(set(purchase_list) - set(kill_list))
    # print last_number
    number_str = ''
    if len(last_number)>0:
        count = 0
        for number in last_number:
            if count == len(last_number)-1:
                number_str = number_str + str(number)
            else:
                number_str = number_str + str(number) + '|'
            count = count + 1
        return number_str
    else:
        return '0'

#获取需要购买的号码列表，每一名次为一个小列表
def get_purchase_list(driver):

    soup_list = get_soup_list(driver)
    purchase_number_list = ''
    purchase_number_list_desc = ''
    predict_number_all_list = []
    protty_id = 0
    count = 0
    for soup in soup_list:
        protty_id, percent_list,number_list,number_str_all_list,kill_flag = get_kill_purchase_list(soup)
        current_number_all = "|".join(number_str_all_list)
        predict_number_all_list.append(current_number_all)
        kill_list = []
        purchase_list = []
        if (kill_flag):
            # print "all kill hit"
            purchase_number = max_min_deal(percent_list, number_list, kill_list, purchase_list)
        else:
            # print "not all kill"
            purchase_number = '0'
        if count == len(soup_list) - 1:
            purchase_number_list = purchase_number_list + str(purchase_number)
            purchase_number_list_desc = purchase_number_list_desc +  '[' + str(purchase_number) + ']'
        else:
            purchase_number_list = purchase_number_list + str(purchase_number) + ','
            purchase_number_list_desc = purchase_number_list_desc + '[' + str(purchase_number) + '],'
        count = count + 1
    predict_number_all_list_str = ",".join(predict_number_all_list)

    # print "protty_id:",protty_id
    # print "purchase_number_list",purchase_number_list
    # print "purchase_number_list_desc:",purchase_number_list_desc
    return protty_id, purchase_number_list, purchase_number_list_desc, predict_number_all_list_str

def get_last_number_predict_kill_result(protty_id,index):
    last_protty_id = int(protty_id) - 1
    try:
        p = KillPredict.objects.get(lottery_id=last_protty_id)
        number_all_list = p.predict_number_all.split(',')[index]
        number_hit = str(int(p.lottery_number.split(',')[index]))
        print "number_hit,number_all_list ",number_hit,number_all_list
        if number_hit in number_all_list:
            # print "no kill all"
            return False
        else:
            # print "kill all"
            return True
    except:
        print "kill error"
        return False



if __name__ == '__main__':
    driver = spider_predict_selenium()
    get_purchase_list(driver)