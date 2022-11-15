import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

options = Options()
options.add_argument("--headless")
options.add_argument("window-size=1400,1500")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

region_codes_json = open('manchester.json')
region_codes = json.load(region_codes_json)
region_codes_json.close()

def get_property_data():
    d = {}
    selenium_search_results = driver.find_elements(By.CLASS_NAME, "l-searchResult")
    for id, result in enumerate(selenium_search_results):
        d[id] = {}
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "propertyCard-priceValue"))
        )
        driver.implicitly_wait(10)
        price = result.find_element(By.CLASS_NAME, "propertyCard-priceValue").text
        price = price.strip('£') 
        price = price.strip(' pcm')
        price = price.replace(',', '')
        d[id]['price'] = int(price)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "property-information"))
        )
        property_info = result.find_element(By.CLASS_NAME, "property-information")
        items = property_info.find_elements(By.CLASS_NAME, "text")
        for n, item in enumerate(items): 
            if n == 0:
                d[id]['house_type'] = item.text
            if n == 1:
                d[id]['bedrooms'] = int(item.text)
            if n == 2:
                d[id]['bathrooms'] = int(item.text)
    
        df = pd.DataFrame(d)
    
    return df.T

# region_codes = {
    # "West_Didsbury": "5E78743",
    # "Gorton": "5E11006",
    # "Blackley": "5E66106"
# }

for region, region_code in region_codes.items():
    df = pd.DataFrame()
    url = 'https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=REGION%' + region_code + '&propertyTypes=&includeLetAgreed=false&mustHave=&dontShow=&furnishTypes=&keywords='
    driver.get(url)
    total_pages_wrapper = driver.find_element(By.CLASS_NAME, "pagination-pageSelect")
    total_pages = total_pages_wrapper.find_element(By.XPATH,  ".//span[@data-bind='text: total']").text
    for i in range(int(total_pages)):
        property_data = get_property_data()
        df = pd.concat([df, property_data])
        button = driver.find_element(By.CLASS_NAME, "pagination-direction--next")
        button.click()
    df = df.reset_index()
    df = df.drop(columns=['index'])

    print(df.to_string())
