from bs4 import BeautifulSoup
import requests
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

chromedriver_autoinstaller.install()
driver = webdriver.Chrome()

def get_html():    
    driver.implicitly_wait(20)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def get_property_data(soup):
    d = {}
    searchResults = soup.find_all("div", class_="l-searchResult")

    for id, result in enumerate(searchResults):
        d[id] = {}
        price = result.find("span", class_="propertyCard-priceValue")
        d[id]['price'] = price.contents[0]
        property_info = result.find(class_="property-information")
        text = property_info.find_all(class_="text")
        for n, item in enumerate(text):
            if n == 0:
                d[id]['house_type'] = item.contents[0]
            if n == 1:
                d[id]['bedrooms'] = item.contents[0]
    
        df = pd.DataFrame(d)
    
    return df.T

region_codes = {
    "Didsbury West": '5E78743',
    # "Fallowfield": '5E9701'
}

for region_code in region_codes.values():
    url = 'https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=REGION%' + region_code + '&propertyTypes=&includeLetAgreed=false&mustHave=&dontShow=&furnishTypes=&keywords='
    driver.implicitly_wait(20)
    driver.get(url)

    df = pd.DataFrame()

    soup = get_html()

    total_pages = soup.find('span', attrs={'data-bind': 'text: total'}).contents[0]

    for i in range((int(total_pages))):
        property_data = get_property_data(get_html())
        df = pd.concat([df, property_data])
        button = driver.find_element(By.CLASS_NAME, "pagination-direction--next")
        button.click()

    df = df.reset_index()
    df = df.drop(columns=['index'])

    print(df.to_string())

