import melee
import json
import random
import sys
import os
import random

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
console = melee.Console(path=r"C:\Users\aiden\AppData\Roaming\Slippi Launcher\netplay")
json_file = open(f"{CURRENT_DIR}/agent_data.json", "r")
state_data = json.load(json_file)

# Observations
def get_percent(g, port):
    return g.players[port].percent

def get_x_dist(g):
    agent_x = g.players[1].position.x
    opp_x = g.players[2].position.x
    return abs(agent_x - opp_x)

def get_y_dist(g):
    agent_y = g.players[1].position.y
    opp_y = g.players[2].position.y
    return abs(agent_y - opp_y)

def get_x_pos(g, port):
    return g.players[port].position.x

def is_offstage(g, port):
    return g.players[port].off_stage

def is_airborne(g, port):
    return g.players[port].on_ground

def facing(g, port):
    return g.players[port].facing

def get_stock(g, port):
    return g.players[port].stock

# Basic Attacks
def Jab(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    return 27
def L_Tilt(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.35, 0.5)
    return 35

def R_Tilt(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.65, 0.5)
    return 35

def U_Tilt(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 0.65)
    return 39

def D_Tilt(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 0.35)
    return 49

# Smash Attacks
def L_Smash(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0, 0.5)
    return 49

def R_Smash(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 1, 0.5)
    return 49

def U_Smash(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 1)
    return 54

def D_Smash(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 0)
    return 64

# Special Attacks
def N_Special(controller):
    controller.press_button(melee.enums.Button.BUTTON_B)
def L_Special(controller):
    controller.press_button(melee.enums.Button.BUTTON_B)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0, 0.5)
def R_Special(controller):
    controller.press_button(melee.enums.Button.BUTTON_B)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 1, 0.5)
def U_Special(controller):
    controller.press_button(melee.enums.Button.BUTTON_B)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 1)
def D_Special(controller):
    controller.press_button(melee.enums.Button.BUTTON_B)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 0)

# Dash Attacks
def L_DAttack(controller):
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 0.5)
    controller.press_button(melee.enums.Button.BUTTON_A)
    return 60

def R_DAttack(controller):
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 1, 0.5)
    controller.press_button(melee.enums.Button.BUTTON_A)
    return 60

# Throws
def L_Throw(controller):
    controller.press_button(melee.enums.Button.BUTTON_Z)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0, 0.5)
    return 29

def R_Throw(controller):
    controller.press_button(melee.enums.Button.BUTTON_Z)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 1, 0.5)
    return 29

def U_Throw(controller):
    controller.press_button(melee.enums.Button.BUTTON_Z)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 1)
    return 29

def D_Throw(controller):
    controller.press_button(melee.enums.Button.BUTTON_Z)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 0)
    return 29

def Shield(controller):
    controller.press_button(melee.enums.Button.BUTTON_R)
    return 100

def Release(controller):
    controller.release_all()
    return 15

# Movements
def L_Dodge(controller):
    controller.press_button(melee.enums.Button.BUTTON_R)
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 0.5)
    return 45

def R_Dodge(controller):
    controller.press_button(melee.enums.Button.BUTTON_R)
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 1, 0.5)
    return 45

def Jump(controller):
    controller.press_button(melee.enums.Button.BUTTON_X)
    return 120

def L_Walk(controller):
    controller.release_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.65, 0.5)
    return 60

def R_Walk(controller):
    controller.release_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.35, 0.5)
    return 60

def L_Dash(controller):
    controller.release_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 0.5)
    return 60

def R_Dash(controller):
    controller.release_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 1, 0.5)
    return 60

def get_random_action():
    actions = [R_Dash, L_Dash, R_Walk, L_Walk, Jump, R_Dodge, L_Dodge, Release, Shield, L_Throw, R_Throw, D_Throw, U_Throw,
               L_DAttack, R_DAttack, L_Smash, R_Smash, D_Smash, U_Smash, L_Tilt, R_Tilt, U_Tilt, D_Tilt, Jab]
    return actions[random.randint(0, len(actions) - 1)]

