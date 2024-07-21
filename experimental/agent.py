"""
Need to save the possible actions in the JSON file too 

Hyperparameters:
    - min_relevance
    - happiness_threshold
    - max_actions
    - learning_rate

happiness_adjustment: how much the current happiness changes when it traverses this node. current_happiness += node.happiness_adjustment * relevance
happiness: used during the relevance calculations and for probability adjustment. More extreme values result in more greater adjustments.

What I am currently doing:
If an action does damage I get a reward based on the damage done. I then update the current happiness and the happiness adjustment. I also
update the performed action's probability based on the reward. 
While traversing the relevant nodes I am getting the probabilities of each of the node's actions and multiplying it by the relevance. However,
this doesn't account for how good of a move it actually was, just that it was performed in a similar state. To better calculate the adjustments
I should use the state's happiness and also the results if it has any. So use the action's resulted happiness but it shouldn't be weighed too heavily.

Ideas:
- -1 to current happiness for each stock you are down by and +1 to current happiness for each stock you are up by. Try this to see if it 
solves the credit assignment problem. Also try with and without action grouping to determine the best combination.

- Memory pruning. To avoid the graph from growing way too large and making this infeasible to actually run, I can simply remove the oldest nodes.
The oldest nodes would also probably not be doing much later on anyways because of the relevance calculations (depending on how much I value the time difference).
Hopefully, me removing old nodes won't impact it too much because it won't need the old ones to get better and better.
Though, this wouldn't work if the environment is more complex and requires accessing old memories. An alternative to this would also be to
compress every n nodes into a single node by calculating the averages of all of them.  

- Dynamic wait times between actions. Not sure if this is needed or not but could be worth trying. 

- Instead of recalculating the most relevant node each time, I can instead return a list of the n most relevant nodes of the initial node and
use that list as the context. It would definitely result in better computational performance but I don't know how it would affect the actual
performance. 

- Releasing all buttons after the wait period

- Modifying the average node calculation. Instead of treating each one equally, I can instead weigh the ones that had better results higher
or the ones with more extreme happiness values.
"""

import os
import ujson as json
import numpy as np
from functions import *

A = melee.enums.Button.BUTTON_A
B = melee.enums.Button.BUTTON_B
Y = melee.enums.Button.BUTTON_Y
Z = melee.enums.Button.BUTTON_Z
R = melee.enums.Button.BUTTON_R
MAIN_STICK = melee.enums.Button.BUTTON_MAIN
C_STICK = melee.enums.Button.BUTTON_C

class Node:
    def __init__(self, features, time, happiness_adjustment=0, actions=None, secondary_actions=None, results={}, happiness=0):
        self.features = features
        self.time = time # cycle when frame was created
        self.happiness_adjustment = happiness_adjustment
        self.actions = actions # actions/probabilties dict 
        self.secondary_actions = secondary_actions # stick_x, stick_y, button to release
        self.results = results # the reward gained from the action
        self.happiness = happiness

    def jsonify(self):
        """
        Converts node objects to dictionaries to store them in a JSON file.
        """
        node_json = {
            'features': self.features,
            'time': self.time,
            'happiness_adjustment': self.happiness_adjustment,
            'actions': self.actions,
            'secondary_actions': self.secondary_actions,
            'results': self.results,
            'happiness': self.happiness
        }
        return node_json

def release(controller, button):
    controller.release_button(button)

def do_action(controller, button, x=0.5, y=0.5):
    if button == MAIN_STICK or button == C_STICK:
        controller.tilt_analog(button, x, y)
    else:
        controller.press_button(button)

def normalize_features(features):
    """
    Converts each feature to a number between 0-1.
    """
    normalized_features = {}
    for key, value in features.items():
        if 'x' in key or 'y' in key:
            normalized_features[key] = (value + 225) / 450  # Scale to range 0 to 1
        elif 'percent' in key:
            normalized_features[key] = value / 999  # Assuming percent can't go above 999
        elif 'jump' in key:
            normalized_features[key] = value / 2
        elif 'stocks' in key:
            normalized_features[key] = value / 4
        else: # boolean
            if value == True: value = 1 # may be too high
            elif value == False: value = 0
            # value can be a number because of averages 
            normalized_features[key] = value

    return normalized_features

