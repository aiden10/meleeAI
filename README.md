## About

Attempted to use a Q-Learning approach to develop an autonomous agent to play Super Smash Bros. Melee. I also used the libmelee library to interact with the game.
First a Q-Table is generated with states, possible actions, and probabilities for each action. This is what the data.py file is for. Afterwards, the Q-Table is used to generate moves and also gets updated after each game.

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

![Figure_1](https://github.com/aiden10/meleeAI/assets/51337166/f8d425ea-555a-4ea3-be83-f2a94c146009)

### Increased probability adjustment (fig. 1.1)
After the figure above was produced, I modified some of the probability adjustment values only to be met with an almost instant performance decrease seen here. It's kind of interesting how it remained so steady for so long with no real changes in average performance but took no time at all to get worse.

![fall_off](https://github.com/aiden10/meleeAI/assets/51337166/148cbeb4-d903-4599-8af5-fa91188d206c)

### Restarted with lower probability adjustments (fig. 2)
I decided to redo the training process, this time with smaller probability adjustments, a fixed reward for moving closer as opposed to having it be based on the changes in the x position (this effectively means that walking and dashing are indistinguishable but that can be changed later) and movements being more likely from the start. After making those adjustments it began to show an increase in average damage after 200 or so games, but then stayed at that level and did not continue to improve. One interesting thing I noticed is that the initial damage started lower and remained lower than the previous attempt. I suspect that's because I made movements more likely for every state, so less attacks were being performed. Although I'm not too concerned about that since I'm less interested in its performance/ability and more interested in its improvement, so I would still consider this a minor success.

![Figure_1](https://github.com/aiden10/meleeAI/assets/51337166/513fa4bf-8740-4929-8785-257df2d78a3b)

## Notes
So far, none of the attempts have resulted in anything I would consider "good" by any means. Even after the improvement seen in (fig. 2), I feel unable to discern at times whether I'm watching actions being performed totally at random or whether they are being performed somewhat "intelligently". Many times the agent continues to SD and do what appears to be just random inputs. Although I guess I could say that it's not random since random would look like the first 200 games of (fig. 2). This is the main reason I have not added any gameplay footage so far. However, I plan to try adding some conditions to encourage recovery better, prevent SDing, and see how smaller probability adjustments will affect the results. After I'm satisfied with the performance I will pit it against a CPU and compare its results to an untrained version.  
