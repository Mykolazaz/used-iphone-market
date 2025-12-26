from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import regex as re
import pandas as pd


TIMEOUT = 10
MAIN_PAGE = 'https://www.skelbiu.lt/skelbimai/?keywords=iphone&autocompleted=1&search=1&distance=0&mainCity=1&category_id=480&user_type=0&ad_since_max=0&detailsSearch=0&type=1&facets=1&facets=0'

cService = webdriver.ChromeService(executable_path='./webdriver/mac-arm64/chromedriver')
driver = webdriver.Chrome(service=cService)

driver.set_window_size(1280, 720)
driver.get(MAIN_PAGE)

wait = WebDriverWait(driver, timeout=TIMEOUT)

wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler'))).click()

wait.until(EC.element_to_be_clickable((By.ID, 'showOrderTitle'))).click()

wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='orderByLinks']//span[text()='Naujausi viršuje']"))).click()

LISTINGS_TO_VISIT = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'li.change-and-submit.active > span'))).text

replacements = str.maketrans({'(':'',
                              ')':'',
                              ' ':'',
                              '€':''})

LISTINGS_TO_VISIT = LISTINGS_TO_VISIT.translate(replacements)

LISTINGS_TO_VISIT = int(LISTINGS_TO_VISIT)

PAGES_TO_VISIT = LISTINGS_TO_VISIT // 24

columns = ['id',
            'name',
            'price',
            'maker',
            'model',
            'condition',
            'city',
            'views',
            'likes',
            'description']

allObjects = pd.DataFrame(columns=columns)

rowCounter = 0

for page in range(1, PAGES_TO_VISIT + 1):
    
    pageListingLinks = []

    pageListings = driver.find_elements(
        By.CSS_SELECTOR,
        'a.js-cfuser-link.standard-list-item'
    )

    for a in pageListings:
        href = a.get_attribute("href")
        if href not in pageListingLinks:
            pageListingLinks.append(href)

    pageListingLinks = list(filter(lambda x : re.search(r'^https://www\.skelbiu\.lt/', x), pageListingLinks))

    for i, url in enumerate(pageListingLinks):
        driver.get(url)

        objID = None
        objName = None
        objPrice = None
        objMaker = None
        objModel = None
        objCondition = None
        objCity = None
        objViews = None
        objLikes = None
        objDescription = None

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        if len(driver.find_elements(By.CSS_SELECTOR, 'div.info-title')) == 0:

            objID = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.image-item-id'))).text
            objID = objID.replace('ID: ', '')
            objID = int(objID)

            objName = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.left-block > h1'))).text
            
            objPrice = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.right-block > p'))).text
            objPrice = objPrice.translate(replacements)
            objPrice = int(objPrice)

            objMaker = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.details-row:nth-child(1) > span'))).text

            objModel = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.details-row:nth-child(2) > span'))).text

            objCondition = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.details-row:nth-child(3) > span'))).text

            objCity = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.main-city'))).text

            objViews = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.block.showed > span'))).text
            objViews = objViews.replace('K', '000')
            objViews = int(objViews)

            objLikes = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span#ad-bookmarks-count'))).text
            objLikes = int(objLikes)

            allObjects.loc[rowCounter] = None

            allObjects.loc[rowCounter, 'id'] = objID
            allObjects.loc[rowCounter, 'name'] = objName
            allObjects.loc[rowCounter, 'price'] = objPrice
            allObjects.loc[rowCounter, 'maker'] = objMaker
            allObjects.loc[rowCounter, 'model'] = objModel
            allObjects.loc[rowCounter, 'condition'] = objCondition
            allObjects.loc[rowCounter, 'city'] = objCity
            allObjects.loc[rowCounter, 'views'] = objViews
            allObjects.loc[rowCounter, 'likes'] = objLikes
            allObjects.loc[rowCounter, 'description'] = objDescription
            rowCounter += 1

        driver.back()

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    nextPage = f'https://www.skelbiu.lt/skelbimai/{page+1}{MAIN_PAGE[33:]}'
    driver.get(nextPage)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

driver.quit()

allObjects.to_csv('./objects.csv', index=False)