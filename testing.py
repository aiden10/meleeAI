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
