import json
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
percent_ranges = [(0, 15), (15, 40), (40, 70), (70, 100), (100, 1000)]
x_dist_ranges = [(0, 5), (5, 16), (16, 30), (30, 50), (50, 70), (70, 1000)]
y_dist_ranges = [(0, 5), (5, 16), (16, 30), (30, 50), (50, 70), (70, 1000)]
airborne = [True, False]
offstage = [True, False]
agent_right = [True, False]

states = []
for agent_percent in percent_ranges:
    for opp_percent in percent_ranges:
        for y_range in y_dist_ranges:
            for x_range in x_dist_ranges:
                for is_airborne in airborne:
                    for is_offstage in offstage:
                        for agent_r in agent_right:
                            state = {
                                "Agent Percentage": agent_percent,
                                "Opponent Percentage": opp_percent,
                                "X_Distance": x_range,
                                "Y_Distance": y_range,
                                "Airborne": is_airborne,
                                "Offstage": is_offstage,
                                "Agent Right": agent_r,
                            }
                            states.append(state)

actions = ["Jab", "L_Tilt", "R_Tilt", "U_Tilt", "D_Tilt",
            "L_Smash", "R_Smash", "U_Smash", "D_Smash",
            "N_Special", "L_Special", "R_Special", "U_Special", "D_Special",
            "L_Throw", "R_Throw", "U_Throw", "D_Throw", 
            "Shield", "L_Dodge", "R_Dodge", "L_DAttack", "R_DAttack",
            "Jump", "L_Walk", "R_Walk", "L_Dash", "R_Dash", "Release"]

data = {}
for state_id, state in enumerate(states, start=1):
    action_probs = {action: 1/len(actions) for action in actions}
    data[state_id] = {"State": state, "Actions": action_probs}

with open(f"{CURRENT_DIR}/agent_data.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

print("done")