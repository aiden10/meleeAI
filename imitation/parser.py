import os
from slippi import Game
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
game = Game(f'{CURRENT_DIR}/replays/BouncyLargeBaboon.slp')
print(game.frames[0])