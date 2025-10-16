# place to read/write user data and parameter data

import json
import os

# helper function to load the user data from user.json 
def load_json(filepath, default_data):
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(default_data, f, indent=4)
    with open(filepath, "r") as f:
        return json.load(f)


# helper function that saves new user data to file
def save_json(filepath, data):

    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)