# from inquirer import List, prompt
import os
import json
from time import sleep
from questionary import select, Style, press_any_key_to_continue, password, text
import rich
from rich.console import Console
import sys
import random
import math

import rich.text


RENDER_CHAR_PERIOD = 0.015
RENDER_LINE_PERIOD = 0.5

TITLE_NAME = "Your New Plant Friend"
TITLE_ART = """ __     __                _   _                 _____  _             _     ______    _                _ 
 \ \   / /               | \ | |               |  __ \| |           | |   |  ____|  (_)              | |
  \ \_/ /__  _   _ _ __  |  \| | _____      __ | |__) | | __ _ _ __ | |_  | |__ _ __ _  ___ _ __   __| |
   \   / _ \| | | | '__| | . ` |/ _ \ \ /\ / / |  ___/| |/ _` | '_ \| __| |  __| '__| |/ _ \ '_ \ / _` |
    | | (_) | |_| | |    | |\  |  __/\ V  V /  | |    | | (_| | | | | |_  | |  | |  | |  __/ | | | (_| |
    |_|\___/ \__,_|_|    |_| \_|\___| \_/\_/   |_|    |_|\__,_|_| |_|\__| |_|  |_|  |_|\___|_| |_|\__,_|"""
SELECT_STYLE = Style([
            ("selected", "fg:#ff0000 bold"),
            ("pointer", "fg:#00ff00 bold"),
            ("highlighted", "fg:#ffff00"),
        ])
MARKET = {"Fertilizer": [()]}


## classes ##

class Fertilizer:
    def __init__(self, name, fertility, chaotic, cost):
        self.name = name
        self.fertility = fertility
        self.chaotic = chaotic
        self.cost = cost

    def info(self):
        return f"[Fertilizer] {self.name}\n   Fertility: {self.fertility}  chaotic: {self.chaotic}\n   cost: {self.cost}👁"

STORE_FERTILIZERS = {"Tangled green worm": Fertilizer("Tangled green worm", 2, 2, 3), 
                     "Rotten fish head": Fertilizer("Rotten fish head", 4, 5, 5)}
MONSTER_FERTILIZERS = {}


class Sedative:
    def __init__(self, name, efficacy, cost):
        self.name = name
        self.efficacy = efficacy
        self.cost = cost

    def info(self):
        return f"[Sedative] {self.name}\n   efficacy: {self.efficacy}\n   cost: {self.cost}👁"

STORE_SEDATIVE = {"Melting ice": Sedative("Melting ice", 3, 3), "Sapphire fragments": Sedative("Sapphire fragments", 6, 5)}


class Herb:
    def __init__(self, name, recover, cost):
        self.name = name
        self.recover = recover
        self.cost = cost

    def info(self):
        return f"[Herb] {self.name}\n   recover: {self.recover}\n   cost: {self.cost}👁"

STORE_POTION = {"Tuber of Titan Arum": Herb("Tuber of Titan Arum", 10, 2)}
MONSTER_POTION = {}

GOODS = {**STORE_FERTILIZERS, **STORE_SEDATIVE, **STORE_POTION}

