from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

import requests

import regex as re
import pandas as pd

from datetime import datetime

import time


TIMEOUT = 10

MAIN_PAGE = 'https://www.skelbiu.lt/skelbimai/?keywords=iphone&autocompleted=1&search=1&distance=0&mainCity=1&category_id=480&user_type=0&ad_since_max=0&detailsSearch=0&type=1&facets=1&facets=0'

cService = webdriver.ChromeService(executable_path='./webdriver/linux/chromedriver')
driver = webdriver.Chrome(service=cService)

driver.set_window_size(1920, 1080)
driver.get(MAIN_PAGE)

wait = WebDriverWait(driver, timeout=TIMEOUT)

wait.until(EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler'))).click()

wait.until(EC.element_to_be_clickable((By.ID, 'showOrderTitle'))).click()

wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='orderByLinks']//span[text()='Naujausi viršuje']"))).click()

lt_months = {
    "sausį": "01",
    "vasarį": "02",
    "kovą": "03",
    "balandį": "04",
    "gegužę": "05",
    "birželį": "06",
    "liepą": "07",
    "rugpjūtį": "08",
    "rugsėjį": "09",
    "spalį": "10",
    "lapkritį": "11",
    "gruodį": "12",
}

LISTINGS_TO_VISIT = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'li.change-and-submit.active > span'))).text

replacements = str.maketrans({'(':'',
                              ')':'',
                              ' ':'',
                              '€':'',
                              ',':'.'})

LISTINGS_TO_VISIT = LISTINGS_TO_VISIT.translate(replacements)

LISTINGS_TO_VISIT = int(LISTINGS_TO_VISIT)

PAGES_TO_VISIT = LISTINGS_TO_VISIT // 24

columns = ['id',
           'url',
            'name',
            'price',
            'maker',
            'model',
            'condition',
            'city',
            'views',
            'likes',
            'description',
            'sold',
            'sale_time',
            'last_update',
            'registration_date',
            'n_listings']

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

    for url in pageListingLinks:
        driver.get(url)

        objID = None
        objURL = None
        objName = None
        objPrice = None
        objMaker = None
        objModel = None
        objCondition = None
        objCity = None
        objViews = None
        objLikes = None
        objDescription = None
        objSold = False
        objSaleTime = None
        objSellerDate = None
        objSellerAds = None
        objSellerVerified = None
        objLastUpdate = None

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        itemAvailable = True if len(driver.find_elements(By.CSS_SELECTOR, 'div.info-title')) == 0 else False

        objID = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.actions-container > div.block:nth-child(1)'))).text
        objID = re.search(r'\d{8}', objID).group()
        objID = int(objID)

        objURL = url

        objName = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.left-block > h1'))).text
        
        if len(driver.find_elements(By.CSS_SELECTOR, 'div.right-block > p')) != 0:
            
            objPrice = driver.find_element(By.CSS_SELECTOR, 'div.right-block > p').text
            objPrice = objPrice.translate(replacements)
            objPrice = float(objPrice)

        objMaker = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.details-row:nth-child(1) > span'))).text

        objModel = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.details-row:nth-child(2) > span'))).text

        if len(driver.find_elements(By.CSS_SELECTOR, 'div.details-row:nth-child(3) > span')) != 0:
            objCondition = driver.find_element(By.CSS_SELECTOR, 'div.details-row:nth-child(3) > span').text

        if itemAvailable:
            objCity = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.main-city'))).text

        objViews = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.block.showed > span'))).text
        objViews = objViews.replace('K', '000')
        objViews = int(objViews)

        objLikes = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span#ad-bookmarks-count'))).text
        objLikes = int(objLikes)


        if len(driver.find_elements(By.CSS_SELECTOR, 'div.description.without-web')) != 0:
            objDescription = driver.find_element(By.CSS_SELECTOR, 'div.description.without-web').text


        if not itemAvailable:
            objSold = True

            objSaleTime = driver.find_element(By.CSS_SELECTOR, 'div.disabled-info-container > div.info-description').text

        if itemAvailable:

            objSellerDate = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.registration-date'))).text

            objSellerDate = objSellerDate.replace("Užsiregistravo ", "")

            for lt, num in lt_months.items():
                if lt in objSellerDate:
                    objSellerDate = objSellerDate.replace(lt, num)
                    break

            objSellerDate = datetime.strptime(objSellerDate, "%Y %m")

            if len(driver.find_elements(By.CSS_SELECTOR, 'div.profile-stats')) != 0:
                objSellerAds = driver.find_element(By.CSS_SELECTOR, 'div.profile-stats').text
                objSellerAds = re.search(r'\d+', objSellerAds).group()

            objSellerVerified = True if len(driver.find_elements(By.CSS_SELECTOR, 'div.user-verified > span.tooltip')) != 0 else False

        objLastUpdate = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.actions-container > div.block:nth-child(2)'))).text

        if itemAvailable:
            if len(driver.find_elements(By.CSS_SELECTOR, 'div.main-photo > img.no-photo')) == 0:

                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.main-photo.js-open-photo'))).click()

                time.sleep(0.5)

                image_urls = []

                for _ in range(3):
                    try:
                        images = driver.find_elements(By.CSS_SELECTOR, 'img.pswp__img')
                        image_urls = [img.get_attribute('src') for img in images]
                        break
                    
                    except StaleElementReferenceException:
                        time.sleep(1)
                        continue

                next_button = driver.find_element(By.CSS_SELECTOR, 'button.pswp__button.pswp__button--arrow--right')

                for index, img_url in enumerate(image_urls):
                    response = requests.get(img_url, stream=True)

                    try:
                        next_button.click()
                    except:
                        None

                    with open(f'./images/{objID}-{index}.png', 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

        allObjects.loc[rowCounter] = None

        allObjects.loc[rowCounter, 'id'] = objID
        allObjects.loc[rowCounter, 'url'] = objURL
        allObjects.loc[rowCounter, 'name'] = objName
        allObjects.loc[rowCounter, 'price'] = objPrice
        allObjects.loc[rowCounter, 'maker'] = objMaker
        allObjects.loc[rowCounter, 'model'] = objModel
        allObjects.loc[rowCounter, 'condition'] = objCondition
        allObjects.loc[rowCounter, 'city'] = objCity
        allObjects.loc[rowCounter, 'views'] = objViews
        allObjects.loc[rowCounter, 'likes'] = objLikes
        allObjects.loc[rowCounter, 'description'] = objDescription
        allObjects.loc[rowCounter, 'sold'] = objSold
        allObjects.loc[rowCounter, 'sale_time'] = objSaleTime
        allObjects.loc[rowCounter, 'last_update'] = objLastUpdate
        allObjects.loc[rowCounter, 'registration_date'] = objSellerDate
        allObjects.loc[rowCounter, 'seller_verified'] = objSellerVerified
        allObjects.loc[rowCounter, 'n_listings'] = objSellerAds
        
        rowCounter += 1

        driver.back()

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    nextPage = f'https://www.skelbiu.lt/skelbimai/{page+1}{MAIN_PAGE[33:]}'
    driver.get(nextPage)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    print(f'Current page number: {page}')

driver.quit()

allObjects.to_csv('./objects.csv', index=False)