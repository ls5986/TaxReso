import json

def load_data():
    with open('data.json', 'r') as file:
        data = json.load(file)
    return data
