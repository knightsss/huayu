#coding=utf-8
__author__ = 'shifeixiang'

# from __future__ import unicode_literals

from selenium import webdriver
import time

from log99.pk_log import PkLog

pk_logger = PkLog('append_purchase_tx_fenfen.purchase_driver').log()

def get_driver(username,password):

    # driver = webdriver.Firefox(executable_path = './log99/geckodriver.exe')
    # chromedriver = "E:\\python\\webdriver\\chrome\\chromedriver37.exe"
    chromedriver = "./log99/chromedriver37.exe"
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
    driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options )

    driver.get("https://x2.yeuss.com/#/")

    driver.maximize_window();
    time.sleep(2)

    #输入用户名
    driver.find_element_by_class_name('loginTabContent').find_element_by_tag_name('input').send_keys(username)

    code_flag = True
    while(code_flag):
        try:
            # elem.send_keys(Keys.RETURN)
            #密码输入完毕后提供10s时间输入验证码
            time.sleep(10)
            #提交按钮
            #登陆1
            driver.find_element_by_class_name('loginTabContent').find_element_by_tag_name('button').click()
            time.sleep(3)

            #输入密码
            driver.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/ui-view/form/div/div[2]/div/p[2]/input').send_keys(password)

            #登陆2
            driver.find_element_by_class_name('loginTabContent').find_element_by_tag_name('button').click()
            time.sleep(5)

            pk_logger.info("login ok")
            code_flag = False
        except:
            driver.quit()

            pk_logger.warn("登录异常，重新登录")
            time.sleep(5)

            chromedriver = "./log99/chromedriver37.exe"
            options = webdriver.ChromeOptions()
            options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
            driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options )
            driver.get("https://x2.yeuss.com/#/")
            driver.maximize_window();

            #输入用户名
            driver.find_element_by_class_name('loginTabContent').find_element_by_tag_name('input').send_keys(username)
            time.sleep(8)

            code_flag = True

    #点击关闭提示框
    driver.find_element_by_xpath('//*[@id="ngdialog1"]/div[2]/div[1]/button').click()
    time.sleep(2)

    #腾讯分分时时彩
    driver.find_element_by_xpath('/html/body/div/div[3]/div[2]/div[1]/ul/li[5]/button').click()
    time.sleep(1)

    return driver


