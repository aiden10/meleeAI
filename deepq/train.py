import numpy as np
import tensorflow as tf
from gym import SmashEnv
from network import DQNAgent
import os
import time

log_dir = "deepq/logs/"
os.makedirs(log_dir, exist_ok=True)

env = SmashEnv()

state_size = env.observation_space_n
action_size = env.action_space_n

agent = DQNAgent(state_size, action_size)

# Parameters
EPISODES = 1000
batch_size = 32

summary_writer = tf.summary.create_file_writer(log_dir)

action_list = list(env.action_space.keys())

for e in range(EPISODES):
    state = env.reset()
    total_reward = 0
    
    for time_step in range(env.max_steps):
        action = agent.act(state, action_list)        
        next_state, reward, done, info = env.step(action)
        
        agent.remember(state, action, reward, next_state, done)
        
        state = next_state
        total_reward += reward
        
        if done:
            if e % 10 == 0:
                agent.update_target_model()
            break
    
    # Train with replay memory
    if len(agent.memory) > batch_size:
        agent.replay(batch_size, action_list)
    
    # Logging
    with summary_writer.as_default():
        tf.summary.scalar('episode_reward', total_reward, step=e)
        tf.summary.scalar('agent_stocks', info['agent_stocks'], step=e)
        tf.summary.scalar('enemy_stocks', info['enemy_stocks'], step=e)
        tf.summary.scalar('epsilon', agent.epsilon, step=e)
    
    if e % 100 == 0:
        agent.save(f"{log_dir}/dqn_smash_{e}.weights.h5")
        
    print(f"Episode: {e}/{EPISODES}, Score: {total_reward}, Epsilon: {agent.epsilon:.2f}")
    print(f"Agent stocks: {info['agent_stocks']}, Enemy stocks: {info['enemy_stocks']}")
    print(f"Steps: {time_step}")
    print("-" * 50)

# Save final model
agent.save(f"{log_dir}/dqn_smash_final.weights.h5")