def get_current_state(g, agent_port, opponent_port):
    agent_percent = get_percent(g, agent_port)
    opp_percent = get_percent(g, opponent_port)
    x_dist = get_x_dist(g)
    y_dist = get_y_dist(g)
    x_pos = get_x_pos(g, agent_port)
    offstage = is_offstage(g, agent_port)
    airborne = is_airborne(g, opponent_port)
    agent_right = facing(g, agent_port)
    agent_stocks = get_stock(g, agent_port)
    opp_stocks = get_stock(g, opponent_port)

    for state_num, data in state_data.items():
        state_info = data["State"]
        if (
            agent_percent >= state_info["Agent Percentage"][0] and agent_percent <= state_info["Agent Percentage"][1] and
            opp_percent >= state_info["Opponent Percentage"][0] and opp_percent <= state_info["Opponent Percentage"][1] and
            x_pos >= state_info["X_Position"][0] and x_pos <= state_info["X_Position"][1] and
            x_dist >= state_info["X_Distance"][0] and x_dist <= state_info["X_Distance"][1] and
            y_dist >= state_info["Y_Distance"][0] and y_dist <= state_info["Y_Distance"][1] and
            offstage == state_info["Offstage"] and
            airborne == state_info["Airborne"] 
            # agent_right == state_info["Agent Right"]
        ):
            return state_num, (agent_percent, opp_percent, x_dist, y_dist, x_pos, offstage, airborne, agent_right, agent_stocks, opp_stocks)

    return None 

def get_action(state_num):
    actions = state_data[str(state_num)]["Actions"]
    # Normalize action probabilities to be non-negative
    min_prob = min(actions.values())
    if min_prob < 0:
        actions = {action: prob - min_prob for action, prob in actions.items()}

    total_prob = sum(actions.values())
    if total_prob == 0:
        return "Release"  # Return default action if all probabilities are zero

    # Normalize the probabilities to sum to 1
    actions = {action: prob / total_prob for action, prob in actions.items()}

    rand_num = random.uniform(0, 1)
    cumulative_prob = 0
    for action, prob in actions.items():
        cumulative_prob += prob
        if rand_num <= cumulative_prob:
            return action

    return "Release"  # Fallback in case no action is selected
        
def unpack_state(state):
    return state[0], state[1], state[2], state[3], state[4], state[5], state[6], state[7], state[8], state[9]

def calculate_rewards(prev_state, curr_state):
    prev_agent_percent, prev_opp_percent, prev_x_dist, prev_y_dist, prev_x_pos, _, _, _, prev_agent_stocks, prev_opp_stocks = unpack_state(prev_state)
    curr_agent_percent, curr_opp_percent, curr_x_dist, curr_y_dist, curr_x_pos, _, _, _, curr_agent_stocks, curr_opp_stocks = unpack_state(curr_state)
    
    # weights subject to change
    distance_x_weight = 0.1
    distance_y_weight = 0.1
    damage_taken_weight = 0.2
    damage_done_weight = 0.1
    
    # X/Y Position
    x_diff = curr_x_dist - prev_x_dist 
    y_diff = curr_y_dist - prev_y_dist
    distance_x = x_diff * distance_x_weight
    distance_y = y_diff * distance_y_weight

    # Percentages
    agent_percent_diff = curr_agent_percent - prev_agent_percent # Damage taken 
    opp_percent_diff = curr_opp_percent - prev_opp_percent 
    damage_taken = agent_percent_diff * damage_taken_weight
    damage_done = opp_percent_diff * damage_done_weight

    # Stocks
    stock_lost = False
    stock_taken = False
    if curr_agent_stocks < prev_agent_stocks: stock_lost = True
    if curr_opp_stocks < prev_opp_stocks: stock_taken = True

    return distance_x, distance_y, damage_taken, damage_done, stock_lost, stock_taken 

def update_odds(dist_x, dist_y, damage_taken, damage_done, actions):
    for state_num, action_list in actions.items():  # Iterate over state numbers and associated actions
        for action in action_list:  # Iterate over actions for each state
            if action != "Release":
                # Distance (x)
                if dist_x != 0:
                    print(f'{action} of state #{state_num}: changed by {dist_x}')
                    state_data[state_num]["Actions"][action] -= dist_x
                # Distance (y)
                if dist_y != 0:
                    state_data[state_num]["Actions"][action] -= dist_y
                    print(f'{action} of state #{state_num}: changed by {dist_y}')
                # Damage done
                if damage_done != 0:
                    state_data[state_num]["Actions"][action] += damage_done
                    print(f'{action} of state #{state_num}: changed by {damage_done}')
                # Damage taken
                if damage_taken != 0:
                    state_data[state_num]["Actions"][action] -= damage_taken
                    print(f'{action} of state #{state_num}: changed by {damage_taken}')


