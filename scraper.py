from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import regex as re
import pandas as pd

from datetime import datetime


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
                              '€':''})

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
        objSellerDate = None
        objSellerAds = None
        objLastUpdate = None

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        if len(driver.find_elements(By.CSS_SELECTOR, 'div.info-title')) == 0:

            objID = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.actions-container > div.block:nth-child(1)'))).text
            objID = re.search(r'\d{8}', objID).group()
            objID = int(objID)

            objURL = url

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

            objDescription = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.description.without-web'))).text

            objSellerDate = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.registration-date'))).text

            objSellerDate = objSellerDate.replace("Užsiregistravo ", "")

            for lt, num in lt_months.items():
                if lt in objSellerDate:
                    objSellerDate = objSellerDate.replace(lt, num)
                    break

            objSellerDate = datetime.strptime(objSellerDate, "%Y %m")

            objSellerAds = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.profile-stats'))).text
            objSellerAds = re.search(r'\d+', objSellerAds).group()

            objLastUpdate = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.actions-container > div.block:nth-child(2)'))).text


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
            allObjects.loc[rowCounter, 'last_update'] = objLastUpdate
            allObjects.loc[rowCounter, 'registration_date'] = objSellerDate
            allObjects.loc[rowCounter, 'n_listings'] = objSellerAds
            

            rowCounter += 1

        driver.back()

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    nextPage = f'https://www.skelbiu.lt/skelbimai/{page+1}{MAIN_PAGE[33:]}'
    driver.get(nextPage)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

driver.quit()

allObjects.to_csv('./objects.csv', index=False)