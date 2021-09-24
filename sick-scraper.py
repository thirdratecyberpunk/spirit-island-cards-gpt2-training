"""
Scrapes the powers from SICK and turns them into JSON
"""
from bs4 import BeautifulSoup
import argparse
import json
import re

def get_valid_filename(s):
    """
    Turns a given string into a safe filename string
    """
    s = str(s).strip().replace(' ', '_').lower()
    return re.sub(r'(?u)[^-\w.]', '', s)

parser=argparse.ArgumentParser(description="Turn HTML SICK into JSON of cards.")
parser.add_argument("--discard_unique", help="Do not include the original Spirit for Unique Powers.", action="store_true")
parser.add_argument("--discard_set", help="Do not include the set in the JSON.", action="store_true")
args = parser.parse_args()

# finding all the div-back elements
with open("sick-powers.html") as f:
    content = f.read()
    soup = BeautifulSoup(content, "html.parser")

soup.prettify()
card_backs = soup.findAll("div", class_="back")
# rewriting the cards as a JSON structure

for card in card_backs:
    # get and clean the html versions of the power
    power_json = {}
    power = card.span
    strings = list(power.stripped_strings)
    # remove the FAQ and get every second element
    strings = strings[:-1][1::2]
    # remove the first two characters (leftover whitespace and :)
    strings = [string[2:] for string in strings]

    # if the power targets a spirit, need to add a null value to range
    # also handles The Past Returns Again
    if strings[5] in ["Any Spirit", "Another Spirit","Yourself",""]:
        strings.insert(5, "None")

    # populate json of power
    if not args.discard_set:
        power_json["set"] = strings[0]
    power_json["name"] = strings[2]
    # removes the origin spirit for unique powers if this option is toggled
    if args.discard_unique and ":" in strings[1]:
        power_json["type"] = "Unique Power"
    else:
        power_json["type"] = strings[1]
    power_json["cost"] = strings[3]
    power_json["speed"] = strings[4]
    power_json["range"] = strings[5]
    power_json["target"] = strings[6]
    power_json["elements"] = strings[7]
    power_json["description"] = strings[8]
    power_json["artist"] = strings[9]

    filename = f"powers/{get_valid_filename(power_json['name'])}.json"
    # save json of power
    out_file = open(filename, "w")
    json.dump(power_json, out_file)
