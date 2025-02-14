"""
Ultimate:
Read yuzu's memory
Write functions to extract values like player percentages, x,y positions, game state, etc.
    Will require some trial and error to determine the memory addresses

Setup functions to simulate button presses
Might not be too bad because of libraries which simulate gamepads, just need to make it work with yuzu

AI can either be machine learning or a state machine
State machine:
    Easier to make but less interesting
    Still challenging to make good and would be fun to make without worrying about machine learning stuff

Machine learning:
    Tough to make good because smash is so fast and there's tons of possible actions and button combinations
    Making it actually good would be very difficult

Replays:
    Since Ultimate has replay's it might be possible to try to make a humanlike agent by training a model to predict the controller state based on 
    tons of replays
    This would be pretty tough especially since replays aren't readily available and I don't know the format
    Would require a lot of replays and would really only work for one set of characters and stages
"""

import melee
from functions import *

SLIPPI_PATH = r"C:\Users\aiden\AppData\Roaming\Slippi Launcher\netplay"

console = melee.Console(path=SLIPPI_PATH)

controller1 = melee.Controller(console=console, port=1)
controller2 = melee.Controller(console=console, port=2)

console.run()
console.connect()

controller1.connect()
controller2.connect()

waiting = False
done = False
current_frame = 0
while True:
    if not waiting: gamestate = console.step()
    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
        current_frame += 1
        print(f"controller2 xy: ({get_x_pos(gamestate, 2)}, {get_y_pos(gamestate, 2)})")
        wait_duration = Jump(controller2)
        target_frame = current_frame + wait_duration
        while current_frame < target_frame:
            waiting = True
            gamestate = console.step()
            current_frame += 1
        
        Release(controller1)
        Release(controller2)

        buffer_wait = current_frame + 20
        while current_frame < buffer_wait: 
            waiting = True
            gamestate = console.step()
            current_frame += 1

    else:
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller1,
                                            melee.Character.MARTH,
                                            melee.Stage.FINAL_DESTINATION,
                                            connect_code="",
                                            costume=0,
                                            autostart=True,
                                            swag=False)
        
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller2,
                                            melee.Character.MARTH,
                                            melee.Stage.FINAL_DESTINATION,
                                            connect_code="",
                                            cpu_level=0,
                                            costume=0,
                                            autostart=True,
                                            swag=False)
