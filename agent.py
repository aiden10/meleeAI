import melee
import ujson as json
import numpy as np
import sys
import os
from functions import *

class Agent:
    def __init__(self):
        self.damage_done = 0
        self.performance = 0

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
            return state_num, (x_dist, y_dist, x_pos, agent_stocks, opp_stocks, y_pos, agent_percent, opp_percent)

    return None 

def get_action(games_played, state_num, initial_epsilon=0.8, min_epsilon=0.05, decay_rate=0.01):
    actions = state_data[str(state_num)]["Actions"]

    # Calculate epsilon
    epsilon = max(min_epsilon, initial_epsilon * (1 / (1 + decay_rate * games_played)))

    def select_action(rewards):
        if random.random() < epsilon:
            # Random action (exploration)
            return random.choice(list(rewards.keys()))
        else:
            # Best action (exploitation)
            return max(rewards, key=rewards.get)

    return select_action(actions)
        
def unpack_state(state):
    return state[0], state[1], state[2], state[3], state[4], state[5], state[6], state[7], state[8], state[9], state[10]

def calculate_rewards(prev_state, curr_state, agent):
    curr_x_dist, curr_y_dist, curr_x_pos, curr_agent_stocks, curr_opp_stocks, curr_y_pos, curr_agent_percent, curr_opp_percent = curr_state
    prev_x_dist, prev_y_dist, prev_x_pos, prev_agent_stocks, prev_opp_stocks, prev_y_pos, prev_agent_percent, prev_opp_percent = prev_state

    distance_x = (prev_x_dist - curr_x_dist) if abs(curr_x_pos - prev_x_pos) > 5 and curr_x_dist < prev_x_dist else 0
    distance_y = (prev_y_dist - curr_y_dist) if abs(curr_y_pos - prev_y_pos) > 5 and curr_y_dist < prev_y_dist else 0

    agent_percent_diff = curr_agent_percent - prev_agent_percent
    opp_percent_diff = curr_opp_percent - prev_opp_percent 
    if opp_percent_diff > 0:
        agent.damage_done += opp_percent_diff

    damage_taken = agent_percent_diff
    damage_done = opp_percent_diff

    stock_lost = curr_agent_stocks < prev_agent_stocks
    stock_taken = curr_opp_stocks < prev_opp_stocks

    return distance_x, distance_y, damage_taken, damage_done, stock_lost, stock_taken 

def update_q_value(agent, prev_state_num, action, reward, next_state_num, update, learning_rate=0.1, discount_factor=0.9):
    max_next_q_value = max(state_data[next_state_num]["Actions"].values()) if next_state_num is not None else 0
    current_q_value = state_data[prev_state_num]["Actions"][action]
    new_q_value = current_q_value + learning_rate * (reward + discount_factor * max_next_q_value - current_q_value)
    
    if update:
        state_data[prev_state_num]["Actions"][action] = new_q_value
    
    agent.performance += new_q_value

def q_learning_step(agent, prev_state_num, prev_state_values, action, curr_state_num, curr_state_values, update=True):

    dist_x, dist_y, damage_taken, damage_done, stock_lost, stock_taken = calculate_rewards(prev_state_values, curr_state_values, agent)

    reward = (
        damage_done - damage_taken + 
        (dist_x + dist_y) // 5 +
        (5 if stock_taken else 0) - 
        (5 if stock_lost else 0) - 
        (1 if not any([dist_x, dist_y, damage_done]) else 0)
    )

    update_q_value(agent, prev_state_num, action, reward, curr_state_num, update)

def update_odds_long(agent, stock_lost, stock_taken, actions_long, update, learning_rate=0.01):
    if update:
        stock_reward = 10 * learning_rate
        if stock_lost:
            for state_num, action_list in actions_long.items():
                for action in action_list:
                    if action != "Release":
                        state_data[state_num]["Actions"][action] -= stock_reward
                        agent.performance -= stock_reward

        if stock_taken:
            for state_num, action_list in actions_long.items():
                for action in action_list:
                    if action != "Release":
                        state_data[state_num]["Actions"][action] += stock_reward * learning_rate
                        agent.performance += stock_reward * learning_rate

def get_damage_done(curr_state, prev_state):
    _, _, _, _, _, _, _, curr_opp_percent = curr_state
    _, _, _, _, _, _, _, prev_opp_percent = prev_state
    return curr_opp_percent - prev_opp_percent

def update_agent():
    with open(f"{CURRENT_DIR}/agent_data.json", "w") as json_file: 
        json.dump(state_data, json_file)

def get_game_num():
    data = open(f"{CURRENT_DIR}/stats.json", "r")
    match_data = json.load(data)
    match_number = match_data["Current Match"]
    return match_number

