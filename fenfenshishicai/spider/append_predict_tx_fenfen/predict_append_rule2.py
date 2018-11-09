#coding=utf-8
__author__ = 'shifeixiang'


import time
from selenium import webdriver
from bs4 import BeautifulSoup
from append_purchase_tx_fenfen.models import KillPredict

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from append_purchase_tx_fenfen.models import PredictLottery

from log99.pk_log import PkLog, GetDate
pk_logger = PkLog('append_predict_tx_fenfen.predict_append_rule_100').log()
#获取predict driver
def spider_predict_selenium():

    driver_flag = True
    while(driver_flag):
        driver = webdriver.Firefox(executable_path = './log99/geckodriver.exe')
        driver.get("http://pay4.hbcchy.com/lotterytrend/chart/16")
        driver.maximize_window();
        time.sleep(2)
        try:
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME , "chart-section")))
            driver_flag = False
            return driver
        except:
            print "get driver time out"
            driver.quit()
            time.sleep(10)



#获取10个名次的soup 列表
def get_soup_list(interval):

    count = 0
    flag = True

    while(flag):
        try:
            soup_list = []
            driver = interval["driver"]
            driver.get("https://www.1399p.com/pk10/shdd")

            try:
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME , "lotteryNumber")))
                time.sleep(1)
                #driver.maximize_window();
                # driver.manage().window().maximize();
                time.sleep(1)
                js = "var q=document.documentElement.scrollTop=300"
                driver.execute_script(js)
                #print "scroll finish!"
                pk_logger.info("scroll finish!")

                #处理100期
                #print 'click select'
                pk_logger.info("click select")
                driver.find_element_by_class_name('colorWorld_selectJtou').click()
                time.sleep(1)
                #print 'click 10'
                #driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div[1]/div/div/div/div/span[1]').click()
                #print 'click 100'
                pk_logger.info("click 100")
                driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div[1]/div/div/div/div/span[4]').click()
                time.sleep(2)
                #处理完成

                for i in range(10):
                    '/html/body/div[3]/div[2]/div/div/div[2]/div[2]/span[1]/span'
                    driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div[2]/div[2]/span[' + str(i+1) + ']/span').click()
                    time.sleep(4)
                    soup = BeautifulSoup(driver.page_source)
                    soup_list.append(soup)
                return soup_list
            except:
                pk_logger.error("get sub driver time out")
                #print "get sub driver time out"
                driver.quit()
                pk_logger.error("spider predict faild!")
                #print "spider predict faild!"
                time.sleep(3)
                interval["driver"] = spider_predict_selenium()
                if count > 2:
                    flag = False
        except:
            driver.quit()
            #print "spider predict faild!"
            pk_logger.error("spider predict faild!")
            time.sleep(3)
            interval["driver"] = spider_predict_selenium()
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

    #每个名次命中率列表
    continue_hit_list = []
    all_continue_hit_number = 0
    for tr in soup.find(class_='lotteryPublic_tableBlock').find_all('tr'):
        #百分比
        if count == 1:
            p_percent = 0
            current_percent_all = 30
            for td in tr.find_all(class_='font_red'):
                if p_percent < 10:
                    value = float(str(td.string).strip().replace("%",""))
                    percent_list.append(value)

                if p_percent == 10:
                    current_percent_all = float(str(td.string).strip().replace("%",""))
                p_percent = p_percent + 1

        #当前连中个数
        if count == 2:
            p_continue_hit = 0
            for td in tr.find_all(class_='font_blue0f'):
                #前10个为10个名次的连中个数
                if p_continue_hit < 10:
                    value = int(str(td.string))
                    #pk_logger.info("continue hit number:%d", value)
                    continue_hit_list.append(value)
                #总连续命中个数
                if p_continue_hit == 10:
                    all_continue_hit_number = int(str(td.string))
                    #pk_logger.info("all continue hit number:%d", all_continue_hit_number)
                p_continue_hit = p_continue_hit + 1

        if count == 5:
            p_number = 0
            for td in tr.find_all('td'):
                if p_number == 0:
                    protty_id = td.string
                if p_number > 1 and p_number < 12:
                    value = int(td.string)
                    number_list.append(value)
                    number_str_all_list.append(str(value))
                p_number = p_number + 1
        #前一期
        if count == 6:
            p_number = 0
            for td in tr.find_all('td'):
                if p_number == 0:
                    pre_protty_id = td.string
                if p_number == 1:
                    hit_number = td.string
                if p_number > 1 and p_number < 12:
                    value = int(td.string)
                    prev_number_list.append(str(value))
                p_number = p_number + 1
        count = count + 1

    #无论是否全部杀号正确，都计算
    #kill_flag = True
    #用于判断是否通过全中过滤
    kill_all_flag = False
    #print "number_list:",number_list
    pk_logger.info("number_list: %s" , number_list)
    #print "last hit_number is:",hit_number,'  ',prev_number_list
    #未全部杀中
    if hit_number in prev_number_list:
        kill_all_flag = False
    #全部杀中
    else:
        kill_all_flag = True
    return protty_id,percent_list,number_list,number_str_all_list,kill_all_flag,current_percent_all,all_continue_hit_number



