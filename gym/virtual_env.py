import ujson as json
import random
import os
import numpy as np
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ATTACK_LIST = ['L_Tilt', 'R_Tilt', 'U_Tilt', 'D_Tilt', 'L_Smash', 'R_Smash', 'U_Smash', 'D_Smash', 'Jab']
LEFT_BORDER = -225
RIGHT_BORDER = 225
TOP_BORDER = 200
BOTTOM_BORDER = -110
FALL_SPEED = 10
DAMAGE_SCALE = 2.5

with open(f"{CURRENT_DIR}/agent_data.json", "r") as json_file:
    state_data = json.load(json_file)
print('loaded data')

class Agent:
    def __init__(self, start_X):
        self.x = start_X
        self.y = 0
        self.stocks = 4
        self.percent = 0
        self.damage_done = 0
        self.jumps = 2
        self.performance = 0
        self.initial_X = start_X

    def reset_after_game(self):
        self.__init__(self.initial_X)

    def reset_on_death(self):
        self.x = self.initial_X
        self.y = 0
        self.percent = 0
        self.jumps = 2

    def is_offstage(self):
        return self.x < -85 or self.x > 85

    def L_Walk(self):
        self.x -= random.randint(4, 8)

    def R_Walk(self):
        self.x += random.randint(4, 8)
    
    def L_Dash(self):
        self.x -= random.randint(15, 25)
    
    def R_Dash(self):
        self.x += random.randint(15, 25) 
    
    def Jump(self):
        if self.jumps > 0:
            self.y += 30
            self.jumps -= 1

    def attack(self, enemy, x_range, y_range, damage_range, knockback_mult):
        if get_x_dist(self, enemy) < x_range and get_y_dist(self, enemy) < y_range:
            damage = random.randint(*damage_range)
            knockback = damage + (enemy.percent - damage) * knockback_mult
            return damage, knockback
        return None, None

    def L_Tilt(self, enemy):
        return self.attack(enemy, 8, 5, (8, 13), 1.5) * DAMAGE_SCALE

    def R_Tilt(self, enemy):
        return self.attack(enemy, 8, 5, (8, 13), 1.5) * DAMAGE_SCALE

    def U_Tilt(self, enemy):
        return self.attack(enemy, 5, 8, (8, 13), 1.5) * DAMAGE_SCALE

    def L_Smash(self, enemy):
        return self.attack(enemy, 8, 6 if self.y else 5, (10, 13) if self.y else (14, 17), 2) * DAMAGE_SCALE

    def R_Smash(self, enemy):
        return self.attack(enemy, 5, 6 if self.y else 5, (10, 13) if self.y else (14, 17), 2) * DAMAGE_SCALE

    def U_Smash(self, enemy):
        return self.attack(enemy, 5, 8, (10, 13) if self.y else (14, 17), 1.75) * DAMAGE_SCALE

    def D_Smash(self, enemy):
        return self.attack(enemy, 8, 5 if self.y else 3, (10, 13) if self.y else (14, 17), 1.75) * DAMAGE_SCALE

    def get_random_action(self):
        actions = [self.R_Dash, self.L_Dash, self.R_Walk, self.L_Walk, self.Jump,
                   self.L_Smash, self.R_Smash, self.D_Smash, self.U_Smash, self.L_Tilt, self.R_Tilt, self.U_Tilt]
        return random.choice(actions) 
       
def get_x_dist(agent, enemy_agent):
    return abs(agent.x - enemy_agent.x)

def get_y_dist(agent, enemy_agent):
    return abs(agent.y - enemy_agent.y)
    
def get_current_state(agent, enemy_agent):
    for state_num, data in state_data.items():
        state_info = data["State"]
        agent_x_in_range = state_info["Agent_X_Position"][0] <= agent.x < state_info["Agent_X_Position"][1]
        agent_y_in_range = state_info["Agent_Y_Position"][0] <= agent.y < state_info["Agent_Y_Position"][1]
        opponent_x_in_range = state_info["Opponent_X_Position"][0] <= enemy_agent.x < state_info["Opponent_X_Position"][1]
        opponent_y_in_range = state_info["Opponent_Y_Position"][0] <= enemy_agent.y < state_info["Opponent_Y_Position"][1]
        jumps_match = (agent.jumps > 0) == state_info["Jumps_Left"]

        if agent_x_in_range and agent_y_in_range and opponent_x_in_range and opponent_y_in_range and jumps_match:
            x_dist = get_x_dist(agent, enemy_agent)
            y_dist = get_y_dist(agent, enemy_agent)
            return state_num, (x_dist, y_dist, agent.x, agent.stocks, enemy_agent.stocks, agent.y, agent.percent, enemy_agent.percent)
    
    print("State not found")
    print(f'Agent x: {agent.x}, Agent y: {agent.y}')
    print(f'Agent Jumps: {agent.jumps}')
    print(f'Enemy x: {enemy_agent.x}, Enemy y: {enemy_agent.y}')
    return None