def record_results(performance, damage):
    data = open(f"{CURRENT_DIR}/stats.json", "r")
    match_data = json.load(data)
    match_number = match_data["Current Match"]
    match_data["Matches"].append({
        "Match Number": match_number,
        "Performance": float(performance),
        "Damage Done": float(damage)
    })
    match_data["Current Match"] += 1

    data.close()

    with open(f"{CURRENT_DIR}/stats.json", "w") as fh:
        json.dump(match_data, fh) 

def main(train, record):
    game_num = get_game_num()
    agent = Agent()
    enemy_agent = Agent()
    controller = melee.Controller(console=console, port=1)
    controller_opp = melee.Controller(console=console, port=2)

    console.run()
    console.connect()

    controller.connect()
    controller_opp.connect()
    a1_character = melee.Character.MARTH
    a2_character = melee.Character.MARTH

    updated = False
    a1_actions_long = {}
    a2_actions_long = {}
    current_frame = 0
    consecutive_same_state = 0

    prev_a1_state = None
    prev_a1_state_num = None
    curr_a1_state = None
    prev_a2_state = None
    prev_a2_state_num = None
    curr_a2_state = None
    waiting = False
    updated = False

    while True:
        if not waiting: gamestate = console.step()
        if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
            current_frame += 1

            updated = False
            a1_state_num, curr_a1_state  = get_current_state(gamestate, 1, 2)
            a2_state_num, curr_a2_state  = get_current_state(gamestate, 2, 1)
            
            # perform actions
            # if consecutive_same_state < 2:
            a1_action = get_action(game_num, a1_state_num)
            a1_action_func = getattr(sys.modules[__name__], a1_action, None)

            a2_action = get_action(game_num, a2_state_num)
            a2_action_func = getattr(sys.modules[__name__], a2_action, None)
            # else: # if stuck in same state, do random action
            #     a1_action_func = get_random_action() 
            #     a2_action_func = get_random_action()
            #     print('doing random action')

            a1_wait = a1_action_func(controller)
            a2_wait = a2_action_func(controller_opp)
            wait_duration = max(a1_wait, a2_wait)
            
            a1_actions_long.update({a1_state_num: a1_action})
            a2_actions_long.update({a2_state_num: a2_action})

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

                # Update the q-values
                _, _, _, _, a1_stock_lost, a1_stock_taken = calculate_rewards(prev_a1_state, curr_a1_state, agent)
                q_learning_step(agent, prev_a1_state_num, prev_a1_state, a1_action, a1_state_num, curr_a1_state, train)
                
                # Update with longer context
                # Reset the long term actions list when stocks change
                if a1_stock_lost or a1_stock_taken: 
                    update_odds_long(agent, a1_stock_lost, a1_stock_taken, a1_actions_long, train) 
                    a1_actions_long = {}    
                
                _, __, __, __, a2_stock_lost, a2_stock_taken = calculate_rewards(prev_a2_state, curr_a2_state, enemy_agent)
                q_learning_step(enemy_agent, prev_a2_state_num, prev_a2_state, a2_action, a2_state_num, curr_a2_state, train)

                if a2_stock_lost or a2_stock_taken:
                    update_odds_long(enemy_agent, a2_stock_lost, a2_stock_taken, a2_actions_long, train)
                    a2_actions_long = {}
                

            prev_a1_state = curr_a1_state
            prev_a1_state_num = a1_state_num
            prev_a2_state = curr_a2_state
            prev_a2_state_num = a2_state_num

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
                if train:
                    update_agent()
                    print('updated agent')
                    game_num += 1

                if record:
                    average_damage = round((agent.damage_done + enemy_agent.damage_done) / 2, 2)
                    average_performance = round((agent.performance + enemy_agent.performance) / 2, 2)
                    record_results(average_performance, average_damage)
                    agent.damage_done = 0
                    enemy_agent.damage_done = 0
                    agent.performance = 0
                    enemy_agent.performance = 0
                    print('recorded results')

            melee.MenuHelper.menu_helper_simple(gamestate,
                                                controller,
                                                a1_character,
                                                melee.Stage.FINAL_DESTINATION,
                                                connect_code="",
                                                cpu_level=0,
                                                costume=0,
                                                autostart=False,
                                                swag=False)
            
            melee.MenuHelper.menu_helper_simple(gamestate,
                                                controller_opp,
                                                a2_character,
                                                melee.Stage.FINAL_DESTINATION,
                                                connect_code="",
                                                cpu_level=3,
                                                costume=0,
                                                autostart=True,
                                                swag=False)


main(train=False, record=True)