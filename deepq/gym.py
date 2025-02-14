import json
import random
import os
import numpy as np
from typing import Tuple, List, Dict, Any, Optional, Callable

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ATTACK_LIST = ['L_Tilt', 'R_Tilt', 'U_Tilt', 'D_Tilt', 'L_Smash', 'R_Smash', 'U_Smash', 'D_Smash', 'Jab']
LEFT_BORDER = -225
RIGHT_BORDER = 225
TOP_BORDER = 200
BOTTOM_BORDER = -110
FALL_SPEED = 10
DAMAGE_SCALE = 2.5

class Agent:
    def __init__(self, start_X: float):
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
        if abs(self.x - enemy.x) <x_range and abs(self.y - enemy.y) <y_range:
            damage = random.randint(*damage_range)
            knockback = damage + (enemy.percent - damage) * knockback_mult
            return damage, knockback
        return None, None

    def L_Tilt(self, enemy):
        return self.attack(enemy, 8, 5, (8, 13), 1.25) 
    def R_Tilt(self, enemy):
        return self.attack(enemy, 8, 5, (8, 13), 1.25) 
    def U_Tilt(self, enemy):
        return self.attack(enemy, 5, 8, (8, 13), 1.25) 
    def D_Tilt(self, enemy):
        return self.attack(enemy, 5, 3, (8, 13), 1.25)
    def L_Smash(self, enemy):
        return self.attack(enemy, 8, 6 if self.y else 5, (10, 13) if self.y else (14, 17), 1.5) 
    def R_Smash(self, enemy):
        return self.attack(enemy, 5, 6 if self.y else 5, (10, 13) if self.y else (14, 17), 1.5) 
    def U_Smash(self, enemy):
        return self.attack(enemy, 5, 8, (10, 13) if self.y else (14, 17), 1.35) 
    def D_Smash(self, enemy):
        return self.attack(enemy, 8, 5 if self.y else 3, (10, 13) if self.y else (14, 17), 1.35)
    def Jab(self, enemy):
        return self.attack(enemy, 6, 4, (5, 8), 1.0)

    def get_possible_actions(self):
        actions = [self.R_Dash, self.L_Dash, self.R_Walk, self.L_Walk, self.Jump,
                   self.L_Smash, self.R_Smash, self.D_Smash, self.U_Smash, 
                   self.L_Tilt, self.R_Tilt, self.U_Tilt, self.D_Tilt, self.Jab]
        return {action.__name__: action for action in actions}

