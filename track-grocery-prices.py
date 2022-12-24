#! python3.11

import datetime
import time
import re
import requests
import mysql.connector
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path

request_headers = {'User-Agent': 'Mozilla/5.0'}

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

waitrose_unsalted_butter = {
    "url": 'https://www.waitrose.com/ecom/products/essential-unsalted-dairy-butter/495389-70038-70039'
}
tesco_unsalted_butter = {
    "url": 'https://www.tesco.com/groceries/en-GB/products/261819888'
}
sainsburys_unsalted_butter = {
    "url": 'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-english-butter--unsalted-250g'
}

def get_waitrose_unsalted_butter_price_per_kg():
    page = requests.get(waitrose_unsalted_butter["url"])
    soup = BeautifulSoup(page.content, "html.parser")

    content = soup.find(id="content")
    prices = content.find("section", class_=re.compile("productPricing."))
    price_per_kg = prices.find("span", class_=re.compile("pricePerUnit."))

    return price_per_kg.text[2:][:-4:]

def get_tesco_unsalted_butter_price_per_kg():
    page = requests.get(tesco_unsalted_butter["url"], headers=request_headers)
    soup = BeautifulSoup(page.content, "html.parser")

    content = soup.find(id="content")
    price_per_kg_parent = content.find(class_="price-details--wrapper")
    price_per_kg = price_per_kg_parent.find("span", class_="value")

    return price_per_kg.text

def get_sainsburys_unsalted_butter_price_per_kg():
    browser = webdriver.Chrome(options=chrome_options)
    # browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    browser.get(sainsburys_unsalted_butter["url"])
    time.sleep(5)
    html = browser.page_source
    browser.quit()
    soup = BeautifulSoup(html, "html.parser")

    content = soup.find(id="root")
    prices = content.find("div", class_="pd__cost")
    price_per_kg = prices.find("span", class_="pd__cost__per-unit")

    return price_per_kg.text[1:][:-5:]

waitrose_unsalted_butter["price_per_kg"] = get_waitrose_unsalted_butter_price_per_kg()
tesco_unsalted_butter["price_per_kg"] = get_tesco_unsalted_butter_price_per_kg()
sainsburys_unsalted_butter["price_per_kg"] = get_sainsburys_unsalted_butter_price_per_kg()

now = datetime.datetime.now()
date_str = str(now.date())

database = mysql.connector.connect(
    host="localhost",
    user="python",
    password="password",
    database="grocery_prices"
)

sql = "INSERT INTO unsalted_butter_price_per_kg (Date, Waitrose, Sainsburys) VALUES (%s, %s, %s)"
sql_val = (
    date_str,
    waitrose_unsalted_butter["price_per_kg"],
    sainsburys_unsalted_butter["price_per_kg"]
    )

dbcursor = database.cursor()
dbcursor.execute(sql, sql_val)
database.commit()

print(dbcursor.rowcount, "record inserted.")
print("%s: Unsalted Butter at Waitrose is £%s/kg" % (date_str, waitrose_unsalted_butter["price_per_kg"]))
print("%s: Unsalted Butter at Sainsbury's is £%s/kg" % (date_str, sainsburys_unsalted_butter["price_per_kg"]))
time.sleep(5)
