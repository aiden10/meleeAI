import melee
import ujson as json
import numpy as np
import sys
import os
from functions import *

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ATTACK_LIST = ['L_Tilt', 'R_Tilt', 'U_Tilt', 'L_Smash', 'R_Smash', 'U_Smash', 'D_Smash']
console = melee.Console(path=r"C:\Users\aiden\AppData\Roaming\Slippi Launcher\netplay")
json_file = open(f"{CURRENT_DIR}/agent_data.json", "r")
state_data = json.load(json_file)
print('loaded data')
total_damage = 0

def get_current_state(g, agent_port, opponent_port):
    agent_percent = get_percent(g, agent_port)
    opp_percent = get_percent(g, opponent_port)
    x_dist = get_x_dist(g)
    y_dist = get_y_dist(g)
    x_pos = get_x_pos(g, agent_port)
    y_pos = get_y_pos(g, agent_port)
    opp_x_pos = get_x_pos(g, opponent_port)
    opp_y_pos = get_y_pos(g, opponent_port)
    offstage = is_offstage(g, agent_port)
    airborne = is_airborne(g, opponent_port)
    direction = facing(g, agent_port)
    agent_stocks = get_stock(g, agent_port)
    opp_stocks = get_stock(g, opponent_port)
    agent_jumps = get_jumps(g, agent_port) > 0

    for state_num, data in state_data.items():
        state_info = data["State"]
        if (
            # agent_percent >= state_info["Agent Percentage"][0] and agent_percent <= state_info["Agent Percentage"][1] and
            # opp_percent >= state_info["Opponent Percentage"][0] and opp_percent <= state_info["Opponent Percentage"][1] and
            x_pos >= state_info["Agent_X_Position"][0] and x_pos <= state_info["Agent_X_Position"][1] and
            y_pos >= state_info["Agent_Y_Position"][0] and y_pos <= state_info["Agent_Y_Position"][1] and
            opp_x_pos >= state_info["Opponent_X_Position"][0] and opp_x_pos <= state_info["Opponent_X_Position"][1] and
            opp_y_pos >= state_info["Opponent_Y_Position"][0] and opp_y_pos <= state_info["Opponent_Y_Position"][1] and
            agent_jumps == state_info["Jumps_Left"]
            # x_dist >= state_info["X_Distance"][0] and x_dist <= state_info["X_Distance"][1] and
            # y_dist >= state_info["Y_Distance"][0] and y_dist <= state_info["Y_Distance"][1] and
            # offstage == state_info["Offstage"] and
            # airborne == state_info["Airborne"] and 
            # direction == state_info["Facing"]
        ):
            return state_num, (agent_percent, opp_percent, x_dist, y_dist, x_pos, offstage, airborne, direction, agent_stocks, opp_stocks, y_pos)

    return None 

def softmax(x):
    return (np.exp(x) / np.sum(np.exp(x), axis=0)).tolist()

def get_action(state_num):
    actions = state_data[str(state_num)]["Actions"]
    probabilities = list(actions.values())
    softmaxed_probabilities = softmax(probabilities)
    best_action = np.random.choice(list(actions.keys()), 1, p=softmaxed_probabilities)[0]
    return best_action    
        
def unpack_state(state):
    return state[0], state[1], state[2], state[3], state[4], state[5], state[6], state[7], state[8], state[9], state[10]

def calculate_rewards(prev_state, curr_state, agent):
    curr_x_dist, curr_y_dist, curr_x_pos, curr_agent_stocks, curr_opp_stocks, curr_y_pos, curr_agent_percent, curr_opp_percent = curr_state
    prev_x_dist, prev_y_dist, prev_x_pos, prev_agent_stocks, prev_opp_stocks, prev_y_pos, prev_agent_percent, prev_opp_percent = prev_state

    damage_taken_weight = 0.15
    damage_done_weight = 0.08
    distance_weight = 0.1

    distance_x = (prev_x_dist - curr_x_dist) * distance_weight if abs(curr_x_pos - prev_x_pos) > 5 and curr_x_dist < prev_x_dist else 0
    distance_y = (prev_y_dist - curr_y_dist) * distance_weight if abs(curr_y_pos - prev_y_pos) > 5 and curr_y_dist < prev_y_dist else 0

    agent_percent_diff = curr_agent_percent - prev_agent_percent
    opp_percent_diff = curr_opp_percent - prev_opp_percent 
    if opp_percent_diff > 0:
        total_damage += opp_percent_diff

    damage_taken = agent_percent_diff * damage_taken_weight
    damage_done = opp_percent_diff * damage_done_weight

    stock_lost = curr_agent_stocks < prev_agent_stocks
    stock_taken = curr_opp_stocks < prev_opp_stocks

    return distance_x, distance_y, damage_taken, damage_done, stock_lost, stock_taken 

