import requests
import json
from pprint import pprint
import os

BAZAAR_AFTER_TAX = 0.99
MIN_PROFIT_PERCENTAGE = 10 # 10%
MIN_PRIFIT_AMOUNT = 100_000
MIN_PRIFIT_IF_MIN_PROFIT_PERCENTAGE = 2_500
MIN_BUY_AMOUNT = 2_500
MIN_SELL_MOVING_WEEK = 15000
MIN_BUY_MOVING_WEEK = 15000

# Used to make any GET request
def make_request(call):
    print("GET", call)
    r = requests.get(call)
    return r.json()

def get_product_profits(item_data):
    try:
        sell = item_data.get("buy_summary")[0]["pricePerUnit"] # buy_summary is the instant buy, which is sell order, we are interested in the sell order aspect
        buy = item_data.get("sell_summary")[0]["pricePerUnit"] # ^^^ same with sell_summary
        sell_moving_week = item_data.get("quick_status")["sellMovingWeek"]
        buy_moving_week = item_data.get("quick_status")["buyMovingWeek"]
        sell_after_tax = sell * BAZAAR_AFTER_TAX
        profit_percentage = sell_after_tax / buy * 100 - 100
        profit_amount = sell_after_tax - buy
        return profit_percentage, profit_amount, buy, sell_moving_week, buy_moving_week
    except:
        return 0, 0, 0, 0, 0

def process_product(item_name, item_data):
    profit_percentage, profit_amount, buy, sell_moving_week, buy_moving_week = get_product_profits(item_data)

    if profit_amount > MIN_PRIFIT_AMOUNT or (profit_percentage > MIN_PROFIT_PERCENTAGE and profit_amount > MIN_PRIFIT_IF_MIN_PROFIT_PERCENTAGE):
        if buy > MIN_BUY_AMOUNT:
            if sell_moving_week > MIN_SELL_MOVING_WEEK and buy_moving_week > MIN_BUY_MOVING_WEEK:
                return item_data
    else:
        return None
    

def get_bazaar_product_names(bazaar_data):
    profitable_products = []
    for item_name, item_data in bazaar_data.get("products", {}).items():
        processed = process_product(item_name, item_data)
        if processed != None:
            profitable_products.append(processed)
    return profitable_products

API_FILE = open(r"bazaar_analyzer\API_KEY.json", "r")
API_KEY = json.loads(API_FILE.read())["API_KEY"]
example_player_uuid = "c3bbf8229941477d9aeaa2d245882bcc"

# For testing purposes bazaar data is store in a json file and loads it if it exists to prevent making unnecessary requests
testing = False
if testing:
    print("Testing:", testing)
    if os.path.isfile("bazaar_data.json"):
        with open("bazaar_data.json", "r") as file:
            bazaar_data = json.load(file)
    else:
        bazaar_data = make_request("https://api.hypixel.net/skyblock/bazaar")
        with open("bazaar_data.json", "w") as file:
            json.dump(bazaar_data, file)
else:
    print("Testing:", testing)
    bazaar_data = make_request("https://api.hypixel.net/skyblock/bazaar")
print()
profitable_products = get_bazaar_product_names(bazaar_data)
for item in profitable_products:
    print(item.get("product_id"))
    profit_percentage, profit_amount, buy, sell_moving_week, buy_moving_week = get_product_profits(item)
    print("profit percentage: ", round(profit_percentage, 5))
    print("profit amount: ", round(profit_amount, 2))
    #print("current top insta buy: ", item.get("buy_summary")[0])
    #print("current top insta sell: ", item.get("sell_summary")[0])
    print()

print("TOTAL: ", len(profitable_products))

with open("prifitables.json", "w") as file:
            json.dump(profitable_products, file)