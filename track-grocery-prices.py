#! python3.11

import datetime
import time
import re
import requests
import mysql.connector
# import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path

request_headers = {'User-Agent': 'Mozilla/5.0'} # to prevent bot detection

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--incognito")
# chrome_options.add_argument("--nogpu")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--window-size=1280,1280")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--enable-javascript")
# chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
# chrome_options.add_experimental_option('useAutomationExtension', False)
# chrome_options.add_argument('--disable-blink-features=AutomationControlled')

shop = {
    "waitrose": {
        "unsalted_butter": {
            "url": 'https://www.waitrose.com/ecom/products/essential-unsalted-dairy-butter/495389-70038-70039'
        }
    },
    "tesco": {
        "unsalted_butter": {
            "url": 'https://www.tesco.com/groceries/en-GB/products/261819888'
        }
    },
    "sainsburys": {
        "unsalted_butter": {
            "url": 'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-english-butter--unsalted-250g'
        }
    },
    "aldi": {
        "unsalted_butter": {
            "url": 'https://groceries.aldi.co.uk/en-GB/p-cowbelle-british-unsalted-butter-250g/4088600190112'
        }
    },
    "asda": {
        "unsalted_butter": {
            "url": 'https://groceries.asda.com/product/block-butter/asda-unsalted-butter/910000419159'
        }
    },
    "lidl": {
        "unsalted_butter": {
            "url": 'https://www.lidl.co.uk/p/aberdoyle-dairies/aberdoyle-dairies-scottish-unsalted-butter/p16722'
        }    
    }
}

def get_waitrose_unsalted_butter_price_per_kg():
    page = requests.get(shop["waitrose"]["unsalted_butter"]["url"], headers=request_headers)
    soup = BeautifulSoup(page.content, "html.parser")

    content = soup.find(id="content")
    prices = content.find("section", class_=re.compile("productPricing."))
    price_per_kg = prices.find("span", class_=re.compile("pricePerUnit."))

    return price_per_kg.text[2:][:-4:]

def get_tesco_unsalted_butter_price_per_kg():
    page = requests.get(shop["tesco"]["unsalted_butter"]["url"], headers=request_headers)
    soup = BeautifulSoup(page.content, "html.parser")

    content = soup.find(id="content")
    price_per_kg_parent = content.find(class_="price-per-quantity-weight")
    price_per_kg = price_per_kg_parent.find("span", class_="value")

    return price_per_kg.text

def get_sainsburys_unsalted_butter_price_per_kg():
    browser = webdriver.Chrome(options=chrome_options)
    # browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    browser.get(shop["sainsburys"]["unsalted_butter"]["url"])
    time.sleep(5)
    html = browser.page_source
    browser.quit()
    soup = BeautifulSoup(html, "html.parser")

    content = soup.find(id="root")
    prices = content.find("div", class_="pd__cost")
    price_per_kg = prices.find("span", class_="pd__cost__per-unit")

    return price_per_kg.text[1:][:-5:]

def get_aldi_unsalted_butter_price_per_kg():
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(shop["aldi"]["unsalted_butter"]["url"])
    time.sleep(5)
    html = browser.page_source
    browser.quit()
    soup = BeautifulSoup(html, "html.parser")

    price_per_kg_parent = soup.find("small", class_="mr-1", property="price")
    
    return price_per_kg_parent.span.text[1:][:-7:]

def get_asda_unsalted_butter_price_per_kg():
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(shop["asda"]["unsalted_butter"]["url"])
    time.sleep(5)
    html = browser.page_source
    browser.quit()
    soup = BeautifulSoup(html, "html.parser")

    price_per_kg = soup.find("span", class_="co-product__price-per-uom")

    return price_per_kg.text[2:][:-4:]

def get_lidl_unsalted_butter_price_per_kg():
    page = requests.get(shop["lidl"]["unsalted_butter"]["url"])
    soup = BeautifulSoup(page.content, "html.parser")

    ### 2022-12-30 WARNING: Price per item and price per unit differ on webpage (assuming price per item is correct for now) ###
    # price_per_100g = soup.find(class_="pricebox__basic-quantity")
    # price_per_kg = float(price_per_100g.text.strip()[6:][:-6:]) * 0.1
    price_per_item = soup.find("span", class_="pricebox__price")
    price_per_kg = float(price_per_item.text.strip()[2:]) * 4 # std item weight = 250g

    return ("%.2f" % price_per_kg)

shop["waitrose"]["unsalted_butter"]["price_per_kg"] = get_waitrose_unsalted_butter_price_per_kg()
shop["tesco"]["unsalted_butter"]["price_per_kg"] = get_tesco_unsalted_butter_price_per_kg()
shop["sainsburys"]["unsalted_butter"]["price_per_kg"] = get_sainsburys_unsalted_butter_price_per_kg()
shop["aldi"]["unsalted_butter"]["price_per_kg"] = get_aldi_unsalted_butter_price_per_kg()
shop["asda"]["unsalted_butter"]["price_per_kg"] = get_asda_unsalted_butter_price_per_kg()
shop["lidl"]["unsalted_butter"]["price_per_kg"] = get_lidl_unsalted_butter_price_per_kg()

now = datetime.datetime.now()
date_str = str(now.date())

database = mysql.connector.connect(
    host="localhost",
    user="python",
    password="password",
    database="grocery_prices"
)

sql = "INSERT INTO unsalted_butter_price_per_kg (Date, Waitrose, Tesco, Sainsburys, Aldi, ASDA, Lidl) VALUES (%s, %s, %s, %s, %s, %s, %s)"
sql_val = (
    date_str,
    shop["waitrose"]["unsalted_butter"]["price_per_kg"],
    shop["tesco"]["unsalted_butter"]["price_per_kg"],
    shop["sainsburys"]["unsalted_butter"]["price_per_kg"],
    shop["aldi"]["unsalted_butter"]["price_per_kg"],
    shop["asda"]["unsalted_butter"]["price_per_kg"],
    shop["lidl"]["unsalted_butter"]["price_per_kg"]
    )

dbcursor = database.cursor()
dbcursor.execute(sql, sql_val)
database.commit()

print("%s: %s record inserted." % (date_str, dbcursor.rowcount))
for key in shop.keys():
    print("Unsalted Butter at %s is £%s/kg" % (key.capitalize(), shop[key]["unsalted_butter"]["price_per_kg"]))

time.sleep(5)
