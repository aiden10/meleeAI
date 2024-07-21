import matplotlib.pyplot as plt
import json
import os
import numpy as np
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

regular_path = os.path.join(CURRENT_DIR, 'stats.json')
gym_path = os.path.join(CURRENT_DIR, 'simv2', 'stats.json')

def create_plot(path):
    with open(path, "r") as data:
        match_data = json.load(data)
    matches = match_data["Matches"]

    match_numbers = [match["Match Number"] for match in matches]
    damages = [match["Damage Done"] for match in matches]
    performances = [match["Performance"] for match in matches]
    df = pd.DataFrame({
        'match_number': match_numbers,
        'damage_done': damages,
        'performances' : performances
    })

    # rolling average
    window_size = 100  
    df['damage_rolling_avg'] = df['damage_done'].rolling(window=window_size).mean()

    fig, ax1 = plt.subplots()

    # Plot damage done
    ax1.set_xlabel('Game Number')
    ax1.set_ylabel('Total Damage Done')
    ax1.plot(df['match_number'], df['damage_rolling_avg'], label=f'{window_size}-Game Damage Rolling Average', color='orange')
    ax1.scatter(df['match_number'], df['damage_done'], alpha=0.3, s=10)  
    low_damage = df[df['damage_done'] < 30]
    ax1.scatter(low_damage['match_number'], low_damage['damage_done'], color='red', alpha=0.6, s=10, label='Damage < 30')
    ax1.grid()
    ax1.legend(loc='upper left')

    # Create a second y-axis for performance
    ax2 = ax1.twinx()  
    ax2.set_ylabel('Performance')
    ax2.plot(df['match_number'], df['performances'], color='blue', alpha=0.2, label='Performance')
    ax2.legend(loc='upper right')

    fig.tight_layout()  # To ensure the right y-label is not slightly clipped

    plt.title('Training')
    plt.show()

create_plot(gym_path)