class Save:
    def __init__(self, name):
        self.name = name
        self.height = 0
        self.chaotic = 0
        self.eyeballs = 0
        self.inventory = {}
        self.sanity = 100

    def save_info(self):
        return {'name': self.name, 'height': self.height, 'chaotic': self.chaotic, 
                "eyeballs": self.eyeballs, 'inventory': self.inventory, 'sanity': self.sanity}
    
    def get_item(self, item_name):
        if item_name not in self.inventory:
            self.inventory[item_name] = 1
        else:
            self.inventory[item_name] += 1
    
    def consume_item(self):
        if len(self.inventory)==0:
            print("Your inventory is empty right now, go shopping.")
            sleep(2)
            return
        items = []
        item_name = None
        for k,v in self.inventory.items():
            items.append(f"{v}*{GOODS[k].info()}")
        items.append("Leave")
        res = select("What to use?", choice_gen(items), qmark='🎒', style=SELECT_STYLE).ask()
        if res == len(items):
            return
        else:
            item_name = list(self.inventory.keys())[res-1]

        render_lines(f"You have consumed 1*{item_name}*")
        self.inventory[item_name] -= 1
        if self.inventory[item_name] == 0:
            self.inventory.pop(item_name)
        good = GOODS[k]
        if isinstance(good, Fertilizer):
            self.fertilize(good)
        elif isinstance(good, Sedative):
            self.comfort(good)
        elif isinstance(good, Herb):
            self.fertilize(good)


    def fertilize(self, used_fertilizer: Fertilizer):
        self.height += used_fertilizer.fertility * 0.2
        self.chaotic += used_fertilizer.fertility

    def comfort(self, used_sedative: Sedative):
        self.chaotic -= used_sedative.efficacy
        if self.chaotic < 0:
            self.chaotic = 0

    def recover_san(self, used_herb: Herb):
        self.sanity -= used_herb.recover

    def new_day(self):
        self.chaotic += 1
        self.height -= 0.1
        new_eyeball = 1 + int(self.height*random.randint(4, 8))
        self.eyeballs += new_eyeball
        lines = ["A new day!",
                 f"'The Root' is now {self.height: .1f}m, with {self.chaotic} chaotic",
                 f"You have harvested {new_eyeball}👁"]
        render_lines(lines)

    def is_over(self):
        res = True
        if self.chaotic >= 100:
            lines = ["The Root is mad.",
                     "You are wrapped by tentacles and digested, becoming the nutrient of The Root..."]
            print()
        elif self.height < 0:
            lines = ["The Root is withered.",
                     "You are dragged by the tentacles into the soil!"]
            render_lines(lines)
        elif self.sanity < 0:
            lines = ["Your mind is infected by The Root.",
                     "You are mad.",
                  "You rush to The Root and become a part of it..."]
            render_lines(lines)
        else:
            res = False
        return res

    def display_inventory(self):
        if len(self.inventory)==0:
            print("Your inventory is empty right now, go shopping.")
            sleep(2)
            return
        print("🎒 Inventory")
        for k,v in self.inventory.items():
            print(f" {v}*",GOODS[k].info(), sep='')
        press_any_key_to_continue().ask()

    def save_info(self):
        return {'name': self.name,
        'height': self.height,
        'chaotic': self.chaotic,
        'eyeballs': self.eyeballs,
        'inventory': self.inventory,
        'sanity': self.sanity}
    
    def load_info(self, save_info: dict):
        self.name = save_info['name']
        self.height = save_info['height']
        self.chaotic = save_info['chaotic']
        self.eyeballs = save_info['eyeballs']
        self.inventory = save_info['inventory']
        self.sanity = save_info['sanity']



class Necronomicon:
    def __init__(self):
        self.spells = [
            "Ph'nglui", "mglw'nafh", "Cthulhu", "R'lyeh",
            "wgah'nagl", "fhtagn", "Yog-Sothoth", "Nyarlathotep"
        ]

    def generate_spell(self):
        damage = random.randint(3,5)
        current_spell = ' '.join(random.choices(self.spells, k=damage))
        return (current_spell, damage)


## game functions ##
def load_save_json():
    with open("SAVES.json", 'r') as f:
        data = json.load(f)
        if len(data)==0:
            return None
        else:
            return data


def save_game(save: Save):
    save_info = save.save_info()
    data: dict|None = load_save_json()
    if data:
        same = None
        for s in data:
            if s == save_info['name']:
                same = s
                break
        if same:
            data.pop(same)
        data[save_info['name']] = save_info
    else:
        data = {save_info['name']: save_info}
    with open('SAVES.json', 'w') as f:
        json.dump(data, f)


def load_game():
    data = load_save_json()
    name_list = []
    for i in data:
        name_list.append(i)
    name_list.append("Leave")
    name_list = choice_gen(name_list)
    res = select("Choose a save", choices=name_list, style=SELECT_STYLE).ask()
    if res == len(name_list):
        return None
    else:
        return data[name_list[res - 1]['name']]


def get_items(current_save: Save, item: dict):
    info_msg = []
    for i in item:
        if i in current_save.inventory:
            current_save.inventory[i] += item[i]
        else:
            current_save.inventory[i] = item[i]
        info_msg.append(f"{item[i]}*{i}*")
    render_lines(f"--You get {' '.join(item)}")


def get_eyeballs(current_save: Save, num: int):
    current_save.eyeballs += num
    render_lines(f"--You get {num}👁")


## system functions ##

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def render_lines(lines: list[str]|str):
    is_wait_ends = True
    is_clear_ends = True
    if isinstance(lines, list):
        for line in lines:
            for char in line:
                sys.stdout.write(char)
                sys.stdout.flush()
                sleep(RENDER_CHAR_PERIOD)
            sleep(RENDER_LINE_PERIOD)
            print()
    else:
        is_wait_ends = False
        is_clear_ends = False
        for char in lines:
            sys.stdout.write(char)
            sys.stdout.flush()
            sleep(RENDER_CHAR_PERIOD)
        print()
    if is_wait_ends:
        press_any_key_to_continue().ask()
    if is_clear_ends:
        clear_screen()