def update_odds_long(stock_lost, stock_taken, actions_long):
    # Stocks
    stock_weight = 0.5 
    for state_num, action_list in actions_long.items():  
        for action in action_list:  
            if stock_lost:
                state_data[state_num]["Actions"][action] += (stock_weight)
                print(f'{action} of state #{state_num}: changed by {stock_weight}')
            if stock_taken:
                state_data[state_num]["Actions"][action] -= (stock_weight)
                print(f'{action} of state #{state_num}: changed by -{stock_weight}')

def update_agent():
    with open(f"{CURRENT_DIR}/agent_data.json", "w") as json_file: 
        json.dump(state_data, json_file, indent=4)

def record_results(stocks_taken):
    data = open(f"{CURRENT_DIR}/stats.json", "r")
    match_data = json.load(data)
    match_number = match_data["Current Match"]
    match_data["Matches"].append({
        "Match Number": match_number,
        "Stocks Remaining": int(stocks_taken)
    })

    match_data["Current Match"] += 1
    data.close()

    with open(f"{CURRENT_DIR}/stats.json", "w") as fh:
        json.dump(match_data, fh, indent=4) 

controller = melee.Controller(console=console, port=1)
controller_opp = melee.Controller(console=console, port=2)

console.run()
console.connect()

controller.connect()
controller_opp.connect()
a1_character = melee.Character.MARTH
a2_character = melee.Character.MARTH

updated = False
a1_performed_actions_long = set()
a2_performed_actions_long = set()
a1_actions_long = {}
a2_actions_long = {}
current_frame = 0
opp_stocks = 0
consecutive_same_state = 0
button_pressed = False

prev_a1_state = None
curr_a1_state = None
prev_a2_state = None
curr_a2_state = None
waiting = False
updated = False