def softmax(x):
    return (np.exp(x) / np.sum(np.exp(x), axis=0)).tolist()

def get_action(state_num):
    actions = state_data[str(state_num)]["Actions"]
    probabilities = list(actions.values())
    softmaxed_probabilities = softmax(probabilities)
    most_likely = max(softmaxed_probabilities)
    action_index = softmaxed_probabilities.index(most_likely)
    best_action = list(actions)[action_index]

    return best_action    
            
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
        agent.damage_done += opp_percent_diff

    damage_taken = agent_percent_diff * damage_taken_weight
    damage_done = opp_percent_diff * damage_done_weight

    stock_lost = curr_agent_stocks < prev_agent_stocks
    stock_taken = curr_opp_stocks < prev_opp_stocks

    return distance_x, distance_y, damage_taken, damage_done, stock_lost, stock_taken 

def update_odds(agent, dist_x, dist_y, damage_taken, damage_done, actions, learning_rate=0.01):
    nothing_weight = 0.1
    for state_num, action_list in actions.items():
        for action in action_list:
            if action != "Release":
                if dist_x and action in ['L_Walk', 'R_Walk', 'L_Dash', 'R_Dash']:
                    state_data[state_num]["Actions"][action] -= dist_x * learning_rate
                    agent.performance -= dist_x * learning_rate
                if dist_y and action == 'Jump':
                    state_data[state_num]["Actions"][action] -= dist_y * learning_rate
                    agent.performance -= dist_y * learning_rate
                if damage_done and action in ATTACK_LIST:
                    state_data[state_num]["Actions"][action] -= damage_done * learning_rate
                    agent.performance  -= damage_done * learning_rate
                if damage_taken:
                    state_data[state_num]["Actions"][action] -= damage_taken * learning_rate
                    agent.performance -= damage_taken * learning_rate
                if not (dist_x or dist_y or damage_done) and action in ATTACK_LIST:
                    state_data[state_num]["Actions"][action] -= nothing_weight * learning_rate
                    agent.performance -= nothing_weight * learning_rate
                    # make movements more likely if nothing happened
                    for move_action in ['L_Dash', 'R_Dash', 'L_Walk', 'R_Walk', 'Jump']: 
                        state_data[state_num]["Actions"][move_action] += nothing_weight * learning_rate
                        agent.performance += nothing_weight * learning_rate

def update_odds_long(agent, stock_lost, stock_taken, actions_long, learning_rate=0.01):
    stock_weight = 0.15
    death_penalty = 0.05 * learning_rate
    sd_penalty = stock_weight * learning_rate
    if stock_lost:
        for state_num, action_list in actions_long.items():
            for action in action_list:
                if action != "Release":
                    state_data[state_num]["Actions"][action] += death_penalty
                    agent.performance += death_penalty
                    if action in ATTACK_LIST:
                        state_data[state_num]["Actions"][action] += sd_penalty
                        agent.performance += sd_penalty

    if stock_taken:
        for state_num, action_list in actions_long.items():
            for action in action_list:
                if action != "Release":
                    state_data[state_num]["Actions"][action] -= stock_weight * learning_rate
                    agent.performance -= stock_weight * learning_rate

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

def get_game_num():
    data = open(f"{CURRENT_DIR}/stats.json", "r")
    match_data = json.load(data)
    match_number = match_data["Current Match"]
    return match_number

def update_agent():
    with open(f"{CURRENT_DIR}/agent_data.json", "w") as json_file: 
        json.dump(state_data, json_file)
    print('saved agent data')

def step(enemy, action):
    if action.__name__ in ATTACK_LIST:
        damage, multiplier = action(enemy)
        if damage and multiplier:
            knockback_x = damage + ((enemy.percent - damage) * multiplier)
            knockback_y = damage + (enemy.percent / multiplier)
            enemy.percent += damage
            enemy.x += knockback_x
            enemy.y += knockback_y
    else:
        action()

