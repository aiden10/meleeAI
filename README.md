## About

Attempted to use a Q-Learning approach to develop an autonomous agent to play Super Smash Bros. Melee. I also used the libmelee library to interact with the game.
First a Q-Table is generated with states, possible actions, and probabilities for each action. This is what the data.py file is for. Afterwards, the Q-Table is used to generate moves and also gets updated after each game.

### Training Loop
- Use libmelee to see what state the game currently falls under and finds it in the Q-Table
- Perform an action based on the probabilities from that state in the table
- Wait based on the amount of frames the action takes
- Check the new state, evaluate the rewards and update the probabilities for the previous state
- Update the Q-Table permanently after each game

### Issues/Notes
In theory I believe that this should work correctly, though it may not produce a very strong agent. However I am currently having issues training it and seeing little to no improvement.
There could be a number of reasons but I think it's most likely one of the following:
- The timing of capturing the current game state after an action has been performed
- Modifying the probabilities too much
- Actions being performed incorrectly
- Not enough training
- Damage done may not be an accurate indicator of performance. At first I assumed that as it improves more damage would be done since attacks would land more and recovery would also improve, but I realize now that if attacks land more but recovery doesn't improve, then the graph won't reflect the improvement 

![Figure_1](https://github.com/aiden10/meleeAI/assets/51337166/f8d425ea-555a-4ea3-be83-f2a94c146009)

After the figure above was produced, I modified some of the probability adjustment values only to be met with an almost instant performance decrease seen here. It's kind of interesting how it remained so steady for so long with no real changes in average performance. 

![fall_off](https://github.com/aiden10/meleeAI/assets/51337166/148cbeb4-d903-4599-8af5-fa91188d206c)

I then decided to redo the training process, this time with smaller probability adjustments and a fixed reward for moving closer as opposed to having it be based on Δdistance_x. This effectively means that walking and dashing are indistinguishable but that can be changed later. Anyways, after making those adjustments it has begun to show an actual increase in average damage over the course 500 or so games (seen below). As a final test, after a sufficient amount of games have been played, I will measure the highest CPU it can beat and compare the results of a trained agent vs untrained agent.

![promise](https://github.com/aiden10/meleeAI/assets/51337166/61cb3ce6-5b3e-460f-b697-ca0233b1a9e6)

