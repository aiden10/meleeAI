import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import melee
from at import atBot
from functions import *

SLIPPI_PATH = r"C:\Users\aiden\AppData\Roaming\Slippi Launcher\netplay"

console = melee.Console(path=SLIPPI_PATH)

controller1 = melee.Controller(console=console, port=1)
controller2 = melee.Controller(console=console, port=2)

console.run()
console.connect()

controller1.connect()
controller2.connect()

p1 = atBot(port=1, controller=controller1)
p2 = atBot(port=2, controller=controller2)

while True:
    gamestate = console.step()
    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
        p1.calculate_states(gamestate, 2)
        p2.calculate_states(gamestate, 1)
        p1.move(gamestate)
        p2.move(gamestate)

    else:
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller1,
                                            melee.Character.MARTH,
                                            melee.Stage.FINAL_DESTINATION,
                                            connect_code="",
                                            costume=0,
                                            autostart=False,
                                            swag=False)
        
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller2,
                                            melee.Character.MARTH,
                                            melee.Stage.FINAL_DESTINATION,
                                            connect_code="",
                                            cpu_level=3,
                                            costume=0,
                                            autostart=True,
                                            swag=False)