def extract_features(g, agent_port, opponent_port):
    """
    Returns a dict with relevant information about the current game state.
    """
    agent_percent = get_percent(g, agent_port)
    opp_percent = get_percent(g, opponent_port)
    x_dist = get_x_dist(g)
    y_dist = get_y_dist(g)
    agent_x_pos = get_x_pos(g, agent_port)
    agent_y_pos = get_y_pos(g, agent_port)
    opp_x_pos = get_x_pos(g, opponent_port)
    opp_y_pos = get_y_pos(g, opponent_port)
    agent_offstage = is_offstage(g, agent_port)
    opp_offstage = is_offstage(g, opponent_port)
    agent_airborne = is_airborne(g, agent_port)
    opp_airborne = is_airborne(g, opponent_port)
    agent_direction = facing(g, agent_port)
    agent_stocks = get_stock(g, agent_port)
    opp_stocks = get_stock(g, opponent_port)
    agent_jumps = get_jumps(g, agent_port)
    opp_jumps = get_jumps(g, opponent_port)
    features = {
        'player_x': agent_x_pos,
        'player_y': agent_y_pos,
        'direction': agent_direction,
        'opp_x': opp_x_pos,
        'opp_y': opp_y_pos,
        'percent': agent_percent,
        'opp_percent': opp_percent,
        'offstage': agent_offstage,
        'opp_offstage': opp_offstage,
        'airborne': agent_airborne,
        'opp_airborne': opp_airborne,
        'jumps': agent_jumps,
        'stocks': agent_stocks,
        'opp_stocks': opp_stocks
    }
    return features

def calculate_relevance(node1, node2):
    """
    Determines how relevant two given nodes are to one another. 
    Takes into account:
        - Time between two nodes
        - Similarity of features
        - Happiness of both nodes
    The returned relevance should be smaller if the nodes are less relevant and larger the more relevant they are to eachother.
    """
    n1_features = normalize_features(node1.features)
    n2_features = normalize_features(node2.features)
    relevance = 0
    time_diff = abs(node1.time - node2.time)
    happiness_diff = abs(node1.happiness - node2.happiness) 
    for key in n1_features: # both should always be the same length
        feature_diff = abs(n1_features[key] - n2_features[key]) # this assumes that each feature will be numeric. But it could be adjusted for other values
        relevance += (feature_diff)
        relevance += happiness_diff

    return relevance + time_diff

def calculate_reward(old_features, new_features):
    """
    Calculates any immediate rewards between two different states.
    """
    prev_opp_percent = old_features['opp_percent']
    opp_percent = new_features['opp_percent']
    
    return (prev_opp_percent - opp_percent) * -1 # multiply by -1 so that doing damage results in positive number

def find_most_relevant_node(graph, node):
    """
    Loops over the graph and finds the most relevant node.
    Returns the most relevant node and its relevance value.
    """
    max_relevance = float('-inf')
    most_relevant_node = None

    for other_node in graph:
        relevance_value = calculate_relevance(node, other_node)
        if relevance_value > max_relevance:
            max_relevance = relevance_value
            most_relevant_node = other_node

    return most_relevant_node, max_relevance

def find_action_groups(graph, happiness_threshold=30, max_actions=5):
    """
    The larger the number of max actions, I think the more complex the behavior that can emerge.
    However, in this environemnt it doesn't need a reason to continue growing, also not every environment necessarily requires
    grouping actions together. Something like chess doesn't really require it, though you could think of openings as action groups in a way.
    """
    action_groups = []

    for i in range(len(graph)):
        cumulative_happiness = 0
        action_sequence = []
        
        for j in range(i, min(i + max_actions, len(graph))):
            node = graph[j]
            result = next(iter(node.results.items()))
            action = result['action']
            if type(action) != 'tuple': # I don't want to create groups of grouped actions since there's a point where more actions doesn't make sense
                if action == MAIN_STICK or action == C_STICK:
                    x = result['stick_x']
                    y = result['stick_y']
                    action_element = (action, x, y)
                elif action == 'RELEASE':
                    action_element = (action, result['release_button'])
                else:
                    action_element = (action)

                action_sequence.append(action_element) # add the action
                cumulative_happiness += node.happiness
                
                if cumulative_happiness >= happiness_threshold:
                    action_groups.append(tuple(action_sequence)) # tuple so they're hashable
                    break

    return action_groups

