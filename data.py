import json
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
x_dist_ranges = [(0, 5), (5, 16), (16, 30), (30, 50), (50, 70), (70, 1000)]
y_dist_ranges = [(0, 5), (5, 16), (16, 30), (30, 50), (50, 70), (70, 1000)]
x_pos_ranges = [(-1000, -85), (-85, -70), (-70, 70), (70, 85), (85, 1000)]
airborne = [True, False]
offstage = [True, False]
facing = [True, False]
def create_initial_agent():
    states = []
    for y_range in y_dist_ranges:
        for x_range in x_dist_ranges:
            for x_pos in x_pos_ranges:
                for is_airborne in airborne:
                    for is_offstage in offstage:
                        for direction in facing:
                            state = {
                                "X_Distance": x_range,
                                "Y_Distance": y_range,
                                "X_Position": x_pos,
                                "Airborne": is_airborne,
                                "Offstage": is_offstage,
                                "Facing": direction
                            }
                            states.append(state)

    actions = ["Jab", "L_Tilt", "R_Tilt", "U_Tilt", "D_Tilt",
                "L_Smash", "R_Smash", "U_Smash", "D_Smash",
                "L_Throw", "R_Throw", "U_Throw", "D_Throw", "Release",
                "L_Dodge", "R_Dodge","Jump", "L_Walk", "R_Walk", "L_Dash", "R_Dash"]

    data = {}
    for state_id, state in enumerate(states, start=1):
        action_probs = {action: 1/len(actions) for action in actions}
        data[state_id] = {"State": state, "Actions": action_probs}

    with open(f"{CURRENT_DIR}/agent_data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

        print("done")
        json_file.close()

def update_movement():
    json_file = open(f"{CURRENT_DIR}/agent_data.json", "r")
    state_data = json.load(json_file)
    for state_num, data in state_data.items():
        state_info = data["Actions"]
        state_info["L_Dash"] += 0.2
        state_info["R_Dash"] += 0.2
        state_info["L_Walk"] += 0.1
        state_info["R_Walk"] += 0.1
    json_file.close()

    json_file = open(f"{CURRENT_DIR}/agent_data.json", "w")

    json.dump(state_data, json_file, indent=4)
    json_file.close()
    print('done')

create_initial_agent()