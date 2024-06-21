import json
import random
import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ATTACK_LIST = ['L_Tilt', 'R_Tilt', 'U_Tilt', 'D_Tilt', 'L_Smash', 'R_Smash', 'U_Smash', 'D_Smash', 'Jab']
json_file = open(f"{CURRENT_DIR}/agent_data.json", "r")
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
        self.initial_X = start_X

    def reset_after_game(self):
        self.x = self.initial_X 
        self.y = 0
        self.stocks = 4
        self.percent = 0
        self.damage_done = 0
        self.jumps = 2
    
    def reset_on_death(self):
        self.x = self.initial_X
        self.y = 0
        self.percent = 0
        self.jumps = 2

    def is_offstage(self):
        if self.x < -85 or self.x > 85: 
            return True
        else:
            return False

    # random values to introduce more variance in states
    def L_Walk(self):
        self.x -= random.randint(6, 12)

    def R_Walk(self):
        self.x += random.randint(6, 12)
    
    def L_Dash(self):
        self.x -= random.randint(25, 34)
    
    def R_Dash(self):
        self.x += random.randint(25, 34) 
    
    def Jump(self):
        if self.jumps > 0:
            self.y += 30
            self.jumps -= 1
            
    def L_Tilt(self, enemy):
        if enemy.x < self.x and get_x_dist(self, enemy) < 5 and get_y_dist(self, enemy) < 3:
            return random.randint(8,13), 2 # damage, knockback
        return None, None
    
    def R_Tilt(self, enemy):
        if enemy.x > self.x and get_x_dist(self, enemy) < 5 and get_y_dist(self, enemy) < 3:
            return random.randint(8,13), 2 # damage, knockback
        return None, None

    def U_Tilt(self, enemy):
        if get_x_dist(self, enemy) < 3 or get_y_dist(self, enemy) < 5 and enemy.y > self.y: # close x or y and above
            return random.randint(8,13), 2 # damage, knockback
        return None, None

    def L_Smash(self, enemy):
        if self.y != 0: # in air
            if enemy.x < self.x and get_x_dist(self, enemy) < 5 and get_y_dist(self, enemy) < 4: # close x or y and not too far or low
                return random.randint(10,13), 2 # damage, knockback
            
        else: # on ground
            if enemy.x < self.x and get_x_dist(self, enemy) < 7 and get_y_dist(self, enemy) < 4: # close x or y and not too far or low
                return random.randint(14,17), 2.25 # damage, knockback
        return None, None

    def R_Smash(self, enemy):
        if self.y != 0: # in air
            if enemy.x > self.x and get_x_dist(self, enemy) < 5 and get_y_dist(self, enemy) < 3 and get_y_dist(self, enemy) < 4:
                return random.randint(10,13), 2 # damage, knockback
            
        else: # on ground
            if enemy.x > self.x and get_x_dist(self, enemy) < 7 and get_y_dist(self, enemy) < 3 and get_y_dist(self, enemy) < 4:
                return random.randint(14,17), 2.25 # damage, knockback
        return None, None

    def U_Smash(self, enemy):
        if self.y != 0:
            if get_x_dist(self, enemy) < 5 or get_y_dist(self, enemy) < 5 and enemy.y > self.y: # close x or y and above
                return random.randint(10,13), 2 # damage, knockback
        else:
            if get_x_dist(self, enemy) < 3 or get_y_dist(self, enemy) < 6 and enemy.y > self.y: 
                return random.randint(14,17), 2.25 # damage, knockback
        return None, None

    def D_Smash(self, enemy):
        if self.y != 0:
            if get_x_dist(self, enemy) < 5 or get_y_dist(self, enemy) < 5 and enemy.y < self.y: # close x or y and below 
                return random.randint(10,13), 2 # damage, knockback
        else: 
            if get_x_dist(self, enemy) < 5 and enemy.y == 0: # close and enemy also grounded
                return random.randint(14,17), 2.25 # damage, knockback
        return None, None
        
    def get_random_action(self):
        actions = [self.R_Dash, self.L_Dash, self.R_Walk, self.L_Walk, self.Jump,
                    self.L_Smash, self.R_Smash, self.D_Smash, self.U_Smash, self.L_Tilt, self.R_Tilt, self.U_Tilt]
        return actions[random.randint(0, len(actions) - 1)]
    
def get_x_dist(agent, enemy_agent):
    agent_x = agent.x
    opp_x = enemy_agent.x
    return abs(agent_x - opp_x)

def get_y_dist(agent, enemy_agent):
    agent_y = agent.y
    opp_y = enemy_agent.y
    return abs(agent_y - opp_y)

