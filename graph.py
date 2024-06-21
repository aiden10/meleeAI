import matplotlib.pyplot as plt
import json
import os
import numpy as np
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

regular_path = os.path.join(CURRENT_DIR, 'stats.json')
gym_path = os.path.join(CURRENT_DIR, 'gym', 'stats.json')

def create_plot(path):
    with open(path, "r") as data:
        match_data = json.load(data)
    matches = match_data["Matches"]

    match_numbers = [match["Match Number"] for match in matches]
    damages = [match["Damage done"] for match in matches]

    df = pd.DataFrame({
        'match_number': match_numbers,
        'damage_done': damages
    })

    # rolling average
    window_size = 100  
    df['rolling_avg'] = df['damage_done'].rolling(window=window_size).mean()

    fig, ax = plt.subplots()
    ax.plot(df['match_number'], df['rolling_avg'], label=f'{window_size}-Game Rolling Average', color='orange')
    ax.scatter(df['match_number'], df['damage_done'], alpha=0.3, s=10)  
    low_damage = df[df['damage_done'] < 10]
    
    ax.scatter(low_damage['match_number'], low_damage['damage_done'], color='red', alpha=0.6, s=10, label='Damage < 30')

    ax.set(xlabel='Game Number', ylabel='Total Damage Done', title='Training')
    ax.grid()
    ax.legend()

    plt.show()

create_plot(gym_path)

# 905 started using pretrained agent