while True:
    if not waiting: gamestate = console.step()
    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
        current_frame += 1

        a1_performed_actions = set()
        a2_performed_actions = set()

        a1_actions = {}
        a2_actions = {}

        updated = False
        a1_state_num, curr_a1_state  = get_current_state(gamestate, 1, 2)
        a2_state_num, curr_a2_state  = get_current_state(gamestate, 2, 1)
        
        # Controller state
        # a1_R = gamestate.players[1].controller_state.button[melee.enums.Button.BUTTON_R]
        # a1_Z = gamestate.players[1].controller_state.button[melee.enums.Button.BUTTON_Z]
        # a1_A = gamestate.players[1].controller_state.button[melee.enums.Button.BUTTON_A]
        # a1_C = gamestate.players[1].controller_state.c_stick

        # a2_R = gamestate.players[2].controller_state.button[melee.enums.Button.BUTTON_R]
        # a2_Z = gamestate.players[2].controller_state.button[melee.enums.Button.BUTTON_Z]
        # a2_A = gamestate.players[2].controller_state.button[melee.enums.Button.BUTTON_A]
        # a2_C = gamestate.players[2].controller_state.c_stick

        # if button_pressed:
        #     if a1_R : controller.release_button(melee.enums.Button.BUTTON_R)
        #     if a1_Z : controller.release_button(melee.enums.Button.BUTTON_Z)
        #     if a1_A : controller.release_button(melee.enums.Button.BUTTON_A)
        #     if a1_C[0] != 0.5 or a1_C[1] != 0.5: controller.release_button(melee.enums.Button.BUTTON_C)

        #     if a2_R : controller_opp.release_button(melee.enums.Button.BUTTON_R)
        #     if a2_Z : controller_opp.release_button(melee.enums.Button.BUTTON_Z)
        #     if a2_A : controller_opp.release_button(melee.enums.Button.BUTTON_A)
        #     if a2_C[0] != 0.5 or a2_C[1] != 0.5: controller_opp.release_button(melee.enums.Button.BUTTON_C)

        # if prev_a1_state and prev_a2_state:
        #     print(f'before: {prev_a1_state}')
        #     print(f'after: {curr_a1_state}')
        #     print('-------------------------------------------------')

        # perform actions
        if consecutive_same_state < 2:
            a1_action = get_action(a1_state_num)
            a1_action_func = getattr(sys.modules[__name__], a1_action, None)

            a2_action = get_action(a2_state_num)
            a2_action_func = getattr(sys.modules[__name__], a2_action, None)
        else: # if stuck in same state, do random action
            a1_action_func = get_random_action() 
            a2_action_func = get_random_action()
            print('doing random action')

        a1_wait = a1_action_func(controller)
        a2_wait = a2_action_func(controller_opp)
        wait_duration = max(a1_wait, a2_wait)

        # else:
        #     a1_action = "Release"
        #     a2_action = "Release"
        #     button_pressed = False
            
        # if a1_action != "Release":
        #     print(f'A1: {a1_action}')
        #     print(f'A2: {a2_action}')

        # Update actions and state dictionary
        a1_performed_actions.add(a1_action)
        a2_performed_actions.add(a2_action)
        
        a1_performed_actions_long.add(a1_action)
        a2_performed_actions_long.add(a2_action)

        a1_actions.update({a1_state_num: a1_performed_actions})
        a2_actions.update({a2_state_num: a2_performed_actions})

        a1_actions_long.update({a1_state_num: a1_performed_actions_long})
        a2_actions_long.update({a2_state_num: a2_performed_actions_long})

        # Wait
        target_frame = current_frame + wait_duration
        while current_frame < target_frame:
            waiting = True
            console.step()
            current_frame += 1

    # After waiting
        waiting = False

    # Look at states after actions have been performed
        if prev_a1_state and prev_a2_state:
            if prev_a1_state == curr_a1_state:
                consecutive_same_state += 1
            else: consecutive_same_state = 0
            opp_stocks = prev_a1_state[8]
            # Update the odds
            a1_distance_x, a1_distance_y, a1_damage_taken, a1_damage_done, a1_stock_lost, a1_stock_taken = calculate_rewards(prev_a1_state, curr_a1_state)
            update_odds(a1_distance_x, a1_distance_y, a1_damage_taken, a1_damage_done, a1_actions)
            
            # Reset short term actions list
            a1_performed_actions = set()
            a1_actions = {}

            # Update odds with longer context
            update_odds_long(a1_stock_lost, a1_stock_taken, a1_actions_long)                
            # Reset the long term actions list when stocks change
            if a1_stock_lost or a1_stock_taken: 
                a1_performed_actions_long = set()
                a1_actions_long = {}
            
            a2_distance_x, a2_distance_y, a2_damage_taken, a2_damage_done, a2_stock_lost, a2_stock_taken = calculate_rewards(prev_a2_state, curr_a2_state)
            update_odds(a2_distance_x, a2_distance_y, a2_damage_taken, a2_damage_done, a2_actions)
            update_odds_long(a2_stock_lost, a2_stock_taken, a2_actions_long)
            a2_performed_actions = set()
            a2_actions = {}

            if a2_stock_lost or a2_stock_taken:
                a2_performed_actions_long = set()
                a2_actions_long = {}
        
        prev_a1_state = curr_a1_state
        prev_a2_state = curr_a2_state

        # Clear inputs after action has been performed
        Release(controller)
        Release(controller_opp)

    else:
        if not updated:
            controller.release_all()
            controller_opp.release_all()
            current_frame = 0
            updated = True
            prev_a1_state = None
            curr_a1_state = None
            prev_a2_state = None
            curr_a2_state = None
            update_agent()

            # record_results(opp_stocks)


        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller,
                                            a1_character,
                                            melee.Stage.FINAL_DESTINATION,
                                            connect_code="",
                                            costume=0,
                                            autostart=True,
                                            swag=False)
        
        melee.MenuHelper.menu_helper_simple(gamestate,
                                            controller_opp,
                                            a2_character,
                                            melee.Stage.FINAL_DESTINATION,
                                            connect_code="",
                                            cpu_level=0,
                                            costume=0,
                                            autostart=True,
                                            swag=False)