def average_context(context, performed_action):
    """
    Creates and returns a new node with the averages of each node in the context. 
    """
    release_button_sums = {
    A: 0,
    B: 0,
    Y: 0,
    Z: 0,
    R: 0,
    MAIN_STICK: 0,
    C_STICK: 0,
    }
    action_sums = {}
    player_x_sum = 0
    player_y_sum = 0
    opp_x_sum = 0
    opp_y_sum = 0
    percent_sum = 0
    opp_percent_sum = 0
    stocks_sum = 0
    opp_stocks_sum = 0
    jumps_sum = 0
    direction_sum = 0
    offstage_sum = 0
    opp_offstage_sum = 0
    airborne_sum = 0
    opp_airborne_sum = 0
    cycle_sum = 0
    happiness_sum = 0
    context_length = len(context)
    
    for node in context:
        release_probs = node.secondary_actions['release_button']
        for button, prob in release_probs.items():
            release_button_sums[button] += prob
        actions = node.actions
        for action, prob in actions.items():
            if action not in action_sums:
                action_sums.update({action: prob})
            else:
                action_sums[action] += prob

        stick_x_sum = 0
        stick_y_sum = 0
        wait_sum = 0
        happiness_sum += node.happiness
        cycle_sum += node.time
        player_x_sum += node.features['player_x']
        player_y_sum += node.features['player_y']
        opp_x_sum += node.features['opp_x']
        opp_y_sum += node.features['opp_y']
        percent_sum += node.features['percent']
        opp_percent_sum += node.features['opp_percent']
        stocks_sum += node.features['stocks']
        opp_stocks_sum += node.features['opp_stocks']
        jumps_sum += node.features['jumps']
        stick_x_sum += node.secondary_actions['stick_x']
        stick_y_sum += node.secondary_actions['stick_y']
        wait_sum += node.secondary_actions['wait_time']
        if node.features['direction']: direction_sum += 1
        if node.features['offstage']: offstage_sum += 1
        if node.features['opp_offstage']: opp_offstage_sum += 1
        if node.features['airborne']: airborne_sum += 1
        if node.features['opp_airborne']: opp_airborne_sum += 1

        # also sum the values for resulted_happiness, time, each action probability and secondary action values 
        relevance = calculate_relevance(initial_node, node)
        context.actions[performed_action] += (resulted_happiness * relevance) 
    
    # calculate averages of the context nodes
    avg_player_x = player_x_sum / context_length
    avg_player_y = player_y_sum / context_length
    avg_opp_x = opp_x_sum / context_length
    avg_opp_y = opp_y_sum / context_length
    avg_percent = percent_sum / context_length
    avg_opp_percent = opp_percent_sum / context_length
    avg_stocks = stocks_sum / context_length
    avg_opp_stocks = opp_stocks_sum / context_length
    avg_jumps = jumps_sum / context_length
    avg_direction = direction_sum / context_length
    avg_offstage = offstage_sum / context_length
    avg_opp_offstage = opp_offstage_sum / context_length
    avg_airborne = airborne_sum / context_length
    avg_opp_airborne = opp_airborne_sum / context_length
    avg_time = cycle_sum / context_length
    avg_happiness = happiness_sum / context_length
    average_features = {
        'player_x': avg_player_x,
        'player_y': avg_player_y,
        'direction': avg_direction,
        'opp_x': avg_opp_x,
        'opp_y': avg_opp_y,
        'percent': avg_percent,
        'opp_percent': avg_opp_percent,
        'offstage': avg_offstage,
        'opp_offstage': avg_opp_offstage,
        'airborne': avg_airborne,
        'opp_airborne': avg_opp_airborne,
        'jumps': avg_jumps,
        'stocks': avg_stocks,
        'opp_stocks': avg_opp_stocks
    }

    avg_actions = {action: action_sums[action] / context_length for action in action_sums}
    avg_secondary_actions = {
        'stick_x': stick_x_sum / context_length,
        'stick_y': stick_y_sum / context_length,
        'release_button': {button: release_button_sums[button] / context_length for button in release_button_sums},
        'wait_time': wait_sum / context_length
    }

    context_average = Node(average_features, avg_time)
    context_average.happiness = avg_happiness
    context_average.actions = avg_actions
    context_average.secondary_actions = avg_secondary_actions

    return context_average

def softmax(x):
    return (np.exp(x) / np.sum(np.exp(x), axis=0)).tolist()

def get_action(actions):
    probabilities = list(actions.values())
    softmaxed_probabilities = softmax(probabilities)
    performed_action = np.random.choice(list(actions.keys()), 1, p=softmaxed_probabilities)[0]
    return performed_action    

def save_state(new_nodes, cycle):
    data = open(f"{CURRENT_DIR}/graph.json", "r")
    nodes = json.load(data)
    nodes['cycle'] = cycle
    for node in new_nodes:
        nodes['nodes'].append(node.jsonify())
    with open(f"{CURRENT_DIR}/graph.json", "w") as fh:
        json.dump(nodes, fh) 
    print('saved data')

def load_graph():
    data = open(f"{CURRENT_DIR}/graph.json", "r")
    nodes = json.load(data)
    node_list = []
    for node in nodes:
        node_object = Node(node['features'], node['time'], 
                        node['happiness_adjustment'], node['actions'],
                        node['secondary_actions'], node['results'], node['happiness'])
        node_list.append(node_object)
    print('loaded data')
    return node_list, nodes['cycle']

def wait(console, wait_time):
    current_frame = 0
    while current_frame < wait_time:
        console.step()
        current_frame += 1

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
console = melee.Console(path=r"C:\Users\aiden\AppData\Roaming\Slippi Launcher\netplay")

controller = melee.Controller(console=console, port=1)
controller_opp = melee.Controller(console=console, port=2)