def choice_gen(choices: list, description: list = None, disable_pos: dict = None) -> dict:
    value = list(range(1,len(choices)+1))
    available = [False for _ in range(len(choices))]
    if disable_pos:
        for k,v in disable_pos.items():
            available[k] = v
    if description:
        return [{'name': x,'value': y, 'description': z, 'disabled':d} for x, y, z, d
                in zip(choices, value, description, available)]
    else:
        return [{'name': x,'value': y, 'disabled':d} for x, y, d
                in zip(choices, value, available)]


def confirm(msg: str) -> bool:
    res = select(msg, choices=["Yes", "No"], style=SELECT_STYLE).ask()
    return True if res == "Yes" else False


## game loop and menu functions ##

def main_menu(is_first_game: bool) -> bool:
    clear_screen()
    print(TITLE_ART, "\n")
    choice_name = ["Meet new seed", "View your garden...", "Leave..."]
    descriptions = ["It fell from where no plant should grow...", "The plant is shrieking for nutrients...", "The seed will whispers endlessly in your ears..."]
    message = "A seed is calling you..."
    disable_pos = {1:"No seed have grown yet..."}
    if is_first_game:
        choices = choice_gen(choice_name, descriptions, disable_pos)
    else:
        choices = choice_gen(choice_name, descriptions)
    ans = select(message, choices, style=SELECT_STYLE, qmark='🌱').ask()
    return ans


def store_menu(save: Save):
    choices = [v.info() for v in GOODS.values()]
    choices.append("Check inventory")
    choices.append("Leave store")
    clear_screen()
    while 1:
        print(f"You have {save.eyeballs}👁")
        good_no = select("What have you set your sights on?", choice_gen(choices), qmark='🛒', style=SELECT_STYLE).ask()
        if good_no < 6:
            selected_good = list(GOODS.values())[good_no-1]
            if save.eyeballs < selected_good.cost:
                print(f"---You don't have enough eyeball for {selected_good.name}!")
                press_any_key_to_continue().ask()
                clear_screen()
                continue
            else:
                confirmation = confirm(f"Are you sure to buy {selected_good.name}?")
                if confirmation:
                    save.eyeballs -= selected_good.cost
                    save.get_item(selected_good.name)
                    print("Thanks for the eyeball!")
                    print(f"You have {save.eyeballs}👁 left.")
                    press_any_key_to_continue().ask()
                    clear_screen()
                    continue
                else:
                    print("It's good to choose wisely.")
                    sleep(1.5)
                    clear_screen()
                    continue
        if good_no == 6:
            save.display_inventory()
            clear_screen()
        else:
            print("See you tomorrow!")
            sleep(1)
            clear_screen()
            break


def fight_menu(save: Save):
    def hp_bar(hp):
        print(f"Guardian HP: {hp} {'🟥'*hp}")
        print(f"Sanity: {save.sanity}")
    
    clear_screen()
    guardian_hp = 5 + int(math.log2(save.chaotic + 2))
    spell_gen = Necronomicon()
    while save.sanity>0 and guardian_hp > 0:
        print("Type the spell and press enter to attack!")
        hp_bar(guardian_hp)
        spell, dmg = spell_gen.generate_spell()
        res = password(f"{spell}\n", qmark="📕").ask()
        if res == spell:
            print(f'{dmg} damage deal!')
            guardian_hp -= dmg
        else:
            hurt = 100 + int(math.log10(save.chaotic + 2))
            print(f"Wrong spell!\nYou loose {hurt} sanity")
            save.sanity -= hurt
        sleep(1.5)
        clear_screen()
    res = None
    if save.is_over():
        res = False
    else:
        print(f"You survived.")
        res = True
    return res