def update_state(agent, enemy):
    
    # this can probably be improved a bit but if statements are fast anyways
    if agent.x >= -85 and agent.x <= 85: # on stage
        if agent.y > 0: # in air
            agent.y -= FALL_SPEED # falling
        
        if agent.y < 0: # don't want to decrement below 0 (if on stage)
            agent.y = 0 

        if agent.y == 0:
            agent.jumps = 2 # reset jumps

    elif agent.x < -85 or agent.x > 85: # offstage so must be falling
        agent.y -= FALL_SPEED
         
    # check for out of bounds
    if agent.x < LEFT_BORDER or agent.x > RIGHT_BORDER or agent.y < BOTTOM_BORDER or agent.y > TOP_BORDER:
        agent.stocks -= 1 
        agent.reset_on_death()

    if enemy.x >= -85 and enemy.x <= 85: # on stage
        if enemy.y > 0:
            enemy.y -= FALL_SPEED

        if enemy.y < 0:
            enemy.y = 0 

        if enemy.y == 0:
            enemy.jumps = 2

    elif enemy.x < -85 or enemy.x > 85: # offstage so must be falling
        enemy.y -= FALL_SPEED

    # check for out of bounds
    if enemy.x < LEFT_BORDER or enemy.x > RIGHT_BORDER or enemy.y < BOTTOM_BORDER or enemy.y > TOP_BORDER:
        enemy.stocks -= 1 
        enemy.reset_on_death()

def print_game(agent, enemy, agent_action, enemy_action, game_num):
    os.system('cls')
    agent_x, agent_y = agent.x, agent.y
    enemy_x, enemy_y = enemy.x, enemy.y
    width = 50
    height = 15
    
    scale_x = ((LEFT_BORDER * -1) + RIGHT_BORDER) / width
    scale_y = (TOP_BORDER + (BOTTOM_BORDER * -1)) / height
    
    game_array = [['.'] * width for _ in range(height)]
    
    ground_line = height * (BOTTOM_BORDER * -1) // ((BOTTOM_BORDER * -1) + TOP_BORDER)
    
    agent_x_scaled = int((agent_x + RIGHT_BORDER) / scale_x)
    agent_y_scaled = ground_line - int(agent_y / scale_y)
    enemy_x_scaled = int((enemy_x + RIGHT_BORDER) / scale_x)
    enemy_y_scaled = ground_line - int(enemy_y / scale_y)
    
    agent_x_scaled = max(0, min(agent_x_scaled, width - 1))
    agent_y_scaled = max(0, min(agent_y_scaled, height - 1))
    enemy_x_scaled = max(0, min(enemy_x_scaled, width - 1))
    enemy_y_scaled = max(0, min(enemy_y_scaled, height - 1))
        
    for i in range(width):
        original_x = i * scale_x - RIGHT_BORDER
        if -85 <= original_x <= 85:
            game_array[ground_line][i] = '_'

    game_array[agent_y_scaled][agent_x_scaled] = 'A'
    game_array[enemy_y_scaled][enemy_x_scaled] = 'E'

    for row in game_array:
        print("".join(row))

    print()
    print(f'Game: {game_num}')
    print()
    print('Agent') 
    print(f'Stocks: {agent.stocks}')
    print(f'Percentage: {agent.percent}%')
    print(f'Action: {agent_action}')
    print(f'Performance: {agent.performance}')
    print()
    print('Enemy Agent') 
    print(f'Stocks: {enemy.stocks}')
    print(f'Percentage: {enemy.percent}%')
    print(f'Action: {enemy_action}')
    print(f'Performance: {enemy.performance}')

