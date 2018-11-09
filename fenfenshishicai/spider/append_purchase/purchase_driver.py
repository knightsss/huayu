#coding=utf-8
__author__ = 'shifeixiang'

# from __future__ import unicode_literals

from selenium import webdriver
import time

from log99.pk_log import PkLog

pk_logger = PkLog('append_purchase_lide.purchase_driver').log()

def get_driver(username,password):

    driver = webdriver.Firefox(executable_path = './log99/geckodriver.exe')

    driver.get("https://28c99.com/home")

    driver.maximize_window();
    time.sleep(2)

    user_elem = driver.find_element_by_xpath("/html/body/section/div[2]/div/div/div/div[2]/div/div[1]/form/div[1]/div[1]/div/input")
    user_elem.send_keys(username)

    pwd_elem = driver.find_element_by_xpath("/html/body/section/div[2]/div/div/div/div[2]/div/div[1]/form/div[1]/div[2]/div/input")
    pwd_elem.send_keys(password)

    code_flag = True
    while(code_flag):
        try:
            # elem.send_keys(Keys.RETURN)
            #密码输入完毕后提供10s时间输入验证码
            time.sleep(10)
            #提交按钮
            driver.find_element_by_xpath("/html/body/section/div[2]/div/div/div/div[2]/div/div[1]/form/div[1]/div[4]/div/div").click()
            time.sleep(3)

            pk_logger.info("login ok")
            code_flag = False
        except:
            driver.quit()

            pk_logger.warn("登录异常，重新登录")
            time.sleep(5)

            driver = webdriver.Firefox(executable_path = 'E:\\python\\webdriver\\firefox\\geckodriver.exe')
            driver.get("https://28c99.com/home")
            driver.maximize_window();
            time.sleep(2)

            user_elem = driver.find_element_by_xpath("/html/body/section/div[2]/div/div/div/div[2]/div/div[1]/form/div[1]/div[1]/div/input")
            user_elem.send_keys(username)

            pwd_elem = driver.find_element_by_xpath("/html/body/section/div[2]/div/div/div/div[2]/div/div[1]/form/div[1]/div[2]/div/input")
            pwd_elem.send_keys(password)

            code_flag = True

    time.sleep(2)
    driver.get('https://28c99.com/bettingHall/betScreen?lotId=54&pid=507')

    return driver

