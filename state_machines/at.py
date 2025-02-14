from functions import *
import random

"""
- Consecutive input support
- Recovering requires a release of inputs then up special
- Inputs need to be released after the move finishes to prevent "misinputs"
- Sticking with a single gimmick might be easier (Jigglypuff rest)

"""
class atBot:
    def __init__(self, port: int, opp_port: int, controller: melee.Controller, close_dist=5, mid_dist=15, far_dist=5000, close_air_dist=5, mid_range_air_dist=15, far_air_dist=50):
        self.port = port
        self.opp_port = opp_port 
        self.controller = controller
        
        self.x = 0
        self.y = 0
        self.count = 0

        self.close = False
        self.mid_range = False
        self.far = False
        self.close_air = False
        self.mid_range_air = False
        self.far_air = False
        self.enemy_left = False

        self.close_dist = close_dist
        self.mid_dist = mid_dist
        self.far_dist = far_dist
        self.close_air_dist = close_air_dist
        self.mid_range_air_dist = mid_range_air_dist
        self.far_air_dist = far_air_dist

    def calculate_states(self, game: melee.GameState):
        if self.count > 2: self.count = 0
        agent_x = game.players[self.port].position.x
        opp_x = game.players[self.opp_port].position.x
        agent_y = game.players[self.port].position.y
        opp_y = game.players[self.opp_port].position.y
        
        self.x = agent_x
        self.y = agent_y
        
        diff_x = abs(agent_x - opp_x)
        diff_y = abs(agent_y - opp_y)

        self.close = diff_x <= self.close_dist 
        self.mid_range = self.close_dist < diff_x < self.mid_dist
        self.far = self.mid_dist < diff_x < self.far_dist

        self.close_air = diff_y <= self.close_air_dist
        self.mid_range_air = self.close_air_dist < diff_y < self.mid_range_air_dist
        self.far_air = self.mid_range_air_dist < diff_y < self.far_air_dist
        self.enemy_left = opp_x < agent_x
        self.count += 1

    def move(self, game: melee.GameState):
        # off stage
        if game.players[self.port].off_stage:
            if self.x > 0: # right side off stage
                Release(self.controller)
                Jump(self.controller)
                L_Walk(self.controller)

            elif self.x < 0: # left side off stage
                Release(self.controller)
                Jump(self.controller)
                R_Walk(self.controller)

        if game.players[self.opp_port].off_stage:
            Release(self.controller)
            return
        
        # on stage
        else:
            # close range
            if self.close and self.enemy_left:
                r = random.randint(0, 2)
                if r == 0:
                    L_Tilt(self.controller)
                elif r == 1:
                    L_Smash(self.controller)
                else:
                    D_Special(self.controller)

            elif self.close and not self.enemy_left:
                r = random.randint(0, 2)
                if r == 0:
                    R_Tilt(self.controller)
                elif r == 1:
                    R_Smash(self.controller)
                else:
                    D_Special(self.controller)

            # mid range
            if self.mid_range and self.enemy_left:
                r = random.randint(0, 4)
                if r == 0:
                    L_Dash(self.controller)
                elif r == 1:
                    L_Walk(self.controller)
                elif r == 2:
                    Jump(self.controller)
                elif r == 3:
                    R_Dash(self.controller)
                else:
                    # roll
                    Shield(self.controller)
                    L_Dash(self.controller)
            
            elif self.mid_range and not self.enemy_left:
                r = random.randint(0, 4)
                if r == 0:
                    R_Dash(self.controller)
                elif r == 1:
                    R_Walk(self.controller)
                elif r == 2:
                    Jump(self.controller)
                elif r == 3:
                    L_Dash(self.controller)
                else:
                    # roll
                    Shield(self.controller)
                    R_Dash(self.controller)
            
            # far range
            if self.far and self.enemy_left:
                L_Dash(self.controller)
            elif self.far and not self.enemy_left:
                R_Dash(self.controller)

        if self.count == 2:
            Release(self.controller)