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

### Actual Improvement (fig. 3)
Prior to this, I had been operating under the false assumption that Q-Learning was simply making good actions more probable, and bad actions less probable. I looked at the formula previously and assumed that that was the jist of it. And while that was partially true, it turns out that it was a bit more nuanced. I think the biggest mistake I was making previously may have been not implementing any way of balancing exploration and exploitation/greed. The other mistake is that when dealing exclusively with probabilities, it's a bit tougher to determine how much the results of any given action should impact the probability of doing it again. The formula for Q-Learning is also more sophisticated than what I had been doing, with it applying a discount rate and subtracting the highest q-value from the new state by the q-value of the action that was just performed. As for the actual results after applying the correct formula and an epsilon greedy approach for exploration, you can see that the agent begins to improve quite quickly, with average damage increasing quite a bit over the course of the first 600 or so games. The issue that arises is afterwards, when it starts to act "greedily" and only chooses the actions which would yield the highest q-values, leading to a continued increase in q-values/rewards, but a huge decrease in damage done and actual performance.

![q-learning](https://github.com/user-attachments/assets/2a629f41-dacc-4d2d-9fe3-b80ac9361ed2)

### Tweaking Rewards and Hyperparameters (fig. 4)
Here, I updated the rewards to penalize bad actions more severely. The actions that I considered "bad" were those that resulted in moving away from the opponent or didn't move closer or do any damage. Interestingly, the agent's improvement went through many ups and downs until finally seeming to stabilize after about 3500 games. Also, this setup is still far from perfect as evidenced by the Q-values not aligning with the increases in damage, seeming inversely proportional to the damage, and growing very negative even after the agent should have begun to try maximizing the Q-values. As for the actual footage, it is still rather lackluster. 

![4](https://github.com/user-attachments/assets/5ffa570c-9792-4161-b6fd-5b1ed954607b)

#### Simulation Results
![fig4 2-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/09d9d8a4-0f17-4f69-baaa-5a8af9e2bdb6)

As you can see in the simulation, the agents appear to be acting in accordance to the rewards I set up, generally moving towards one another and attacking to do damage. The simulation is far from perfect and is more of a rough implementation meant to hopefully allow for the bare minimum of moving towards the opponent. I'm not really sure how knockback is calculated in the real game and there's a lot more smaller things which differ from the actual game, like attack distances, jump height, stage distances, getup attacks, ledges, etc, which is probably why it didn't translate super well to the real game as you can see below.

#### Simulation -> Real Game
![fig4 1-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/b6c63573-192a-473d-9e84-0c5c998f2e7b)

Here, the exact same Q-Table and decision making process is applied but this time to the actual game. The results here were even worse than in the simulation and seemed almost like purely random imputs at times. It could probably be improved by resetting the epsilon to a higher value to encourage more exploration again and then letting it train in the real game but I think it'd be best to instead just try applying Deep Q-Learning at this point. And I would also like to try using Slippi replays to mimic human playstyles at some point. In conclusion, the Q-Table kind of works here, but there's some compromises that needed to be made in order to keep the number of states small enough both for file size and keeping training time low. With that said, I was still pleasantly surprised by the results of using a Q-Table for this and seeing improvements on the graphs is a nice feeling.  
