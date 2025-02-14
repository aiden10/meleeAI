import matplotlib.pyplot as plt
import json
import os
import numpy as np
import pandas as pd
import matplotlib.animation as animation

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
gym_path = os.path.join(CURRENT_DIR, 'gym', 'stats.json')
deepq_path = os.path.join(CURRENT_DIR, 'deepq', 'stats.json')
real_game_path = os.path.join(CURRENT_DIR, 'stats.json')

def load_data(path):
    with open(path, "r") as data:
        match_data = json.load(data)
    matches = match_data["Matches"]
    match_numbers = [match["Match Number"] for match in matches]
    damages = [match["Damage Done"] for match in matches]
    performances = [match["Performance"] for match in matches]
    df = pd.DataFrame({
        'match_number': match_numbers,
        'damage_done': damages,
        'performances': performances
    })
    window_size = 100
    df['damage_rolling_avg'] = df['damage_done'].rolling(window=window_size).mean()
    return df

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)

def animate(i):
    df = load_data(deepq_path)
    
    ax1.clear()
    ax2.clear()
    
    # Plot damage done
    ax1.set_ylabel('Total Damage Done')
    ax1.plot(df['match_number'], df['damage_rolling_avg'], label='100-Game Damage Rolling Average', color='orange')
    ax1.scatter(df['match_number'], df['damage_done'], alpha=0.3, s=10)
    low_damage = df[df['damage_done'] < 30]
    ax1.scatter(low_damage['match_number'], low_damage['damage_done'], color='red', alpha=0.6, s=10, label='Damage < 30')
    ax1.grid()
    ax1.legend(loc='upper left')
    
    # Plot performance
    ax2.set_xlabel('Game Number')
    ax2.set_ylabel('Q-Value')
    ax2.plot(df['match_number'], df['performances'], color='blue', alpha=0.2, label='Q-Values')
    ax2.legend(loc='upper right')
    ax2.grid()
    plt.text(0.5, 0.93, 'Training', fontsize=20, transform=plt.gcf().transFigure)
    plt.text(0.025, 0.93, '', fontsize=16, transform=plt.gcf().transFigure)
    plt.text(0.015, 0.03, '', fontsize=9, transform=plt.gcf().transFigure)

ani = animation.FuncAnimation(fig, animate, interval=5000, cache_frame_data=False)  # 5 seconds
plt.show()