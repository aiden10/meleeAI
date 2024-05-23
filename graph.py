import matplotlib.pyplot as plt
import json
import os
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def create_plot():

    data = open(f"{CURRENT_DIR}/stats.json", "r")
    match_data = json.load(data)
    matches = match_data["Matches"]
    damages = []
    match_numbers = []
    for match in matches:
        match_numbers.append(match["Match Number"]) 
        damages.append(match["Damage done"])
    
    fig, ax = plt.subplots()
    ax.plot(match_numbers, damages)

    ax.set(xlabel='Game Number', ylabel='Total Damage Done',
    title='Training')
    ax.grid()

    plt.show()

create_plot()