import os, json

def get_locations(root = os.path.dirname(os.path.realpath(__file__))):
    with open(os.path.join(root, 'divisions.txt'), 'r', encoding = 'utf-8') as f:
        divisions = json.load(f)

    with open(os.path.join(root, 'districts.txt'), 'r', encoding = 'utf-8') as f:
        districts = json.load(f)

    with open(os.path.join(root, 'upazilas.txt'), 'r', encoding = 'utf-8') as f:
        upazilas = json.load(f)

    return {
        "divisions": divisions,
        "districts": districts,
        "upazilas": upazilas
    }