import json
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
x_dist_ranges = [(0, 5), (5, 16), (16, 30), (30, 50), (50, 70), (70, 1000)]
y_dist_ranges = [(0, 5), (5, 16), (16, 30), (30, 50), (50, 70), (70, 1000)]
x_pos_ranges = [
    (-1000, -85), (-85, -75), (-75, -65), (-65, -55), (-55, -45), (-45, -35),
    (-35, -25), (-25, -15), (-15, -5), (-5, 5), (5, 15), (15, 25), (25, 35),
    (35, 45), (45, 55), (55, 65), (65, 75), (75, 85), (85, 1000)]

y_pos_ranges = [(-1000, 0), (0, 10), (10, 20), (20, 40), (40, 60), (60, 1000)]
offstage = [True, False]
facing = [True, False]
jumps_left = [True, False]
def create_initial_agent():
    states = []
    for agent_x_pos in x_pos_ranges:
        for agent_y_pos in y_pos_ranges:
            for opponent_x_pos in x_pos_ranges:
                for opponent_y_pos in y_pos_ranges:
                    for jumps in jumps_left:
                        state = {
                            "Agent_X_Position": agent_x_pos,
                            "Agent_Y_Position": agent_y_pos,
                            "Opponent_X_Position": opponent_x_pos,
                            "Opponent_Y_Position": opponent_y_pos,
                            "Jumps_Left": jumps
                        }
                        states.append(state)

    actions = ["L_Tilt", "R_Tilt", "U_Tilt",
                "L_Smash", "R_Smash", "U_Smash", "D_Smash",
                "Jump", "L_Walk", "R_Walk", "L_Dash", "R_Dash"]
    data = {}
    for state_id, state in enumerate(states, start=1):
        action_probs = {action: 1/len(actions) for action in actions}
        if state == (-1000, -85): # offstage and at edge of stage (left side)
            action_probs["L_Dash"] += 0.3  # Make L_Dash less likely
            action_probs["L_Walk"] += 0.3  # Make L_Walk less likely
            action_probs["R_Dash"] += 0.3  # Make R_Dash more likely
            action_probs["R_Walk"] += 0.3  # Make R_Walk more likely
            action_probs["Jump"] += 0.3    # Make jumps more likely
        
        elif state == (85, 1000): # offstage and at edge of stage (right side)
            action_probs["R_Dash"] += 0.3  # Make R_Dash less likely
            action_probs["R_Walk"] += 0.3  # Make R_Walk less likely
            action_probs["L_Dash"] += 0.3  # Make L_Dash more likely
            action_probs["L_Walk"] += 0.3  # Make L_Walk more likely
            action_probs["Jump"] += 0.3  # Make jumps more likely
                    
        data[state_id] = {"State": state, "Actions": action_probs}
    with open(f"{CURRENT_DIR}/agent_data.json", "w") as json_file:
        json.dump(data, json_file)

        print("done")
        json_file.close()
 
create_initial_agent()