def update_odds(dist_x, dist_y, damage_taken, damage_done, actions, learning_rate=0.01):
    nothing_weight = 0.1
    for state_num, action_list in actions.items():
        for action in action_list:
            if action != "Release":
                if dist_x and action in ['L_Walk', 'R_Walk', 'L_Dash', 'R_Dash']:
                    state_data[state_num]["Actions"][action] -= dist_x * learning_rate
                if dist_y and action == 'Jump':
                    state_data[state_num]["Actions"][action] -= dist_y * learning_rate
                if damage_done and action in ATTACK_LIST:
                    state_data[state_num]["Actions"][action] -= damage_done * learning_rate
                if damage_taken:
                    state_data[state_num]["Actions"][action] -= damage_taken * learning_rate
                if not (dist_x or dist_y or damage_done) and action in ATTACK_LIST:
                    state_data[state_num]["Actions"][action] -= nothing_weight * learning_rate
                    for move_action in ['L_Dash', 'R_Dash', 'L_Walk', 'R_Walk', 'Jump']:
                        state_data[state_num]["Actions"][move_action] += nothing_weight * learning_rate

def update_odds_long(stock_lost, stock_taken, actions_long, learning_rate=0.01):
    stock_weight = 0.15
    death_penalty = 0.05 * learning_rate
    sd_penalty = stock_weight * learning_rate
    if stock_lost:
        for state_num, action_list in actions_long.items():
            for action in action_list:
                if action != "Release":
                    state_data[state_num]["Actions"][action] += death_penalty
                    if action in ATTACK_LIST:
                        state_data[state_num]["Actions"][action] += sd_penalty

    if stock_taken:
        for state_num, action_list in actions_long.items():
            for action in action_list:
                if action != "Release":
                    state_data[state_num]["Actions"][action] -= stock_weight * learning_rate

def update_agent():
    with open(f"{CURRENT_DIR}/agent_data.json", "w") as json_file: 
        json.dump(state_data, json_file, indent=4)

def record_results(damage):
    data = open(f"{CURRENT_DIR}/stats.json", "r")
    match_data = json.load(data)
    match_number = match_data["Current Match"]
    match_data["Matches"].append({
        "Match Number": match_number,
        "Damage done": float(damage)
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
consecutive_same_state = 0

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

        # Update actions and state dictionary
        a1_performed_actions.add(a1_action)
        a2_performed_actions.add(a2_action)
        
        a1_performed_actions_long.add(a1_action)
        a2_performed_actions_long.add(a2_action)

        a1_actions.update({a1_state_num: a1_performed_actions})
        a2_actions.update({a2_state_num: a2_performed_actions})

        a1_actions_long.update({a1_state_num: a1_performed_actions_long})
        a2_actions_long.update({a2_state_num: a2_performed_actions_long})

        # Wait for however long the action takes
        target_frame = current_frame + wait_duration
        while current_frame < target_frame:
            waiting = True
            gamestate = console.step()
            current_frame += 1

        # Clear inputs after action has been performed
        Release(controller)
        Release(controller_opp)
        
    # After waiting
        waiting = False

    # Look at states after actions have been performed
        if prev_a1_state and prev_a2_state:
            if prev_a1_state == curr_a1_state:
                consecutive_same_state += 1
            else: 
                consecutive_same_state = 0

            opp_stocks = prev_a1_state[8]
            # Update the odds
            a1_distance_x, a1_distance_y, a1_damage_taken, a1_damage_done, a1_stock_lost, a1_stock_taken = calculate_rewards(prev_a1_state, curr_a1_state)
            update_odds(a1_distance_x, a1_distance_y, a1_damage_taken, a1_damage_done, a1_actions)
            
            # Reset short term actions list
            a1_performed_actions = set()
            a1_actions = {}

            # Update odds with longer context
            # Reset the long term actions list when stocks change
            if a1_stock_lost or a1_stock_taken: 
                update_odds_long(a1_stock_lost, a1_stock_taken, a1_actions_long)                
                a1_performed_actions_long = set()
                a1_actions_long = {}    
            
            a2_distance_x, a2_distance_y, a2_damage_taken, a2_damage_done, a2_stock_lost, a2_stock_taken = calculate_rewards(prev_a2_state, curr_a2_state)
            update_odds(a2_distance_x, a2_distance_y, a2_damage_taken, a2_damage_done, a2_actions)
            a2_performed_actions = set()
            a2_actions = {}

            if a2_stock_lost or a2_stock_taken:
                update_odds_long(a2_stock_lost, a2_stock_taken, a2_actions_long)
                a2_performed_actions_long = set()
                a2_actions_long = {}
        
        prev_a1_state = curr_a1_state
        prev_a2_state = curr_a2_state

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
            print('updated agent')
            record_results(total_damage)
            total_damage = 0
            print('recorded results')

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


