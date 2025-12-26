from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TIMEOUT = 10
PAGES_TO_VISIT = 1
MAIN_PAGE = 'https://www.skelbiu.lt/'

cService = webdriver.ChromeService(executable_path='./webdriver/mac-arm64/chromedriver')
driver = webdriver.Chrome(service=cService)

driver.set_window_size(1280, 720)
driver.get(MAIN_PAGE)

wait = WebDriverWait(driver, timeout=TIMEOUT)

wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler'))).click()

driver.quit()