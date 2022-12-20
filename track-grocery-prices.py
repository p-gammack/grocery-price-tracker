#! python3.11

import datetime
import time
import csv
import re
import requests
import mysql.connector
from bs4 import BeautifulSoup
from pathlib import Path

waitrose_butter_url = 'https://www.waitrose.com/ecom/products/essential-unsalted-dairy-butter/495389-70038-70039'
page = requests.get(waitrose_butter_url)
soup = BeautifulSoup(page.content, "html.parser")

content = soup.find(id="content")
prices = content.find("section", class_=re.compile("productPricing."))
price_per_unit = prices.find("span", attrs={'data-test': 'product-pod-price'})
price_per_kg = prices.find("span", class_=re.compile("pricePerUnit."))

price_per_unit_str = price_per_unit.text[1:]
price_per_kg_str = price_per_kg.text[2:][:-4:]

now = datetime.datetime.now()
date_str = str(now.date())

# csv_row = [date_str, price_per_unit_str, price_per_kg_str]

# data_file = "c:/Users/Patrick Gammack/scripts/track-grocery-prices/grocery-prices.csv"
# data_file_path = Path(data_file)
# data_file_exists = data_file_path.is_file()

# with open(data_file_path, 'a', encoding='UTF8', newline='') as f:
#     writer = csv.writer(f)

#     if not data_file_exists:
#         csv_header_row = ['Date', 'Price per Unit (£)', 'Price per KG (£)']
#         writer.writerow(csv_header_row)
#         print('New file created: %s' % (data_file))

#     writer.writerow(csv_row)

database = mysql.connector.connect (
    host="localhost",
    user="python",
    password="password",
    database="grocery_prices"
)

dbcursor = database.cursor()

sql = "INSERT INTO unsalted_butter (Date, Price_Per_Unit, Price_Per_KG) VALUES (%s, %s, %s)"
sql_val = (date_str, price_per_unit_str, price_per_kg_str)
dbcursor.execute(sql, sql_val)
database.commit()

print(dbcursor.rowcount, "record inserted.")
print('%s: Current price of Unsalted Butter at Waitrose is £%s £%s' % (date_str, price_per_unit_str, price_per_kg_str))
time.sleep(5)
