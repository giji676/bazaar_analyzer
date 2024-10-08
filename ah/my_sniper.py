from concurrent.futures import ThreadPoolExecutor
from reforge_processor import filtering_lists
from re import sub
import requests
import asyncio
import time
import json


 # 300/5 = 60

MAX_REQ_SEC = 60/1 # MAX = 60/60


MIN_PROFIT_PERCENTAGE = 50 # 50%
MIN_PRIFIT_AMOUNT = 1_000_000
MIN_PRIFIT_IF_MIN_PROFIT_PERCENTAGE = 1_000_000
MIN_BUY_AMOUNT = 1
MAX_COST = 15_000_000

auction_file = open("page0.json", "r")
auctions = json.load(auction_file)
auction_file.close()

BASE_URL = "https://api.hypixel.net/skyblock/auctions?page="

prices = {}
results = []


def pricedump():
    with open("my_prices.txt", "w", encoding="utf-8") as file:
        file.truncate(0)
        file.write(str(prices))


def analyse_item(item):
    if item["claimed"]:
        return
    if not item['bin']:
        return
    if "Furniture" in item["item_lore"]:
        return
    if "consumables" == item['category']:
        return
    if "New Year Cake" in item["item_name"]:
        return
    if "Rune" in item["item_name"]:
        return
    
    item_name = str(item["item_name"])
    item_lore = str(item["item_lore"]) # Description, including stats, enchants and everything else
    
    # Remove all the reforges
    for reforge in filtering_lists["reforges"]:
        item_name = item_name.replace(reforge, "")

    # After reforges have been removed, some items are left with only these name
    # In that case it becomes useless
    for stripped_name in filtering_lists["stripped_names"]:
        if stripped_name == item_name:
            return
    clean_name = item_name
    for star in filtering_lists["stars"]:
        clean_name = clean_name.replace(star, "")
    for mstar in filtering_lists["mstars"]:
        clean_name = clean_name.replace(mstar, "")
    # Remove all the starts, except if there is 5
    # 5 is max stars, and sells for a lot more than 0 stars
    # So it gets treated as a separate item
    if "✪" in item_name and item_name.count("✪") != 5:
        item_name = item_name.replace(" ✪", "")
        item_name = item_name.replace("✪", "")
    clean_name = clean_name.replace(" ", "")

    # Check if the item is recombobulated
    if filtering_lists["rarity_upgrade_filter"] in item_lore:
        item_name = str("".join([item_name, "(re)"]))
    
    item_tier = item["tier"]
    clean_name = "".join([clean_name, item_tier])

    # If it is a pet, clacfy it in a certain level group
    if "Right-click to add this pet to" in item["item_lore"]:
        item_name = sub(r"[\[\]]", "", item_name)
        pet_w_level = item_name.split(" ")
        pet_level = int(pet_w_level[1])
        if pet_level != 100:
            if pet_level > 95:
                pet_level = "lvl>95"
            elif pet_level > 90:
                pet_level = "lvl>90"
            elif pet_level > 75:
                pet_level = "lvl>75"
            else:
                pet_level = "lvl>0"
        else:
            pet_level = "lvl100"
        pet_name = pet_w_level[2:]
        item_name = "".join(pet_name)
        item_name = "".join([pet_level, item_name, item_tier])
        clean_name = item_name
    else:
        item_name = sub(r"\[[^\]]*\]", "", " ".join([item_name, item_tier]))
        
    item_name = item_name.replace(" ", "")
    if item_name == clean_name:
        clean_name = ""

    # If it is already in prices and there is a cheaper price return
    starting_bid = item["starting_bid"]
    if item_name in prices:
        if prices[item_name][1] < starting_bid:
            return
    
    # If it is already in prices, check if any of the prices are cheaper
    # If so add it to prices, and arrange to have cheaper one at 0th index
    # If it's not in prices, add it and add higher price as infinity, for later comparison
    if item_name in prices:
        if prices[item_name][0] > starting_bid:
            prices[item_name][1] = prices[item_name][0]
            prices[item_name][0] = starting_bid
        elif prices[item_name][1] > starting_bid:
            prices[item_name][1] = starting_bid
    else:
        prices[item_name] = [starting_bid, float("inf")]
    
    # Do the same for clean name
    if clean_name != "":
        if clean_name in prices:
            if prices[clean_name][0] > starting_bid:
                prices[clean_name][1] = prices[clean_name][0]
                prices[clean_name][0] = starting_bid
            elif prices[clean_name][1] > starting_bid:
                prices[clean_name][1] = starting_bid
        else:
            prices[clean_name] = [starting_bid, float("inf")]

    profit_percentage = prices[item_name][1] / prices[item_name][0] * 100 - 100
    profit_amount = prices[item_name][1] - prices[item_name][0]

    if prices[item_name][1] == float("inf"):
        return
    # If all the margin requirements are met
    # Add the necessary data to results list
    if (profit_percentage >= MIN_PROFIT_PERCENTAGE and profit_amount >= MIN_PRIFIT_IF_MIN_PROFIT_PERCENTAGE
        ) or (profit_amount >= MIN_PRIFIT_AMOUNT
        ) and prices[item_name][0] < MAX_COST:
        print_name = item["item_name"]
        if filtering_lists["rarity_upgrade_filter"] in item_lore:
            print_name = "".join([print_name, "(re)"])
        print_name = " ".join([print_name, item_tier])
        if clean_name:
            results.append([item["uuid"], print_name, item["starting_bid"], item_name, clean_name])
        else:
            results.append([item["uuid"], print_name, item["starting_bid"], item_name])


