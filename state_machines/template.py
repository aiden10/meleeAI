from functions import *

"""
Class containing some state values and decision making logic. 
"""
class Bot:
    def __init__(self, port: int, controller: melee.Controller, close_dist=5, mid_dist=15, far_dist=50, close_air_dist=5, mid_range_air_dist=15, far_air_dist=50):
        self.port = port
        self.controller = controller
        
        self.x = 0
        self.y = 0

        self.close = False
        self.mid_range = False
        self.far = False
        self.close_air = False
        self.mid_range_air = False
        self.far_air = False

        self.close_dist = close_dist
        self.mid_dist = mid_dist
        self.far_dist = far_dist
        self.close_air_dist = close_air_dist
        self.mid_range_air_dist = mid_range_air_dist
        self.far_air_dist = far_air_dist

    """
    Function for updating state values. Called every frame/step.
    """
    def calculate_states(self, game: melee.GameState, opp_port: int):
        agent_x = game.players[self.port].position.x
        opp_x = game.players[opp_port].position.x
        agent_y = game.players[self.port].position.y
        opp_y = game.players[opp_port].position.y
        
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

    """
    Main function for handling decision making for moves. Called every frame/step.
    """
    def move(self, game: melee.GameState):
        # action logic here
        pass            