class SmashEnv:
    def __init__(self):
        self.agent = Agent(-50)
        self.enemy_agent = Agent(50)
        self.game_number = 1
        self.prev_state = None
        self.max_steps = 1000
        self.current_step = 0
        self.action_space = self.agent.get_possible_actions()
        self.action_space_n = len(self.action_space)
        self.observation_space_n = 8  # x_dist, y_dist, x_pos, agent_stocks, enemy_stocks, y_pos, agent_percent, enemy_percent
        
    def reset(self) -> np.ndarray:
        self.agent.reset_after_game()
        self.enemy_agent.reset_after_game()
        self.game_number += 1
        self.current_step = 0
        
        x_dist = abs(self.agent.x - self.enemy_agent.x)
        y_dist = abs(self.agent.y - self.enemy_agent.y)
        state = np.array([
            x_dist, y_dist, self.agent.x, self.agent.stocks, 
            self.enemy_agent.stocks, self.agent.y, self.agent.percent, self.enemy_agent.percent
        ], dtype=np.float32)
        self.prev_state = state
        return state
    
    def get_state(self) -> np.ndarray:
        x_dist = abs(self.agent.x - self.enemy_agent.x)
        y_dist = abs(self.agent.y - self.enemy_agent.y)
        return np.array([
            x_dist, y_dist, self.agent.x, self.agent.stocks, 
            self.enemy_agent.stocks, self.agent.y, self.agent.percent, self.enemy_agent.percent
        ], dtype=np.float32)
    
    def enemy_act(self):
        # Simple heuristic for enemy
        # If far, approach. If close, attack.
        x_dist = abs(self.agent.x - self.enemy_agent.x)
        y_dist = abs(self.agent.y - self.enemy_agent.y)
        
        if self.enemy_agent.is_offstage():
            if self.enemy_agent.x <-85:
                self.enemy_agent.R_Dash()
            else:
                self.enemy_agent.L_Dash()
            if self.enemy_agent.y < 0 and self.enemy_agent.jumps > 0:
                self.enemy_agent.Jump()
        elif x_dist > 20:
            if self.enemy_agent.x < self.agent.x:
                self.enemy_agent.R_Dash()
            else:
                self.enemy_agent.L_Dash()
        elif x_dist <= 20 and y_dist <= 10:
            attack_options = [
                self.enemy_agent.L_Tilt, self.enemy_agent.R_Tilt, 
                self.enemy_agent.U_Tilt, self.enemy_agent.D_Tilt,
                self.enemy_agent.L_Smash, self.enemy_agent.R_Smash, 
                self.enemy_agent.U_Smash, self.enemy_agent.D_Smash, 
                self.enemy_agent.Jab
            ]
            attack = random.choice(attack_options)
            damage, _ = attack(self.agent)
            if damage:
                self.agent.percent += damage
                self.enemy_agent.damage_done += damage
        else:
            if random.random() < 0.3:
                self.enemy_agent.Jump()
            elif self.enemy_agent.x < self.agent.x:
                self.enemy_agent.R_Walk()
            else:
                self.enemy_agent.L_Walk()
        
        # Update position and state after enemy's action
        self.update_state()
        
    def step(self, action_name: str) -> Tuple[np.ndarray, float, bool, Dict]:
        self.current_step += 1
        action = self.action_space.get(action_name)
        
        prev_state = self.get_state()
        
        # Execute player action
        if action_name in ATTACK_LIST:
            damage, multiplier = action(self.enemy_agent)
            if damage and multiplier:
                knockback_x = multiplier * (damage / 10) * (1 + self.enemy_agent.percent / 100)
                knockback_y = (damage / 10) * (1 + self.enemy_agent.percent / 100)
                
                if "L_" in action_name:
                    self.enemy_agent.x -= knockback_x
                elif "R_" in action_name:
                    self.enemy_agent.x += knockback_x
                
                if "U_" in action_name:
                    self.enemy_agent.y += knockback_y
                elif "D_" in action_name:
                    self.enemy_agent.y -= knockback_y / 2  # Less downward knockback
                
                self.enemy_agent.percent += damage
        else:
            action()
        
        # Update after player action
        self.update_state()
        
        # Do enemy actions
        self.enemy_act()
        
        # Get new state and calculate reward
        new_state = self.get_state()
        reward = self.calculate_reward(prev_state, new_state)

        done = (self.agent.stocks <= 0 or 
                self.enemy_agent.stocks <= 0 or 
                self.current_step >= self.max_steps)
        
        info = {
            "agent_stocks": self.agent.stocks,
            "enemy_stocks": self.enemy_agent.stocks,
            "agent_percent": self.agent.percent,
            "enemy_percent": self.enemy_agent.percent,
            "step": self.current_step
        }
        
        if done:
            if self.agent.stocks > self.enemy_agent.stocks:
                reward += 100  # Big reward for winning
            elif self.agent.stocks < self.enemy_agent.stocks:
                reward -= 100  # Big penalty for losing

            self.save_stats(reward, self.enemy_agent.damage_done)
        
        return new_state, reward, done, info
        
    def update_state(self):
        if self.agent.x >= -85 and self.agent.x <= 85:  # on stage
            if self.agent.y > 0:  # in air
                self.agent.y -= FALL_SPEED  # falling
            
            if self.agent.y < 0:  # don't want to decrement below 0 (if on stage)
                self.agent.y = 0 

            if self.agent.y == 0:
                self.agent.jumps = 2  # reset jumps

        elif self.agent.x < -85 or self.agent.x > 85:  # offstage
            self.agent.y -= FALL_SPEED
            
        # Check for agent out of bounds
        if (self.agent.x < LEFT_BORDER or self.agent.x > RIGHT_BORDER or 
            self.agent.y < BOTTOM_BORDER or self.agent.y > TOP_BORDER):
            self.agent.stocks -= 1 
            self.agent.reset_on_death()

        # Update enemy
        if self.enemy_agent.x >= -85 and self.enemy_agent.x <= 85:  # on stage
            if self.enemy_agent.y > 0:
                self.enemy_agent.y -= FALL_SPEED

            if self.enemy_agent.y <0:
                self.enemy_agent.y = 0 

            if self.enemy_agent.y == 0:
                self.enemy_agent.jumps = 2

        elif self.enemy_agent.x < -85 or self.enemy_agent.x > 85:  # offstage
            self.enemy_agent.y -= FALL_SPEED

        # Check for enemy out of bounds
        if (self.enemy_agent.x <LEFT_BORDER or self.enemy_agent.x > RIGHT_BORDER or 
            self.enemy_agent.y <BOTTOM_BORDER or self.enemy_agent.y > TOP_BORDER):
            self.enemy_agent.stocks -= 1 
            self.enemy_agent.reset_on_death()
        
    def calculate_reward(self, prev_state, curr_state) -> float:
        prev_x_dist, prev_y_dist, prev_x_pos, prev_agent_stocks, prev_enemy_stocks, prev_y_pos, prev_agent_percent, prev_enemy_percent = prev_state
        curr_x_dist, curr_y_dist, curr_x_pos, curr_agent_stocks, curr_enemy_stocks, curr_y_pos, curr_agent_percent, curr_enemy_percent = curr_state

        reward = 0.0
        
        # Reward for getting closer to enemy
        if curr_x_dist < prev_x_dist:
            reward += 0.1
        
        # Reward for dealing damage
        damage_dealt = curr_enemy_percent - prev_enemy_percent
        if damage_dealt > 0:
            reward += damage_dealt * 0.5
        
        # Penalty for taking damage
        damage_taken = curr_agent_percent - prev_agent_percent
        if damage_taken > 0:
            reward -= damage_taken * 0.7
        
        # Big reward/penalty for stocks
        stocks_gained = curr_enemy_stocks <prev_enemy_stocks
        if stocks_gained:
            reward += 50
        
        stocks_lost = curr_agent_stocks < prev_agent_stocks
        if stocks_lost:
            reward -= 50
        
        # Penalty for being off-stage
        if self.agent.is_offstage():
            reward -= 1.0
        
        # Reward for forcing enemy off-stage
        if self.enemy_agent.is_offstage():
            reward += 0.5
        
        # Penalty for doing nothing
        if (curr_x_pos == prev_x_pos and curr_y_pos == prev_y_pos and 
            damage_dealt == 0 and not self.agent.is_offstage()):
            reward -= 0.1
        
        return reward
    
    def save_stats(self, score, damage_done):
        data = open(f"{CURRENT_DIR}/stats.json", "r")
        match_data = json.load(data)
        match_number = match_data["Current Match"]
        match_data["Matches"].append({
            "Match Number": match_number,
            "Performance": float(score),
            "Damage Done": float(damage_done)
        })

        match_data["Current Match"] += 1
        data.close()

        with open(f"{CURRENT_DIR}/stats.json", "w") as fh:
            json.dump(match_data, fh) 

    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        agent = self.agent
        enemy = self.enemy_agent
        
        width = 50
        height = 15
        
        scale_x = ((LEFT_BORDER * -1) + RIGHT_BORDER) / width
        scale_y = (TOP_BORDER + (BOTTOM_BORDER * -1)) / height
        
        game_array = [['.'] * width for _ in range(height)]
        
        ground_line = height * (BOTTOM_BORDER * -1) // ((BOTTOM_BORDER * -1) + TOP_BORDER)
        
        agent_x_scaled = int((agent.x + RIGHT_BORDER) / scale_x)
        agent_y_scaled = ground_line - int(agent.y / scale_y)
        enemy_x_scaled = int((enemy.x + RIGHT_BORDER) / scale_x)
        enemy_y_scaled = ground_line - int(enemy.y / scale_y)
        
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
        print(f'Game: {self.game_number}')
        print()
        print('Agent') 
        print(f'Stocks: {agent.stocks}')
        print(f'Percentage: {agent.percent}%')
        print(f'Performance: {agent.performance}')
        print()
        print('Enemy Agent') 
        print(f'Stocks: {enemy.stocks}')
        print(f'Percentage: {enemy.percent}%')
        print(f'Performance: {enemy.performance}')