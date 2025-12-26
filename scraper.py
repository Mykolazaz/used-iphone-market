from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


import time

TIMEOUT = 10
PAGES_TO_VISIT = 1
MAIN_PAGE = 'https://www.skelbiu.lt/skelbimai/?keywords=iphone&autocompleted=1&search=1&distance=0&mainCity=1&category_id=480&user_type=0&ad_since_max=0&detailsSearch=0&type=1&facets=1&facets=0'

cService = webdriver.ChromeService(executable_path='./webdriver/mac-arm64/chromedriver')
driver = webdriver.Chrome(service=cService)

driver.set_window_size(1280, 720)
driver.get(MAIN_PAGE)

wait = WebDriverWait(driver, timeout=TIMEOUT)

wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler'))).click()

wait.until(EC.element_to_be_clickable((By.ID, 'showOrderTitle'))).click()

wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='orderByLinks']//span[text()='Naujausi viršuje']"))).click()

time.sleep(5)

driver.quit()