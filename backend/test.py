import json

with open("regulations.json") as f:
    data = json.load(f)

for reg in data:
    print(reg["bill"], reg["jurisdiction"], reg["fields"].keys())
