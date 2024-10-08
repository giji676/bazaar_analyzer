import json


def process():
    global filtering_lists
    
    filtering_lists = {
        "stars": [" ✦", "⚚ ", " ✪", "✪"],
        "mstars": ['➊', '➋', '➌', '➍', '➎'],
        "reforges": [],
        "ultimate_enchantments": {},
        "color": ["Red ", "Orange ", "Yellow ", "Lime ", "Green ", "Aqua ", "Purple ", "Pink ", "Black "],
        "gslots": [],
        "rarity_upgrade_filter": "§ka§r",
        "stripped_names": ["Helmet", "Chestplate", "Leggings", "Boots", "Sword", "Axe", "Pickaxe", "Hoe", "Showel", "Bow"]
    }

    ult_enchants_json = {
        #Removed any duplicates
        #Swords
        "Chimera V": "CH5",
        "Combo V": "CO5",
        "Fatal Tempo V": "FT5",
        "Inferno V": "IN5",
        "One For All": "OFA",
        "Soul Eater V": "SE5",
        "Swarm V": "SW5",
        "Ultimate Jerry V": "UJ5",
        "Ultimate Wise V": "UW5",
        #Bows
        "Duplex V": "DU5",
        "Rend V": "RE5",
        #Armor
        "Bank V": "BA5",
        "Habanero Tactics V": "HT5",
        "Robbin'Time V": "RT5",
        "Last Stand V": "LS5",
        "Legion V": "LE5",
        "No Pain No Gain V": "NP5",
        "Refrigerate V": "RF5",
        "Wisdom V": "WI5",
        #Tools
        "Flowstate III": "FL3",
        #Fishing Rods
        "Flash V": "FL5",
        #Wands
        #Equipment
        "The One V": "TO5",
    }

    filtering_lists = json.dumps(filtering_lists, ensure_ascii=False)
    filtering_lists = json.loads(filtering_lists)
    filtering_lists["ultimate_enchantments"] = ult_enchants_json

    with open("reforges.txt", "r") as reforge_file:
        raw_reforges = reforge_file.readlines()
        for reforge in raw_reforges:
            reforge = reforge.strip("\n")
            reforge = reforge.strip(" ")
            if reforge == "":
                continue
            if list(reforge)[0] == "#":
                continue
            filtering_lists["reforges"].append(reforge + " ")

    imported_reforges = (
        #swords
        'Gentle ',
        'Odd ',
        'Fast ',
        'Fair ',
        'Epic ',
        'Sharp ',
        'Heroic ',
        'Spicy ',
        'Legendary ',
        #meh sword stones
        'Dirty ',
        'Suspicious ',
        'Bulky ',
        #bows
        'Deadly ',
        'Fine ',
        'Grand ',
        'Hasty ',
        'Neat ',
        'Rapid ',
        'Unreal ',
        'Awkward ',
        'Rich ',
        #meh bow stones
        'Headstrong ',
        'Precise ',
        #armour
        'Clean ',
        'Fierce ',
        'Heavy ',
        'Light ',
        'Mythic ',
        'Pure ',
        'Smart ',
        'Titanic ',
        'Wise ',
        #meh armour stones
        'Perfect ',
        'Necrotic ',
        'Spiked ',
        'Cubic ',
        'Hyper ',
        'Reinforced ',
        'Ridiculous ',
        'Empowered ',
        #special things
        'Very ',
        'Highly ',
        'Extremely ',
        'Not So ',
        'Thicc ',
        'Absolutely ',
        'Even More ',
        'Strong ',
        'Shiny ',
        #others
        "Stiff ",
        "Lucky ",
        "Jerry's ",
        "Stellar ",
        "Heated ",
        "Ambered ",
        "Fruitful ",
        "Magnetic ",
        "Fleet ",
        "Mithraic ",
        "Auspicious ",
        "Refined ",
        "Moil ",
        "Blessed ",
        "Toil ",
        "Bountiful ",
        "Sweet ",
        "Silky ",
        "Bloody ",
        "Shaded ",
        "Bizarre ",
        "Itchy ",
        "Ominous ",
        "Pleasant ",
        "Pretty ",
        "Simple ",
        "Strange ",
        "Vivid ",
        "Godly ",
        "Demonic ",
        "Forceful ",
        "Hurtful ",
        "Keen ",
        "Unpleasant ",
        "Zealous ",
        "Double-Bit ",
        "Lumberjack's ",
        "Great ",
        "Rugged ",
        "Lush ",
        "Green Thumb ",
        "Peasant's ",
        "Robust ",
        "Zooming ",
        "Unyielding ",
        "Prospector's ",
        "Excellent ",
        "Sturdy ",
        "Fortunate ",
        "Strengthened ",
        "Fortified ",
        "Waxed ",
        "Glistening ",
        "Treacherous ",
        "Salty ",
        "Candied ",
        "Reforged ")

    for reforge in imported_reforges:
        reforge = reforge.strip(" ")
        reforge = reforge + " "

        if reforge not in filtering_lists["reforges"]:
            filtering_lists["reforges"].append(reforge)

process()