#基于一个名次soup 获取预测杀号率列表 总杀号率  总连中个数
def get_min_current_percent_all_and_continue_hit(soup):
    count = 1
    continue_hit_list = []
    all_continue_hit_number = 0
    for tr in soup.find(class_='lotteryPublic_tableBlock').find_all('tr'):
        if count == 1:
            p_percent = 0
            for td in tr.find_all(class_='font_red'):
                if p_percent == 10:
                    current_percent_all = float(str(td.string).strip().replace("%",""))
                p_percent = p_percent + 1
            #print "current_percent_all:",current_percent_all

        #当前连中个数
        if count == 2:
            p_continue_hit = 0
            for td in tr.find_all(class_='font_blue0f'):
                #前10个为10个名次的连中个数
                if p_continue_hit < 10:
                    value = int(str(td.string))
                    #pk_logger.info("continue hit number:%d", value)
                    continue_hit_list.append(value)
                #总连续命中个数
                if p_continue_hit == 10:
                    all_continue_hit_number = int(str(td.string))
                    #pk_logger.info("all continue hit number:%d", all_continue_hit_number)
                p_continue_hit = p_continue_hit + 1
        count = count + 1

    return current_percent_all,all_continue_hit_number


#号码处理，排名前6的号码过滤，剩余的号码购买
def max_min_deal(percent_list,number_list, kill_list, purchase_list, current_percent_all):
    if current_percent_all < 50:
        last_number = list(set(number_list))
    # elif current_percent_all>= 40:
    #     #杀掉号码，取前6名作为杀号码
    #     for i in range(10):
    #         max_percent = max(percent_list)
    #         index = percent_list.index(max_percent)
    #         percent_list.remove(max_percent)
    #         number_value = number_list.pop(index)
    #         kill_list.append(number_value)
    #     #预留号码
    #     for i  in range(10):
    #         purchase_list.append(int(i+1))
    #     last_number = list(set(purchase_list) - set(kill_list))
    else:
        last_number = []

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
def get_purchase_list(interval, last_purchase_hit, xiazhu_nums):

    soup_list = get_soup_list(interval)
    purchase_number_list = ''
    purchase_number_list_desc = ''
    predict_number_all_list = []
    protty_id = 0
    count = 0
    page_count_index = 1
    purchase_mingci_number = 1

    #获取最小的总百分比
    current_percent_all_min = 50
    current_percent_all_list = []

    current_all_continue_hit_max = 0
    current_all_continue_hit_list = []
    for soup in soup_list:
        #获取总百分比，获取总连续命中
        current_percent_all,all_continue_hit_number = get_min_current_percent_all_and_continue_hit(soup)
        current_percent_all_list.append(current_percent_all)
        current_all_continue_hit_list.append(all_continue_hit_number)
        pk_logger.info("current_percent_all: %s" , current_percent_all)
        pk_logger.info("all_continue_hit_number: %s" , all_continue_hit_number)
        #排序，找出最小的命中率
        if current_percent_all_min > current_percent_all:
            current_percent_all_min = current_percent_all
        #排序，找出最大的连中次数
        if current_all_continue_hit_max < all_continue_hit_number:
            current_all_continue_hit_max = all_continue_hit_number

    current_percent_all_min = sorted(current_percent_all_list)[0]
    current_percent_all_second_min = sorted(current_percent_all_list)[1]

    pk_logger.info("current_percent_all_min: %s" , current_percent_all_min)
    pk_logger.info("current_percent_all_second_min: %s" , current_percent_all_second_min)

    #第一名与次名相差8，这使用次名作为最小值
    if current_percent_all_second_min - current_percent_all_min >= 8:
        current_percent_all_min = current_percent_all_second_min

    current_percent_all_list_str = str(current_percent_all_list)
    #print "current_percent_all_min:",current_percent_all_min
    pk_logger.info("current_percent_all_min: %s" , current_percent_all_min)
    pk_logger.info("current_all_continue_hit_max: %s" , current_all_continue_hit_max)
    #循环遍历，满足条件的提取出来
    for soup in soup_list:
        protty_id, percent_list,number_list,number_str_all_list,kill_all_flag,current_percent_all,all_continue_hit_number = get_kill_purchase_list(soup)
        current_number_all = "|".join(number_str_all_list)
        predict_number_all_list.append(current_number_all)
        kill_list = []
        purchase_list = []

        #有大于等于连续3期命中的，跳转过去
        if current_all_continue_hit_max > 3 :
            if all_continue_hit_number == current_all_continue_hit_max:
                pk_logger.info("jump to continue hit:%d",current_all_continue_hit_max)
                purchase_number = max_min_deal(percent_list, number_list, kill_list, purchase_list, current_percent_all)
                purchase_mingci_number = page_count_index
                #防止有相同的最大连中名次，多次购买。
                current_all_continue_hit_max = current_all_continue_hit_max + 1
            else:
                purchase_number = '0'
        #没有4期连中的情况
        else:
            #上期命中情况
            if (last_purchase_hit):
                #最小的购买
                if current_percent_all == current_percent_all_min:
                #最小和次小的购买
                #if current_percent_all <= current_percent_all_second_min:
                    #print "last hit"
                    pk_logger.info("last hit")
                    purchase_number = max_min_deal(percent_list, number_list, kill_list, purchase_list, current_percent_all)
                    purchase_mingci_number = page_count_index
                    #防止有相同的最小名次，多次购买。
                    current_percent_all_min = 0
                else:
                    purchase_number = '0'
            #上期未命中情况
            else:
                #使用同一未中名次
                #if xiazhu_nums == page_count_index:
                #按照排名最小的取值
                if current_percent_all == current_percent_all_min:
                #最小和次小的购买
                #if current_percent_all <= current_percent_all_second_min:
                    #print "last not hit"
                    pk_logger.info("last not hit")
                    purchase_number = max_min_deal(percent_list, number_list, kill_list, purchase_list, current_percent_all)
                    purchase_mingci_number = page_count_index
                    #防止有相同的最小名次，多次购买。
                    current_percent_all_min = 0
                else:
                    purchase_number = '0'

        if count == len(soup_list) - 1:
            purchase_number_list = purchase_number_list + str(purchase_number)
            purchase_number_list_desc = purchase_number_list_desc +  '[' + str(purchase_number) + ']'
        else:
            purchase_number_list = purchase_number_list + str(purchase_number) + ','
            purchase_number_list_desc = purchase_number_list_desc + '[' + str(purchase_number) + ']---,'
        count = count + 1
        page_count_index = page_count_index + 1
    predict_number_all_list_str = ",".join(predict_number_all_list)

    return protty_id, purchase_number_list, purchase_number_list_desc, predict_number_all_list_str, current_percent_all_list_str, purchase_mingci_number




