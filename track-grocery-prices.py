#! python3.11

import datetime
import time
import re
import requests
import mysql.connector
from bs4 import BeautifulSoup
from pathlib import Path

waitrose_unsalted_butter = {
    "url": 'https://www.waitrose.com/ecom/products/essential-unsalted-dairy-butter/495389-70038-70039'
}
sainsburys_unsalted_butter = {
    "url": 'https://www.sainsburys.co.uk/gol-ui/product/sainsburys-english-butter--unsalted-250g'
}

def get_waitrose_unsalted_butter_price_data():
    page = requests.get(waitrose_unsalted_butter["url"])
    soup = BeautifulSoup(page.content, "html.parser")

    content = soup.find(id="content")
    prices = content.find("section", class_=re.compile("productPricing."))
    return prices

def get_waitrose_unsalted_butter_price_per_unit():
    prices = get_waitrose_unsalted_butter_price_data()
    price_per_unit = prices.find("span", attrs={'data-test': 'product-pod-price'})
    return price_per_unit.text[1:]

def get_waitrose_unsalted_butter_price_per_kg():
    prices = get_waitrose_unsalted_butter_price_data()
    price_per_kg = prices.find("span", class_=re.compile("pricePerUnit."))
    return price_per_kg.text[2:][:-4:]

waitrose_unsalted_butter["price_per_unit"] = get_waitrose_unsalted_butter_price_per_unit()
waitrose_unsalted_butter["price_per_kg"] = get_waitrose_unsalted_butter_price_per_kg()

now = datetime.datetime.now()
date_str = str(now.date())

database = mysql.connector.connect(
    host="localhost",
    user="python",
    password="password",
    database="grocery_prices"
)

dbcursor = database.cursor()

sql = "INSERT INTO unsalted_butter (Date, Price_Per_Unit, Price_Per_KG) VALUES (%s, %s, %s)"
sql_val = (date_str, waitrose_unsalted_butter["price_per_unit"], waitrose_unsalted_butter["price_per_kg"])
dbcursor.execute(sql, sql_val)
# database.commit()

print(dbcursor.rowcount, "record inserted.")
print('%s: Current price of Unsalted Butter at Waitrose is £%s £%s' %
      (date_str, waitrose_unsalted_butter["price_per_unit"], waitrose_unsalted_butter["price_per_kg"]))
time.sleep(5)