def fetch(url):
    # print("GET", url)
    r = requests.get(url)
    return r.json()


# Obsolute - keeping it around just in case
def get_raw_page_data(page):
    return fetch(BASE_URL + str(page))


def get_auction_from_page(session, page):
    with session.get(BASE_URL+str(page)) as response:
        data = response.json()
        if data["success"]:
            for auction in data["auctions"]:
                analyse_item(auction)

# Obsolute - keeping it around just in case
def get_auc_data(total_pages):
    auctions = []
    for i in range(int(total_pages)):
    # for i in range(5):
        auctions.extend(get_raw_page_data(i)["auctions"])
    for auction in auctions:
        analyse_item(auction)


def get_total_pages():
    data = fetch(BASE_URL+"0")
    total_pages = data["totalPages"]
    return total_pages


async def get_data_asynchronous(total_pages):
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            tasks = []
            loop = asyncio.get_event_loop()
            for page in range(total_pages):
                task = loop.run_in_executor(executor, get_auction_from_page, *(session, page))
                tasks.append(task)
            for response in await asyncio.gather(*tasks):
                # print(response)
                pass


# Save raw data as json, analyze each page in separate thread?, request each page as separate thread
def main():
    global results, prices
    results = []
    prices = {}

    total_pages = get_total_pages()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_data_asynchronous(total_pages))
    loop.run_until_complete(future)

    pricedump()

    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print(current_time + ' prices cached')
    # get_auc_data(total_pages)

    if len(results):
        for result_index in range(len(results)):
            result = results[result_index]
            # Nealy the same margin calculation and validation as in analyze_item()
            profit_percentage = prices[result[3]][1] / prices[result[3]][0] * 100 - 100
            profit_amount = prices[result[3]][1] - prices[result[3]][0]
            
            if (prices[result[3]][1] != float("inf")
                ) and (prices[result[3]][0] == result[2]
                ) and ((profit_percentage >= MIN_PROFIT_PERCENTAGE and profit_amount >= MIN_PRIFIT_IF_MIN_PROFIT_PERCENTAGE
                ) or (profit_amount >= MIN_PRIFIT_AMOUNT
                ) and prices[result[3]][0] < MAX_COST):
                # If len == 4 -- it does not include the clean_item data
                if len(result) == 4:
                    results[result_index] = results[result_index] + [prices[result[3]][1]]
                else:
                    results[result_index] = results[result_index] + [prices[result[3]][1]]
                    results[result_index] = results[result_index] + [prices[result[4]][0]]
            else:
                results[result_index] = ""
    while "" in results:
        results.remove("")
        
    if len(results):
        for result in results:
            if result != "":
                # If len == 7 -- it includes the clean_item data
                if len(result) == 7:
                    toprint = "/viewauction " + str(result[0]) + " | Item: `" + str(result[1]) + "` | Price: `{:,}`".format(result[2]) + " | Second LBIN: `{:,}`".format(result[5]) + " | Clean LBIN `{:,}`".format(result[6])
                else:
                    toprint = "/viewauction " + str(result[0]) + " | Item: `" + str(result[1]) + "` | Price: `{:,}`".format(result[2]) + " | Second LBIN: `{:,}`".format(result[4])
                print(toprint)


while True:
    main()
    time.sleep(MAX_REQ_SEC)
