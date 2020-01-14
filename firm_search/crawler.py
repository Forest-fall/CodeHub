#-*- coding-8 -*-
import requests
import lxml
import sys
from bs4 import BeautifulSoup
import xlwt
import time
import urllib
import re

#反爬虫
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 


from selenium.webdriver import ActionChains
import time
import random
import numpy as np
import xlwt  
import xlrd
import xlsxwriter
from xlutils.copy import copy
import os
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import re

global is_firstfirm
is_firstfirm = True
global wrong_firm_num, right_firm_num
wrong_firm_num, right_firm_num = 0, 0

def str_no_symbol(string):
  return re.sub(r'[^\w\s]','', string)

def capture_whole_webpage(driver, firm):
    path = 'screenshot/'
    width = driver.execute_script("return document.body.scrollWidth")	 
    height = driver.execute_script("return document.body.scrollHeight")
    #resize
    driver.set_window_size(width, height)
    driver.get_screenshot_as_file(path + firm + ".png")
    

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
  t=2
  # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
  tracks=[]
  # 当前的位移
  current=0
  # 到达mid值开始减速
  mid=distance * 4/5
 
  distance += 10 # 先滑过一点，最后再反着滑动回来
 
  while current < distance:
    if current < mid:
      # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
      a = 2 # 加速运动
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

def time_format():
    current_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    return current_time

def num_or_unit(registerCapital, is_num=False):
  if registerCapital == '-':
    return "无"
  seg_list = re.split("万", registerCapital)
  if is_num:
    return seg_list[0]
  else:
    s = re.split("元", seg_list[1])
    return s[1] if s[0] == '' else seg_list[1]

def is_tabel_visible(text, firm_type="工商信息"):
  info_list = text.split('\n')
  if firm_type == "工商信息":
    return False if len(info_list) < 15 else True
  if firm_type == "上市信息":
    return False if len(info_list) < 19 else True

def extract_info(firm, row, text, firm_type="工商信息"):
  info_list = text.split('\n')
  if firm_type == "工商信息":
    info_LegalPerson = info_list[1]
    # 币种
    info_RegisterCapital = info_list[3].split(' ')[1]
    info_RegisterCapital_num = num_or_unit(info_RegisterCapital, is_num=True)
    info_RegisterCapital_unit = num_or_unit(info_RegisterCapital)
    #
    info_FirmType = info_list[8].split(' ')[1]
    info_FirmAddress = info_list[13].split(' ')[1]
    info_BusinessRange = info_list[14].split(' ')[1]
  else:
    info_LegalPerson = info_list[5].split(' ')[1]
    info_RegisterCapital_num = info_list[12].split(' ')[1]
    info_RegisterCapital_unit = info_list[11].split(' ')[-1]
    info_FirmType = info_list[3].split(' ')[1]
    info_FirmAddress = info_list[13].split(' ')[1]
    info_BusinessRange = "无"
    
  path = "save.xls"
  rb = xlrd.open_workbook(path)
  wb = copy(rb)
  sheet = wb.get_sheet(0)
  #
  # sheet.write(0, 0, "公司名称")
  # sheet.write(0, 1, "法人代表")
  # sheet.write(0, 2, "公司类型")
  # sheet.write(0, 3, "注册资本")
  # sheet.write(1, 3, "数量")
  # sheet.write(1, 4, "币种")
  # sheet.write(0, 5, "公司地址")
  # sheet.write(0, 6, "经营范围")
  #
  sheet.write(row, 0, firm)
  sheet.write(row, 1, info_LegalPerson)
  sheet.write(row, 2, info_FirmType)
  sheet.write(row, 3, info_RegisterCapital_num)
  sheet.write(row, 4, info_RegisterCapital_unit)
  sheet.write(row, 5, info_FirmAddress)
  sheet.write(row, 6, info_BusinessRange)
  os.remove(path)
  wb.save(path)  

def record_no_info_firm(firm, row, error_reason): 
  path = "wrong.xls"
  rb = xlrd.open_workbook(path)
  wb = copy(rb)
  sheet = wb.get_sheet(0)
  #
  sheet.write(0, 0, "公司名称")
  sheet.write(0, 1, "出错原因")
  #
  sheet.write(row, 0, firm)
  sheet.write(row, 1, error_reason)
  os.remove(path)
  wb.save(path) 

def Home_search(driver, firm):
  time.sleep(2)
  home_searchInput = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'searchkey')) )
  print("成功登录")
  home_searchInput.send_keys(firm) 
  home_searchButton = driver.find_element_by_xpath('//*[@class="search-area"]/form/div/span')
  home_searchButton.click()

def Head_search(driver, firm):
  # head_searchInput = driver.find_element_by_xpath('//*[@class="navi-form"]/div/div/input') # 顶部查询框输入待查询的公司名称
  # while not head_searchInput.is_displayed():
  #   head_searchInput = driver.find_element_by_xpath('//*[@class="navi-form"]/div/div/input')
  head_searchInput = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@class="navi-form"]/div/div/input')) )
  head_searchInput.clear()
  head_searchInput.send_keys(firm) 
  head_searchButton = driver.find_element_by_xpath('//*[@class="input-group-btn"]/button')
  head_searchButton.click()

