from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains

import time
import random
# 实例化一个启动参数对象
chrome_options = Options()
# 添加启动参数
chrome_options.add_argument('--proxy-server=127.0.0.1:8080')
# 将参数对象传入Chrome，则启动了一个设置了窗口大小的Chrome
driver = webdriver.Chrome(chrome_options=chrome_options)
# wait = WebDriverWait(driver, 20)

def get_track(distance):
    '''
    拿到移动轨迹，模仿人的滑动行为，先匀加速后匀减速
    匀变速运动基本公式：
    ①v=v0+at
    ②s=v0t+(1/2)at²
    ③v²-v0²=2as

    :param distance: 需要移动的距离
    :return: 存放每0.2秒移动的距离
    '''
    # 初速度
    v=0
    # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
    t=0.1
    # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
    tracks=[]
    # 当前的位移
    current=0
    # 到达mid值开始减速
    mid=distance * 4/5

    distance += 10  # 先滑过一点，最后再反着滑动回来

    while current < distance:
        if current < mid:
            # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
            a = 2  # 加速运动
        else:
            a = -3 # 减速运动

        # 初速度
        v0 = v
        # 0.2秒时间内的位移
        s = v0*t+0.5*a*(t**2)
        # 当前的位置
        current += s
        # 添加到轨迹列表
        tracks.append(round(s))

        # 速度已经达到v,该速度作为下次的初速度
        v= v0+a*t

    # 反着滑动到大概准确位置
    for i in range(3):
       tracks.append(-2)
    for i in range(4):
       tracks.append(-1)
    return tracks


def move_to_gap(tracks):
    # https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html
    # https://passport.zcool.com.cn/regPhone.do?appId=1006&cback=https://my.zcool.com.cn/focus/activity
    driver.get("https://passport.zcool.com.cn/regPhone.do?appId=1006&cback=https://my.zcool.com.cn/focus/activity")
    #隐私前往
    driver.find_element_by_id('details-button').click()
    driver.find_element_by_xpath('//*[@id="details"]/p[2]/a').click()
    #
    need_move_span = driver.find_element_by_xpath('//*[@id="nc_1_n1t"]/span')
    ActionChains(driver).click_and_hold(need_move_span).perform()
    for x in tracks:
        print(x)
        ActionChains(driver).move_by_offset(xoffset=x,yoffset=random.randint(1,3)).perform()
    time.sleep(1)
    ActionChains(driver).release().perform()




if __name__ == '__main__':
    move_to_gap(get_track(295))





#
# action.click(reg_btn).perform() #单击某元素

    #driver.get("https://mp.dayu.com/")
    # 设置等待超时
    #wait = WebDriverWait(driver, 20)
    #
    #
    # reg_btn = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="header-navbar-collapses"]/ul[2]/li[3]/a')))
    #
    # driver.refresh()
    # time.sleep(2)

