import melee
import random

# Observations
def get_percent(g, port):
    return g.players[port].percent

def get_x_dist(g):
    agent_x = g.players[1].position.x
    opp_x = g.players[2].position.x
    return abs(agent_x - opp_x)

def get_y_dist(g):
    agent_y = g.players[1].position.y
    opp_y = g.players[2].position.y
    return abs(agent_y - opp_y)

def get_x_pos(g, port):
    return g.players[port].position.x

def get_y_pos(g, port):
    return g.players[port].position.y

def is_offstage(g, port):
    return g.players[port].off_stage

def is_airborne(g, port):
    return g.players[port].on_ground

def facing(g, port):
    return g.players[port].facing

def get_stock(g, port):
    return g.players[port].stock

def get_jumps(g, port):
    return g.players[port].jumps_left

# Basic Attacks
def Jab(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    return 17
def L_Tilt(controller):
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.4, 0.5)
    controller.press_button(melee.enums.Button.BUTTON_A)
    return 25

def R_Tilt(controller):
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.6, 0.5)
    controller.press_button(melee.enums.Button.BUTTON_A)
    return 25

def U_Tilt(controller):
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.5, 0.6)
    controller.press_button(melee.enums.Button.BUTTON_A)
    return 29

def D_Tilt(controller):
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.5, 0.4)
    controller.press_button(melee.enums.Button.BUTTON_A)
    return 39

# Smash Attacks
def L_Smash(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0, 0.5)
    return 5

def R_Smash(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 1, 0.5)
    return 5

def U_Smash(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 1)
    return 5

def D_Smash(controller):
    controller.press_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 0)
    return 5

# Special Attacks
def N_Special(controller):
    controller.press_button(melee.enums.Button.BUTTON_B)
def L_Special(controller):
    controller.press_button(melee.enums.Button.BUTTON_B)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0, 0.5)
def R_Special(controller):
    controller.press_button(melee.enums.Button.BUTTON_B)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 1, 0.5)
def U_Special(controller):
    controller.press_button(melee.enums.Button.BUTTON_B)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 1)
def D_Special(controller):
    controller.press_button(melee.enums.Button.BUTTON_B)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 0)

# Dash Attacks
def L_DAttack(controller):
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 0.5)
    controller.press_button(melee.enums.Button.BUTTON_A)
    return 50

def R_DAttack(controller):
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 1, 0.5)
    controller.press_button(melee.enums.Button.BUTTON_A)
    return 50

# Throws
def L_Throw(controller):
    controller.press_button(melee.enums.Button.BUTTON_Z)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0, 0.5)
    return 19

def R_Throw(controller):
    controller.press_button(melee.enums.Button.BUTTON_Z)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 1, 0.5)
    return 19

def U_Throw(controller):
    controller.press_button(melee.enums.Button.BUTTON_Z)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 1)
    return 19

def D_Throw(controller):
    controller.press_button(melee.enums.Button.BUTTON_Z)
    controller.tilt_analog(melee.enums.Button.BUTTON_C, 0.5, 0)
    return 19

def Shield(controller):
    controller.press_button(melee.enums.Button.BUTTON_R)
    return 50

def Release(controller):
    controller.release_all()
    return 15

# Movements
def L_Dodge(controller):
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.9, 0.5)
    controller.press_button(melee.enums.Button.BUTTON_R)
    return 30

def R_Dodge(controller):
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.1, 0.5)
    controller.press_button(melee.enums.Button.BUTTON_R)
    return 30

def Jump(controller):
    controller.press_button(melee.enums.Button.BUTTON_X)
    return 8

def L_Walk(controller):
    controller.release_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.35, 0.5)
    return 45

def R_Walk(controller):
    controller.release_button(melee.enums.Button.BUTTON_A)
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.65, 0.5)
    return 45

def L_Dash(controller):
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0, 0.5)
    return 20

def R_Dash(controller):
    controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 1, 0.5)
    return 20

def get_random_action():
    actions = [R_Dash, L_Dash, R_Walk, L_Walk, Jump, Release,
                L_Smash, R_Smash, D_Smash, U_Smash, L_Tilt, R_Tilt, U_Tilt]
    
    return actions[random.randint(0, len(actions) - 1)]