def regiser(driver):
  #隐私前往
  # driver.find_element_by_id('details-button').click()
  # driver.find_element_by_xpath('//*[@id="details"]/p[2]/a').click()
  # 登录
  register_ButtonElement = driver.find_element_by_class_name('navi-btn')
  ActionChains(driver).click(register_ButtonElement).perform() 
  #切换至密码登录
  code_TabElement = driver.find_element_by_xpath('//*[@class="modal-dialog login-madal-dialog"]/div/div/div[3]/div/div[2]/a')
  while not code_TabElement.is_displayed(): # 直到密码登录tab可点击
    code_TabElement = driver.find_element_by_xpath('//*[@class="modal-dialog login-madal-dialog"]/div/div/div[3]/div/div[2]/a')
  code_TabElement.click()
  
  driver.find_element_by_id('nameNormal').send_keys("15061885272")
  driver.find_element_by_id('pwdNormal').send_keys("IhateU628")
  #模拟拖动滑块
  need_move_span = driver.find_element_by_xpath('//*[@class="modal-dialog login-madal-dialog"]/div/div/div[2]/div[2]/form/div[3]/div/div/div/span')
  ActionChains(driver).click_and_hold(need_move_span).perform() # 模拟按住鼠标左键
  tracks = get_track(295)
  for x in tracks:  # 模拟人的拖动轨迹
      # print(x)
      ActionChains(driver).move_by_offset(xoffset=x,yoffset=random.randint(1,3)).perform()
  time.sleep(1)
  ActionChains(driver).release().perform()  # 释放左键
  driver.find_element_by_xpath('//*[@class="modal-dialog login-madal-dialog"]/div/div/div[2]/div[2]/form/button').click() # 拖动完后点击登录

def back_to_home(driver):
  driver.close() # 关闭当前窗口
  n = driver.window_handles # 回到主页
  driver.switch_to.window(n[0])

def crawl(driver, firm, idx):
  global is_firstfirm
  global wrong_firm_num
  global right_firm_num
  #登录
  if is_firstfirm:
      regiser(driver)
      Home_search(driver, firm)
      is_firstfirm = False
  else:
     Head_search(driver, firm)
  print(str(idx) + ": " + firm)

  search_num = 0
  firm_table = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="search-result"]/tr[1]/td[3]/a')) )
  while not str_no_symbol(firm_table.text) == str_no_symbol(firm):
    if search_num > 3:
      print("can't find " + firm + ", 错误类型：搜索3次后仍未搜到！"+ "\n")
      record_no_info_firm(firm, wrong_firm_num, "搜索3次后仍未搜到")
      wrong_firm_num += 1
      return
    search_num += 1
    Head_search(driver, firm)
    firm_table = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="search-result"]/tr[1]/td[3]/a')) )
  firm_table.click()

  n = driver.window_handles # 获取当前页句柄
  while len(n) < 2:
    n = driver.window_handles # 获取当前页句柄
  driver.switch_to.window(n[-1]) # 切换到新的网页窗口
  # driver.get_screenshot_as_file("截图"+ str(time_format()) +".png") #用来检查当前页面状况

  '''关闭企业画报（弹窗）'''
  try:
    window = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="firstepdadModal"]/div/div/div[2]/button')) )
    window.click()
  except:
    pass
  
  '''获取工商信息'''
  try:
    Bus_info_tabel = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="Cominfo"]/table')) )  
  except:
    print("can't find " + firm + ", 错误类型：找不到工商信息" + "\n")
    #
    try:
      Sanban_info_tabel = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="sanbanBase"]/table')) )
    except:
      print("can't find " + firm + ", 错误类型：找不到上市信息" + "\n")
      record_no_info_firm(firm, wrong_firm_num + 1, "找不到上市信息")
      wrong_firm_num += 1 
    else:
      print(firm + "-----------找到上市信息" + "\n")
      while not is_tabel_visible(Sanban_info_tabel.text, "上市信息"):
        Sanban_info_tabel = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="sanbanBase"]/table')) )
      print(Sanban_info_tabel.text + "\n")
      extract_info(firm, right_firm_num + 2, Sanban_info_tabel.text, "上市信息")
      capture_whole_webpage(driver, firm) # 截图
      right_firm_num += 1 
    finally:
      back_to_home(driver)
      return
    #
  try:
      while not is_tabel_visible(Bus_info_tabel.text):
        Bus_info_tabel = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="Cominfo"]/table')) )
      print(Bus_info_tabel.text + "\n")
      extract_info(firm, right_firm_num + 2, Bus_info_tabel.text)
      capture_whole_webpage(driver, firm) # 截图
      right_firm_num += 1 
  except:
    print("提取工商信息出错")
  finally:
    back_to_home(driver)
    



 
if __name__ == "__main__":
  # options = Options()
  # chrome_options.add_argument("--headless")
  # chrome_options.add_argument("--disable-gpu")
  # chrome_options.add_argument('--hide-scrollbars') 
  # driver = webdriver.Chrome(chrome_options=chrome_options)

  ## 第一步：创建一个FirefoxProfile实例
  profile = FirefoxProfile()
  ## 第二步：开启“手动设置代理”
  profile.set_preference('network.proxy.type', 1)
  ## 第三步：设置代理IP
  profile.set_preference('network.proxy.http', '127.0.0.1')
  ## 第四步：设置代理端口，注意端口是int类型，不是字符串
  profile.set_preference('network.proxy.http_port', 8080)
  ## 第五步：设置htpps协议也使用该代理
  profile.set_preference('network.proxy.ssl', '127.0.0.1')
  profile.set_preference('network.proxy.ssl_port', 8080)

  fireFoxOptions = webdriver.FirefoxOptions()
  fireFoxOptions.set_headless()
  driver = webdriver.Firefox(profile, firefox_options=fireFoxOptions)
  # driver.maximize_window() 
  driver.implicitly_wait(5) # 单位是秒
  driver.get('https://www.qichacha.com')

  firm_list = np.load('firm_name.npy')
  for idx, firm in enumerate(firm_list[2:]): # firm_list[2:3]
    crawl(driver, firm, idx)
  driver.quit()