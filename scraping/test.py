import json

with open("website_structure.json") as f:
    data = json.load(f)

for l in data:
    if l[-3:] == "/n0":
        if l[:-3] in data:
            equal = True
            for ll in data[l]:
                if ll not in data[l[:-3]] and ll[:-3] not in data[l[:-3]]:
                    equal = False
            if equal:
                print("Equal")
            else:
                print("Not Equal - " + l)
        else:
            print("not present - " + l)


# erkenntnisse:
# 0. nicht jede Addresse ohne /n0 hat einen parallelen Eintrag mit /n0
# 1. nicht jede /n0 Addresse hat einen eintrag ohne /n0
# 2. diejenigen /n0 Addressen die auch einen eintrag ohne /n0 haben, sind von den Sublinks gleich (bis auf den loop link zur eigenen Seite)
# => es muss A u B gewählt werden
