## About

Attempted to use a Q-Learning approach to develop an autonomous agent to play Super Smash Bros. Melee. I also used the libmeleee library to interact with the game.

### Observations:
I used the following ranges/variables to generate all possible game states and paired each state with all possible actions and each possible action with a probability (a Q-Table):

`percent_ranges = [(0, 15), (15, 40), (40, 70), (70, 100), (100, 1000)]`

`x_dist_ranges = [(0, 5), (5, 16), (16, 30), (30, 50), (50, 70), (70, 1000)]`

`y_dist_ranges = [(0, 5), (5, 16), (16, 30), (30, 50), (50, 70), (70, 1000)]`

`x_pos_ranges = [(-1000, -85), (-85, -70), (-70, 70), (70, 85), (85, 1000)]`

`airborne = [True, False]`

`offstage = [True, False]`

### Training
After generating the Q-Table, the game is run and I use meleelib to see which game state the game is currently in. An action is then performed based on the respective probabilities for that state, and after the action is performed, I see the new state the game is in. 


### Rewards
After seeing how the state changed, the probabilities of performing the action(s) which led to the reward/punishment are tweaked.
- Moving closer -> Positive 
- Moving further -> Negative
- Taking a stock -> Positive
- Losing a stock -> Negative
- Dealing damage -> Positive
- Taking damage -> Negative