def get_current_state(agent, enemy_agent):
    for state_num, data in state_data.items():
        state_info = data["State"]
        agent_stocks = agent.stocks
        opp_stocks = enemy_agent.stocks
        agent_percent = agent.percent
        opp_percent = enemy_agent.percent
        x_pos = agent.x
        y_pos = agent.y
        x_dist = get_x_dist(agent, enemy_agent)
        y_dist = get_y_dist(agent, enemy_agent)
        if (
            agent.x >= state_info["Agent_X_Position"][0] and agent.x <= state_info["Agent_X_Position"][1] and
            agent.y >= state_info["Agent_Y_Position"][0] and agent.y <= state_info["Agent_Y_Position"][1] and
            enemy_agent.x >= state_info["Opponent_X_Position"][0] and enemy_agent.x <= state_info["Opponent_X_Position"][1] and
            enemy_agent.y >= state_info["Opponent_Y_Position"][0] and enemy_agent.y <= state_info["Opponent_Y_Position"][1] and
            (agent.jumps > 0) == state_info["Jumps_Left"] 
        ):
            return state_num, (x_dist, y_dist, x_pos, agent_stocks, opp_stocks, y_pos, agent_percent, opp_percent)
        
    print("State not found")
    print(f'Agent: {(agent.x, agent.y)}')
    print(f'Enemy Agent: {(enemy_agent.x, enemy_agent.y)}')
    return None 

def get_action(state_num):
    actions = state_data[str(state_num)]["Actions"]
    # Normalize action probabilities to be non-negative
    min_prob = min(actions.values())
    if min_prob < 0:
        actions = {action: prob - min_prob for action, prob in actions.items()}

    total_prob = sum(actions.values())
    # Normalize the probabilities to sum to 1
    actions = {action: prob / total_prob for action, prob in actions.items()}
    state_data[str(state_num)]["Actions"] = actions

    rand_num = random.uniform(0, 1)
    cumulative_prob = 0
    for action, prob in actions.items():
        cumulative_prob += prob
        if rand_num <= cumulative_prob:
            return action

def calculate_rewards(prev_state, curr_state, agent):
    curr_x_dist, curr_y_dist, curr_x_pos, curr_agent_stocks, curr_opp_stocks, curr_y_pos, curr_agent_percent, curr_opp_percent = curr_state[0], curr_state[1], curr_state[2], curr_state[3], curr_state[4], curr_state[5], curr_state[6], curr_state[7]
    prev_x_dist, prev_y_dist, prev_x_pos, prev_agent_stocks, prev_opp_stocks, prev_y_pos, prev_agent_percent, prev_opp_percent = prev_state[0], prev_state[1], prev_state[2], prev_state[3], prev_state[4], prev_state[5], prev_state[6], prev_state[7]

    # weights subject to change
    damage_taken_weight = 0.15
    damage_done_weight = 0.08
    
    distance_x = 0
    distance_y = 0
    distance_weight = 0.01

    # X/Y Position 
    if abs(curr_x_pos - prev_x_pos) > 5 and curr_x_dist < prev_x_dist: # don't want to include the opponent's movement
        distance_x = (prev_x_dist - curr_x_dist) * distance_weight
    if abs(curr_y_pos - prev_y_pos) > 5 and curr_y_dist < prev_y_dist:
        distance_y = (prev_y_dist - curr_y_dist) * distance_weight

    # Percentages
    agent_percent_diff = curr_agent_percent - prev_agent_percent # Damage taken 
    opp_percent_diff = curr_opp_percent - prev_opp_percent 
    if opp_percent_diff > 0:
        agent.damage_done += opp_percent_diff

    damage_taken = agent_percent_diff * damage_taken_weight
    damage_done = opp_percent_diff * damage_done_weight

    # Stocks
    stock_lost = False
    stock_taken = False
    if curr_agent_stocks < prev_agent_stocks: stock_lost = True
    if curr_opp_stocks < prev_opp_stocks: stock_taken = True

    return distance_x, distance_y, damage_taken, damage_done, stock_lost, stock_taken 

def update_odds(dist_x, dist_y, damage_taken, damage_done, actions, learning_rate=0.01):
    nothing_weight = 0.2
    for state_num, action_list in actions.items():  # Iterate over state numbers and associated actions
        for action in action_list:  # Iterate over actions for each state
            if action != "Release":
                # Distance (x)
                if dist_x != 0:
                    if action == 'L_Walk' or action == 'R_Walk' or action == 'L_Dash' or action == 'R_Dash':
                        scaled_change = dist_x * learning_rate
                        # print(f'Distance X: {action} of state #{state_num}: changed by {scaled_change}')
                        state_data[state_num]["Actions"][action] -= scaled_change
                # Distance (y)
                if dist_y != 0:
                    if action == 'Jump':
                        scaled_change = dist_y * learning_rate
                        state_data[state_num]["Actions"][action] -= scaled_change
                        # print(f'Distance Y: {action} of state #{state_num}: changed by {scaled_change}')
                # Damage done
                if damage_done != 0:
                    if action in ATTACK_LIST:
                        scaled_change = damage_done * learning_rate
                        state_data[state_num]["Actions"][action] -= scaled_change
                        # print(f'{action} of state #{state_num}: changed by {scaled_change}')
                        # print(f'Damage Done: {action} of state #{state_num}: changed by {scaled_change}')
                # Damage taken
                # if damage_taken != 0:
                #     scaled_change = damage_taken * learning_rate
                #     state_data[state_num]["Actions"][action] -= scaled_change
                #     print(f'{action} of state #{state_num}: changed by {scaled_change}')
                #     print(f'Damage Taken: {action} of state #{state_num}: changed by {scaled_change}')

                if dist_x == 0 and dist_y == 0 and damage_done == 0: # if nothing happened
                    if action in ATTACK_LIST:
                        scaled_change = nothing_weight * learning_rate
                        state_data[state_num]["Actions"][action] -= scaled_change # make it less likely

                        # Make movements more likely
                        state_data[state_num]["Actions"]['L_Dash'] += scaled_change
                        state_data[state_num]["Actions"]['R_Dash'] += scaled_change
                        state_data[state_num]["Actions"]['L_Walk'] += scaled_change
                        state_data[state_num]["Actions"]['R_Walk'] += scaled_change
                        state_data[state_num]["Actions"]['Jump'] += scaled_change

                        # print(f'Nothing Changed: {action} changed by -{scaled_change}')
                        # print(f'Nothing Changed: Movements changed by {scaled_change}')

