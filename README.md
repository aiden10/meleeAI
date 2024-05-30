## About

Attempted to use a Q-Learning approach to develop an autonomous agent to play Super Smash Bros. Melee. I also used the libmelee library to interact with the game.
First a Q-Table is generated with states, possible actions, and probabilities for each action. This is what the data.py file is for. Afterwards, the Q-Table is used to generate moves and also gets updated after each game.

### Training Loop
- Use libmelee to see what state the game currently falls under and finds it in the Q-Table
- Perform an action based on the probabilities from that state in the table
- Wait based on the amount of frames the action takes
- Check the new state, evaluate the rewards and update the probabilities for the previous state
- Update the Q-Table permanently after each game

### Issues
In theory I believe that this should work correctly, though it may not produce a very strong agent. However I am currently having issues training it and seeing little to no improvement.
There could be a number of reasons but I think it's most likely one of the following:
- The timing of capturing the current game state after an action has been performed
- Modifying the probabilities too much
- Actions being performed incorrectly

![Figure_1](https://github.com/aiden10/meleeAI/assets/51337166/e21ed015-2cff-49e8-ac1e-ac34bd043b94)

More testing is needed.
