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

def get_waitrose_unsalted_butter_price_per_kg():
    page = requests.get(waitrose_unsalted_butter["url"])
    soup = BeautifulSoup(page.content, "html.parser")

    content = soup.find(id="content")
    prices = content.find("section", class_=re.compile("productPricing."))
    price_per_kg = prices.find("span", class_=re.compile("pricePerUnit."))

    return price_per_kg.text[2:][:-4:]

waitrose_unsalted_butter["price_per_kg"] = get_waitrose_unsalted_butter_price_per_kg()

now = datetime.datetime.now()
date_str = str(now.date())

database = mysql.connector.connect(
    host="localhost",
    user="python",
    password="password",
    database="grocery_prices"
)

sql = "INSERT INTO unsalted_butter_price_per_kg (Date, Waitrose) VALUES (%s, %s)"
sql_val = (date_str, waitrose_unsalted_butter["price_per_kg"])

dbcursor = database.cursor()
dbcursor.execute(sql, sql_val)
# database.commit()

print(dbcursor.rowcount, "record inserted.")
print('%s: Unsalted Butter at Waitrose is £%s/kg' % (date_str, waitrose_unsalted_butter["price_per_kg"]))
time.sleep(5)