graph, cycle = load_graph()
current_happiness = 0
current_frame = 0
min_relevance = 50
possible_actions = [A, B, Y, Z, R, MAIN_STICK, C_STICK, 'RELEASE']
base_probability = 1 / len(possible_actions) 
button_release_probabilities = {
A: base_probability,
B: base_probability,
Y: base_probability,
Z: base_probability,
R: base_probability,
MAIN_STICK: base_probability,
C_STICK: base_probability,
}
current_secondary_actions = {
    'stick_x': 0,
    'stick_y': 0,
    'release_button' : button_release_probabilities,
    'wait_time': 1
}

console.run()
console.connect()

controller.connect()
controller_opp.connect()
a1_character = melee.Character.MARTH
a2_character = melee.Character.MARTH

while True:
    gamestate = console.step()
    if gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]:
        cycle += 1
        context = []
        current_actions = {}

        # load action table. Done like this because of action grouping
        for action in possible_actions:
            current_actions.update({action: base_probability})

        state_features = extract_features()
        initial_node = Node(state_features, cycle)

        # traverse the graph
        current_node, relevance = find_most_relevant_node(graph, initial_node)
        while relevance > min_relevance:    
            context.append(current_node)
            current_node, relevance = find_most_relevant_node(current_node) # potentially modify to be a list of nodes instead
        
        # update the current probabilities based on the nodes in the context
        for node in context:
            relevance = calculate_relevance(initial_node, node)
            for action, prob in node.actions.values():
                adjusted_prob = (prob * relevance) 
                current_actions[action] += adjusted_prob

            stick_x, stick_y = node.secondary_actions['stick_x'], node.secondary_actions['stick_y']
            release_probs = node.secondary_actions['release_button']

            if node.results['performed_action'] == C_STICK or node.results['performed_action'] == MAIN_STICK:
                current_secondary_actions['stick_x'] += (stick_x * relevance) 
                current_secondary_actions['stick_y'] += (stick_y * relevance) 

            for button, prob in release_probs.items():
                adjusted_prob = (prob * relevance) 
                current_secondary_actions['release_button'][button] += adjusted_prob

            current_happiness += (node.happiness_adjustment * relevance) 
            
        # assign the probabilities here so they represent the action values after the traversal
        initial_node.actions = current_actions
        initial_node.secondary_actions = current_secondary_actions

        # do action
        performed_action = get_action(current_actions) # need to replace with softmax + probability to pick action
        button_to_release = None
        wait_time = current_secondary_actions['wait_time']

        if performed_action == 'RELEASE':
            button_to_release = controller, max(current_secondary_actions['release_button'], key=current_secondary_actions['release_button'].get)
            release(button_to_release)
            wait(console, wait_time)

        # action was a grouped action not a single button press
        elif type(performed_action) == 'tuple':
            for element in performed_action: # do each action
                action = element[0]
                if action == 'RELEASE':
                    controller.release_button(element[1])
                else:
                    x, y = element[1], element[2]
                    do_action(controller, action)

                wait(console, 1) # pressing in sequence so wait only one frame
        
        # regular button press action
        else: 
            x = current_secondary_actions[stick_x]
            y = current_secondary_actions[stick_y]

            do_action(controller, performed_action, x, y)
        
            wait(console, wait_time)

        # get new state and compare with previous state
        new_state = extract_features()
        resulted_happiness = calculate_reward(state_features, new_state) # scale this to work for probabilities and x/y stick values

        # update happiness values for the node
        current_happiness += resulted_happiness
        initial_node.happiness = current_happiness
        initial_node.happiness_adjustment += resulted_happiness

        # update performed action probabilities
        if performed_action == 'RELEASE': 
            current_secondary_actions['release_button'][button_to_release] += resulted_happiness
        elif performed_action == MAIN_STICK or performed_action == C_STICK:
            current_secondary_actions['stick_x'] += resulted_happiness
            current_secondary_actions['stick_y'] += resulted_happiness

        current_actions[performed_action] += resulted_happiness 
        initial_node.results.update({'action': performed_action,
                                    'reward': resulted_happiness,
                                    'stick_x': current_secondary_actions['stick_x'],
                                    'stick_y': current_secondary_actions['stick_y'],
                                    'release_button': button_to_release,
                                    'wait': wait_time})

        context_average = average_context(context, performed_action) # create a new node with the averages of the context values               
        
        graph.append(initial_node)
        graph.append(context_average)

        # get action groups and add them to the possible actions 
        new_actions = find_action_groups(graph)
        for action_group in new_actions:
            possible_actions.append({hash(action_group): action_group})

    else:
        if not updated:
            controller.release_all()
            controller_opp.release_all()
            save_state(graph, cycle)
            updated = True
            current_frame = 0

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