def get_last_number_predict_kill_result(protty_id,index):
    last_protty_id = int(protty_id) - 1
    try:
        p = KillPredict.objects.get(lottery_id=last_protty_id)
        number_all_list = p.predict_number_all.split(',')[index]
        number_hit = str(int(p.lottery_number.split(',')[index]))
        #print "number_hit,number_all_list ",number_hit,number_all_list
        pk_logger.info("number_hit:%s", number_hit)
        pk_logger.info("number_all_list:%s", number_all_list)
        if number_hit in number_all_list:
            # print "no kill all"
            return False
        else:
            # print "kill all"
            return True
    except:
        #print "kill error"
        pk_logger.info("kill error")
        return False


#格式转换
def parase_lotterys(lottery):
    # print lottery
    #定义行列矩阵,179行，10列，基础数组，原始数据
    base_lottery_list = [[0 for i in range(5)] for i in range(len(lottery))]
    #定义行列矩阵,179行，10列，奇偶数组，1表示奇，0表示偶
    parity_lottery_list = [[0 for i in range(5)] for i in range(len(lottery))]
    #定义行列矩阵,179行，10列，大小数组,1表示大，0表示小
    larsma_lottery_list = [[0 for i in range(5)] for i in range(len(lottery))]
    count = 0
    #print "lottery:",lottery
    for loty in lottery:
        #print "loty.lottery_number:",loty.lottery_number
        temp_lotys = loty.lottery_number.split(',')
        # print temp_lotys
        # print count,len(lottery)
        for i in range(len(temp_lotys)):
            sub_num = int(temp_lotys[i])
            base_lottery_list[len(lottery) - count - 1][i] = sub_num
            if (sub_num%2 == 1):
                parity_lottery_list[len(lottery) -1 - count][i] = 1
            if (sub_num > 5):
                larsma_lottery_list[len(lottery) -1 - count][i] = 1
        count = count + 1
    tran_base_lottery_list = map(list, zip(*base_lottery_list))

    return base_lottery_list,parity_lottery_list,larsma_lottery_list

