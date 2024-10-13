"""
Use a neural network to predict the next action from any given state
Feed it the state from the replay and have it predict what buttons were pressed.
Look at the replay, get the actual buttons that were pressed and update the network.
If I don't want to feed it a ton of different replays, it'd be best to only do those
from a single stage and with the same characters.

To make up for limited data and also kinda fine tune it I can do a combination of imitation and reinforcement learning where it plays
against itself.

Parsing the replay
Need to get:
    - State
    - Buttons that were pressed 
"""