def main(games, save_frequency, display):
    total_games = get_game_num()
    for i in range(games):
        print(f'Game: {total_games + i}')
        a1_performed_actions_long = set()
        a2_performed_actions_long = set()
        a1_actions_long = {}
        a2_actions_long = {}
        consecutive_same_state = 0
        prev_a1_state = None
        curr_a1_state = None
        prev_a2_state = None
        curr_a2_state = None

        agent = Agent(60)
        enemy_agent = Agent(-60)
        while agent.stocks > 0 and enemy_agent.stocks > 0:
            # print(f'XY: ({agent.x}, {agent.y})\nDamage: {agent.damage_done}\nStocks: {agent.stocks}\n')
            a1_performed_actions = set()
            a2_performed_actions = set()

            a1_actions = {}
            a2_actions = {}

            a1_state_num, curr_a1_state  = get_current_state(agent, enemy_agent)
            a2_state_num, curr_a2_state  = get_current_state(enemy_agent, agent)
            
            if consecutive_same_state < 2:
                a1_action = get_action(a1_state_num)
                a1_action_func = getattr(agent, a1_action, None)

                a2_action = get_action(a2_state_num)
                a2_action_func = getattr(enemy_agent, a2_action, None)
            else: # if stuck in same state, do random action
                a1_action_func = agent.get_random_action() 
                a2_action_func = enemy_agent.get_random_action()
            if display:
                print_game(agent, enemy_agent, a1_action, a2_action, total_games + i)

            # Update actions and state dictionary
            a1_performed_actions.add(a1_action)
            a2_performed_actions.add(a2_action)
            
            a1_performed_actions_long.add(a1_action)
            a2_performed_actions_long.add(a2_action)

            a1_actions.update({a1_state_num: a1_performed_actions})
            a2_actions.update({a2_state_num: a2_performed_actions})

            a1_actions_long.update({a1_state_num: a1_performed_actions_long})
            a2_actions_long.update({a2_state_num: a2_performed_actions_long})

            # Do action

            update_state(agent, enemy_agent)
            step(enemy=enemy_agent, action=a1_action_func)
            step(enemy=agent, action=a2_action_func)

            # check if previous states exist
            if prev_a1_state and prev_a2_state:
                if prev_a1_state == curr_a1_state: # check if they are the same
                    consecutive_same_state += 1 
                else: 
                    consecutive_same_state = 0
            
                a1_distance_x, a1_distance_y, a1_damage_taken, a1_damage_done, a1_stock_lost, a1_stock_taken = calculate_rewards(prev_a1_state, curr_a1_state, agent)
                update_odds(agent, a1_distance_x, a1_distance_y, a1_damage_taken, a1_damage_done, a1_actions)
                
                # Reset short term actions list
                a1_performed_actions = set()
                a1_actions = {}

                # Update odds with longer context
                # Reset the long term actions list when stocks change
                if a1_stock_lost or a1_stock_taken: 
                    update_odds_long(agent, a1_stock_lost, a1_stock_taken, a1_actions_long)                
                    a1_performed_actions_long = set()
                    a1_actions_long = {}    
                
                a2_distance_x, a2_distance_y, a2_damage_taken, a2_damage_done, a2_stock_lost, a2_stock_taken = calculate_rewards(prev_a2_state, curr_a2_state, enemy_agent)
                update_odds(enemy_agent, a2_distance_x, a2_distance_y, a2_damage_taken, a2_damage_done, a2_actions)
                a2_performed_actions = set()
                a2_actions = {}

                if a2_stock_lost or a2_stock_taken:
                    update_odds_long(enemy_agent, a2_stock_lost, a2_stock_taken, a2_actions_long)
                    a2_performed_actions_long = set()
                    a2_actions_long = {}
            
            prev_a1_state = curr_a1_state
            prev_a2_state = curr_a2_state
        average_damage = round((agent.damage_done + enemy_agent.damage_done) / 2, 2)
        average_performance = round((agent.performance + enemy_agent.performance) / 2, 2)
        record_results(average_performance, average_damage)
        agent.reset_on_death()
        enemy_agent.reset_on_death()
        if (i + total_games) % save_frequency == 0:
            update_agent()
    
    update_agent()

main(games=50000, save_frequency=10, display=False)
"""
Try softmax to convert all probabilities to some value between 0 and 1 and perform the highest value

unoptimized time to run 50 games: 0:07:15.030954
optimized time to run 50 games: 0:03:02.229954
time to run 50 games with prints: 0:07:28.968943
Implement evolutionary reinforcement learning by summing the q-values each game, returning the total q-values
and the changes it made after a game.
Changes might look like: 
{
    "State_Num": 1,
    "Changes": {"L_Walk": 0.2, "U_Tilt": 0.02}
}
Maybe also add a way to visualize what is happening in each game to see how accurrate it is
Then multiple games on different threads and see which had the highest q-values or which played the best.  
Take the changes of the one that played the best and apply it to the agent_data file.
Could also slightly modify all probabilities in the data at the start of each game for the mutation aspect. 
"""