def get_purchase_list_99_v1():
    # current_date = time.strftime('%Y%m%d',time.localtime(time.time()))
    current_date = GetDate().get_base_date_forward_six()
    lotterys = PredictLottery.objects.filter(lottery_date=current_date)

    predict_lottery_id = current_date + str(len(lotterys) + 1).zfill(4)
    base_lottery_list,parity_lottery_list,larsma_lottery_list = parase_lotterys(lotterys)
    purchase_number_list = []
    tran_parity_lottery_list = map(list, zip(*parity_lottery_list))

    xiazhu_index_list = []
    for parity_lottery in tran_parity_lottery_list:
        xiazhu_index = 0
        #正式
        # if parity_lottery[:14] == [1,1,0,1,0,1,0,1,0,1,0,1,0,1][::-1]:
        #     xiazhu_index = 5
        #     purchase_number_list.append(1)
        # elif parity_lottery[:14] == [0,0,1,0,1,0,1,0,1,0,1,0,1,0][::-1]:
        #     xiazhu_index = 5
        #     purchase_number_list.append(0)
        #
        # elif parity_lottery[:13] == [1,1,0,1,0,1,0,1,0,1,0,1,0][::-1]:
        #     xiazhu_index = 4
        #     purchase_number_list.append(0)
        # elif parity_lottery[:13] == [0,0,1,0,1,0,1,0,1,0,1,0,1][::-1]:
        #     xiazhu_index = 4
        #     purchase_number_list.append(1)
        #
        # elif parity_lottery[:12] == [1,1,0,1,0,1,0,1,0,1,0,1][::-1]:
        #     xiazhu_index = 3
        #     purchase_number_list.append(1)
        # elif parity_lottery[:12] == [0,0,1,0,1,0,1,0,1,0,1,0][::-1]:
        #     xiazhu_index = 3
        #     purchase_number_list.append(0)
        #
        # elif parity_lottery[:11] == [1,1,0,1,0,1,0,1,0,1,0][::-1]:
        #     xiazhu_index = 2
        #     purchase_number_list.append(0)
        # elif parity_lottery[:11] == [0,0,1,0,1,0,1,0,1,0,1][::-1]:
        #     xiazhu_index = 2
        #     purchase_number_list.append(1)
        #
        # elif parity_lottery[:10] == [1,1,0,1,0,1,0,1,0,1][::-1]:
        #     xiazhu_index = 1
        #     purchase_number_list.append(1)
        # elif parity_lottery[:10] == [0,0,1,0,1,0,1,0,1,0][::-1]:
        #     xiazhu_index = 1
        #     purchase_number_list.append(0)
        #
        # elif parity_lottery[:9] == [1,1,0,1,0,1,0,1,0][::-1]:
        #     xiazhu_index = 0
        #     purchase_number_list.append(0)
        # elif parity_lottery[:9] == [0,0,1,0,1,0,1,0,1][::-1]:
        #     xiazhu_index = 0
        #     purchase_number_list.append(1)
        # else:
        #     purchase_number_list.append(-1)
        #
        # xiazhu_index_list.append(xiazhu_index)


        # 测试
        # if parity_lottery[:2] == [1,0]:
        #     purchase_number_list.append(0)
        # elif parity_lottery[:2] == [0,1]:
        #     purchase_number_list.append(1)
        # else:
        #     purchase_number_list.append(-1)


        #测试
        if parity_lottery[:8] == [1,1,0,1,0,1,0,1][::-1]:
            xiazhu_index = 5
            purchase_number_list.append(1)
        elif parity_lottery[:8] == [0,0,1,0,1,0,1,0][::-1]:
            xiazhu_index = 5
            purchase_number_list.append(0)

        elif parity_lottery[:7] == [1,1,0,1,0,1,0][::-1]:
            xiazhu_index = 4
            purchase_number_list.append(0)
        elif parity_lottery[:7] == [0,0,1,0,1,0,1][::-1]:
            xiazhu_index = 4
            purchase_number_list.append(1)

        elif parity_lottery[:6] == [1,1,0,1,0,1][::-1]:
            xiazhu_index = 3
            purchase_number_list.append(1)
        elif parity_lottery[:6] == [0,0,1,0,1,0][::-1]:
            xiazhu_index = 3
            purchase_number_list.append(0)

        elif parity_lottery[:5] == [1,1,0,1,0][::-1]:
            xiazhu_index = 2
            purchase_number_list.append(0)
        elif parity_lottery[:5] == [0,0,1,0,1][::-1]:
            xiazhu_index = 2
            purchase_number_list.append(1)

        elif parity_lottery[:4] == [1,1,0,1][::-1]:
            xiazhu_index = 1
            purchase_number_list.append(1)
        elif parity_lottery[:4] == [0,0,1,0][::-1]:
            xiazhu_index = 1
            purchase_number_list.append(0)

        elif parity_lottery[:3] == [1,1,0][::-1]:
            xiazhu_index = 0
            purchase_number_list.append(0)
        elif parity_lottery[:3] == [0,0,1][::-1]:
            xiazhu_index = 0
            purchase_number_list.append(1)
        else:
            purchase_number_list.append(-1)

        xiazhu_index_list.append(xiazhu_index)


    purchase_number_list_desc = str(purchase_number_list)
    purchase_mingci_number = 1
    print "purchase_number_list:",purchase_number_list
    return predict_lottery_id,purchase_number_list,purchase_number_list_desc,xiazhu_index_list, purchase_mingci_number



