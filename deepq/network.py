"""
Create a neural network which will take in a state and output the estimated q-values for each action.
It may not even be necessary to fully understand neural networks if I can just use a library to handle all that for me.
And hopefully I'll understand them more after I do it with that and am forced to tweak things. 
I'd also like to try other "rules" to improve it. Moving towards the enemy and doing damage probably won't be able to lead to very 
good actual in-game performance? If the melee library has some way of running the game in headless mode that'd be useful too.

Actions:
    Previously, I simplified the action space to only basic movements and attacks but this time I'd like to try and
    incorporate grabs, rolls, specials, and shielding. These extra actions are going to also make the training time longer though
    since it'll have more actions to explore/try. If I add those, then I'd also need to update the simulation or run train it entirely through
    the actual game which will make training take even longer.

States:
    I'll need more observations if I add the extra actions.
    These attributes might be useful as inputs, with one list for each agent:
        ['x', 'y', 'percent', 'shield_strength', 'stock', 'facing',
        'action', 'action_frame', 'invulnerable', 'invulnerability_left', 'hitlag_left', 'hitstun_frames_left',
        'jumps_left', 'on_ground', 'speed_air_x_self', 'speed_y_self'] 

Rewards:
    How should sparse rewards work? Like dying and taking stocks? Is it okay to update all the actions that occurred
    during those states?        

Parameters:
    Could be the same as I currently have to describe the state but ideally more since it'd no longer be limited
    to the space that the table can hold. 
    New parameters could include percentages, a small context list of the previous actions, etc.

Training:
    Input state
    Get predicted q-values
    Do action
    Compare prediction to actual result
    Update network 

Usage:
    network = NN()
    state = get_state()
    actions = network.predict_q_values(state)
    best_action = get_action(actions)
    rewards = agent.do_action(best_action)
    network.update(results)

"""
import numpy as np
class Node:
    def __init__(self):
        self.bias = 0
        self.weight = 0
        self.value = 0
        self.next_node = None
        self.previous_layer = [] # contains all the nodes from the previous layer

    def activation(self):
        pass

