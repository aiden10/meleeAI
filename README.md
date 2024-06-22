## About

Attempted to use a tabular Q-Learning approach to develop an autonomous agent to play Super Smash Bros. Melee. I also used the libmelee library to interact with the game.
First the `data.py` file is used to generate a Q-Table with states, possible actions, and probabilities for each action. Afterwards, the Q-Table is used to generate moves and also gets updated after each game.

## Training Loop
- Use libmelee to see what state the game currently falls under and finds it in the Q-Table
- Perform an action based on the probabilities from that state in the table
- Wait based on the amount of frames the action takes
- Check the new state, evaluate the rewards and update the probabilities for the previous state
- Update the Q-Table permanently after each game


## Results
### Initial Attempt (fig. 1)

The data in the graph below was captured over the course of approximately 2000 games, during which I tried the following methods of modifying action probabilities:
-  If the action resulted in moving closer to the opponent, make the action more likely based on how much closer the agent got
-  If the action resulted in moving further away from the opponent, make the action less likely based on how much further the agent got
-  If the action did damage, make the action more likely based on how much damage was done
-  If the action does no damage and does not change the agent's x position, decrease the probability of it and increase the probabilities of movements for that state
-  When the agent loses a stock, decrease all the probabilities of all actions that were done during that stock

However, as you can see there was no improvement or changes to its performance. I believe that this was because I was modifying the probabilities too much whenever one of the above occured. I don't fully understand why it led to this, especially since I would assume that it would balance itself out to some extent but the results show otherwise. 

![fig1(1)](https://github.com/aiden10/meleeAI/assets/51337166/7647c843-58d8-4455-b237-d279c0db5752)

### Increased probability adjustment (fig. 1.1)
After the figure above was produced, I modified some of the probability adjustment values only to be met with an almost instant performance decrease seen here. It's kind of interesting how it remained so steady for so long with no real changes in average performance but took no time at all to get worse.

![fig1 1(1)](https://github.com/aiden10/meleeAI/assets/51337166/9614b3ca-fc33-47e5-8dbf-38ed54a0bdfa)

### Restarted with lower probability adjustments (fig. 2)
I decided to redo the training process, this time with smaller probability adjustments, a fixed reward for moving closer as opposed to having it be based on the changes in the x position (this effectively means that walking and dashing are indistinguishable but that can be changed later) and movements being more likely from the start. After making those adjustments it began to show an increase in average damage after 200 or so games, but then stayed at that level and did not continue to improve. One interesting thing I noticed is that the initial damage started lower and remained lower than the previous attempt. I suspect that's because I made movements more likely for every state, so less attacks were being performed. Although I'm not too concerned about that since I'm less interested in its performance/ability and more interested in its improvement, so I would still consider this a minor success.

![fig2(1)](https://github.com/aiden10/meleeAI/assets/51337166/91946ddb-0ff5-4aa6-99d1-7d125c8d6b0e)

### Simulated Game
After trying different weights and adjusting the policy, I was still failing to see improvement and decided to create a simulated version of the game so I could test things faster. So I plan to train an agent quickly in the simulated version and then take the agent data and put it into the real game so I can see how well it performs and also to hopefully correct any inconsistencies between the simulation and real game. I may attempt an evolutionary reinforcement learning approach after.  

![melee_sim-ezgif com-video-to-gif-converter](https://github.com/aiden10/meleeAI/assets/51337166/58cb6ee2-0d37-483b-be85-f8ef2b67331c)