def get_purchase_list_99_v2():
    # current_date = time.strftime('%Y%m%d',time.localtime(time.time()))
    current_date = GetDate().get_base_date_forward_six()
    lotterys = PredictLottery.objects.filter(lottery_date=current_date)

    predict_lottery_id = current_date + str(len(lotterys) + 1).zfill(4)
    base_lottery_list,parity_lottery_list,larsma_lottery_list = parase_lotterys(lotterys)
    purchase_number_list = []
    tran_parity_lottery_list = map(list, zip(*parity_lottery_list))

    xiazhu_index_list = []
    for parity_lottery in tran_parity_lottery_list:
        xiazhu_index = 0
        #正式
        if parity_lottery[:18] == [1,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1][::-1]:
            xiazhu_index = 4
            purchase_number_list.append(1)
        elif parity_lottery[:18] == [0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0][::-1]:
            xiazhu_index = 4
            purchase_number_list.append(0)

        elif parity_lottery[:17] == [1,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0][::-1]:
            xiazhu_index = 3
            purchase_number_list.append(0)
        elif parity_lottery[:17] == [0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1][::-1]:
            xiazhu_index = 3
            purchase_number_list.append(1)

        elif parity_lottery[:16] == [1,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1][::-1]:
            xiazhu_index = 2
            purchase_number_list.append(1)
        elif parity_lottery[:16] == [0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0][::-1]:
            xiazhu_index = 2
            purchase_number_list.append(0)

        elif parity_lottery[:15] == [1,1,0,1,0,1,0,1,0,1,0,1,0,1,0][::-1]:
            xiazhu_index = 1
            purchase_number_list.append(0)
        elif parity_lottery[:15] == [0,0,1,0,1,0,1,0,1,0,1,0,1,0,1][::-1]:
            xiazhu_index = 1
            purchase_number_list.append(1)

        elif parity_lottery[:14] == [0,0,1,0,1,0,1,0,1,0,1,0,1,0][::-1]:
            xiazhu_index = 0
            purchase_number_list.append(0)
        elif parity_lottery[:14] == [1,1,0,1,0,1,0,1,0,1,0,1,0,1][::-1]:
            xiazhu_index = 0
            purchase_number_list.append(1)

        else:
            purchase_number_list.append(-1)

        xiazhu_index_list.append(xiazhu_index)

    purchase_number_list_desc = str(purchase_number_list)
    purchase_mingci_number = 1
    print "purchase_number_list:",purchase_number_list
    return predict_lottery_id,purchase_number_list,purchase_number_list_desc,xiazhu_index_list, purchase_mingci_number