def update_odds_long(stock_lost, stock_taken, actions_long, learning_rate=0.1):
    # Stocks
    stock_weight = 0.15
    death_penalty = 0.05 * learning_rate
    sd_penalty = stock_weight * learning_rate
    if stock_lost:
        for state_num, action_list in actions_long.items():
            for action in action_list:  
                if action != 'Jump': # excluding jumps since most deaths are from sding and jumps would help prevent that
                    state_data[state_num]["Actions"][action] -= (death_penalty)
                    # print(f'{action} of state #{state_num}: changed by -{death_penalty}')

                if action == 'L_Walk' or action == 'R_Walk' or action == 'L_Dash' or action == 'R_Dash':
                    state_data[state_num]["Actions"][action] -= (sd_penalty)
                    # print(f'{action} of state #{state_num}: changed by -{sd_penalty}')
            # if stock_taken:
            #     state_data[state_num]["Actions"][action] += (sd_penalty)
            #     print(f'{action} of state #{state_num}: changed by -{sd_penalty}')
            
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

def update_agent():
    with open(f"{CURRENT_DIR}/agent_data.json", "w") as json_file: 
        json.dump(state_data, json_file, indent=4)
    print('updated agent')


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
    if agent.x >= -85 and agent.x <= 85: # on stage
        if agent.y > 0: # in air
            agent.x -= 5 # falling
        
        if agent.x < 0: # don't want to decrement below 0
            agent.x = 0 

        if agent.x == 0:
            agent.jumps = 2 # reset jumps

    elif agent.x < -85 or agent.x > 85: # offstage so must be falling
        agent.x -= 5
         
    # check for out of bounds
    if agent.x < -250 or agent.x > 250 or agent.y < -140 or agent.y > 190:
        agent.stocks -= 1 
        agent.reset_on_death()

    if enemy.x >= -85 and enemy.x <= 85 and enemy.y > 0: # on stage, in air
        enemy.x -= 5
        if enemy.x < 0: enemy.x = 0 # don't want to decrement below 0

    elif enemy.x < -85 or enemy.x > 85: # offstage so must be falling
        enemy.x -= 5 

    # check for out of bounds
    if enemy.x < -250 or enemy.x > 250 or enemy.y < -140 or enemy.y > 190:
        enemy.stocks -= 1 
        enemy.reset_on_death()

def main(games, save_frequency):
    game_num = 0
    for i in range(games):
        print(f'Game: {i}')
        game_num += 1
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

            # Update actions and state dictionary
            a1_performed_actions.add(a1_action)
            a2_performed_actions.add(a2_action)
            
            a1_performed_actions_long.add(a1_action)
            a2_performed_actions_long.add(a2_action)

            a1_actions.update({a1_state_num: a1_performed_actions})
            a2_actions.update({a2_state_num: a2_performed_actions})

            a1_actions_long.update({a1_state_num: a1_performed_actions_long})
            a2_actions_long.update({a2_state_num: a2_performed_actions_long})

            # Do action here

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
                
                a2_distance_x, a2_distance_y, a2_damage_taken, a2_damage_done, a2_stock_lost, a2_stock_taken = calculate_rewards(prev_a2_state, curr_a2_state, enemy_agent)
                update_odds(a2_distance_x, a2_distance_y, a2_damage_taken, a2_damage_done, a2_actions)
                a2_performed_actions = set()
                a2_actions = {}

                if a2_stock_lost or a2_stock_taken:
                    update_odds_long(a2_stock_lost, a2_stock_taken, a2_actions_long)
                    a2_performed_actions_long = set()
                    a2_actions_long = {}
            
            prev_a1_state = curr_a1_state
            prev_a2_state = curr_a2_state
            
        record_results((agent.damage_done + enemy_agent.damage_done) // 2)
        agent.reset_on_death()
        enemy_agent.reset_on_death()
        if game_num == save_frequency:
            update_agent()
            game_num = 0
    
    update_agent()

main(games=50000, save_frequency=75)