def new_game() -> Save:
    name_list = []
    with open("SAVES.json", 'r') as f:
        data = json.load(f)
        name_list = [name for name in data]

    clear_screen()
    lines = ["A searing flash tears through your eyelids and drag you out of the dream.", 
             "Through the window, you can see something shining with crystal-like indescribable brilliance striking toward your yard from the atmosphere...",
             "*BOOM!*",
             "The impact shakes the house violently making you fall off the bed.",
             "The smell of burnt permeates the room.",
             "Driven by curiosity you decide to check the yard.",
             "You walk to the crater, shocking by the weirdest scene you've never seen.",
             "Tentacles twisted and coiled together. Liquid with ruby texture is leaking and glowing from the clump.",
             "Whisper and humming of creepy melody in distorted unison surrounds you...",
             "'Grow it... Harvest it... Name it...'"]
    render_lines(lines)
    while 1:
        new_name = text("Give it a name: ").ask()
        if new_name in name_list:
            print("Name exists!")
            sleep(1)
            continue
        else:
            new_save = Save(new_name)
            break
    clear_screen()
    lines = [f"'I'm... {new_name}...'",
             "'Grow me up... Or withering with me...'",
             "A rat scurried by...",
             "Suddenly, a tentacle catches and squeezes the rat.",
             "The ruby-like liquid wraps the rat and dissolving it slowly...",
             "'Thanks for the nutrients... Here's your reward...'",
             "An eyeball dropping out of the suction cup on tentacle..",
             "'But, serve my meal when moon comes out... Otherwise, wait for them...'",
             "Those horrifying voices eventually disappeared.",
             "And the arrival of dawn has made you a little more awake."]
    render_lines(lines)
    get_eyeballs(new_save, 1)
    lines = ["You pick up the eyeballs, and those eyeballs are glitching in your hand.",
             "Suddenly, a creature climb up your leg.",
             "It is a worm with spider head and human mouth, coming out from the ground.",
             "The weirdest thing is, there's no eyeball in one of its eye sockets.",
             "As you trying to get rid of this creep, the creature start speaking.",
             "'Hey dude, did 'The Roots' just give you some eyeballs?'",
             "'I don't mean to scare you, but I really need them!'",
             "'Look, how about we make a deal?'",
             "'I have something can help you to get along peacefully with 'The Roots'.'",
             "The creature takes out some cocoons, and take some strange stuff out of them...",
             "'The fertilizer, grows 'The Roots'. But remember, it also makes 'The Roots' mad, and we all gonna crazy!'",
             "'The sedative, calms 'The Roots' down.",
             "'The recovery herb, helps you keep sane.'",
             "'If you like one of them, just insert eyeballs in my eye sockets for the exchange.'"]
    render_lines(lines)
    store_menu(new_save)
    lines = ["The sun is about to set...",
             "'Okay, I have something to remind you before the sun drops down.'",
             "'When the moon rises, you have to face the 'Guardian' from 'The Root'.'",
             "'Oh no, I have to teach you some spell to handle the 'Guardian'!'",
             "The 'Shopkeeper' takes out a book.",
             "'Here's the book of called 'Necronomicon'. When you see those 'Guardian', just read whats on the book.'",
             "'The book will show random spell in a short time, say the spell, if you can't spell right, it can cause mental damage!'",
             "'I gotta go! Before the sun is completely gone! See you!'"]
    render_lines(lines)
    lines = ["'The Root' is shaking, a tentacle suddenly attacks you.",
             "The book starts glowing and flipping its pages itself.",
             "You can see some spell."]
    render_lines(lines)
    fight_menu(new_save)
    liens = ["You've passed the first day!",
             "You can find your plant in the option 'View your garden...' in main menu."
             "Good luck and have fun!"]
    render_lines(lines)
    save_game(new_save)
    press_any_key_to_continue().ask()


def game_loop(save: Save):
    choices = ["Meet shopkeeper", "Use item", "Face the Guardian", "Save", "Check inventory", "Leave"]
    while 1:
        clear_screen()
        print("**Know your garden**")
        print(f"Height: {save.height: .1f}   Chaotic: {save.chaotic}   Sanity: {save.sanity}   👁: {save.eyeballs}")
        res = select(message="Choose an option", choices=choice_gen(choices), qmark="🌱", style=SELECT_STYLE).ask()
        match res:
            case 1:
                store_menu(save)
            case 2:
                save.consume_item()
            case 3:
                is_won = fight_menu(save)
                if not is_won:
                    press_any_key_to_continue().ask()
                    break
                clear_screen()
                save.new_day()
                if save.is_over():
                    press_any_key_to_continue().ask()
                    break
            case 4:
                save_game(save)
                print("Game saved!")
                sleep(1)
            case 5:
                save.display_inventory()
            case 6:
                print("See you.")
                sleep(1)
                break


def main():
    # main loop
    while 1:
        saves = load_save_json()
        is_first_game = saves is None
        choice = main_menu(is_first_game)
        match choice:
            case 1:
                new_game()
            case 2:
                save = load_game()
                print(save)
                if save is None:
                    continue
                else:
                    curr = Save('123')
                    curr.load_info(save)
                game_loop(curr)
            case 3:
                break





if __name__ == "__main__":
    main()