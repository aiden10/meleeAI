import tensorflow as tf
import numpy as np
import random
from collections import deque

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0   # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()

    def _build_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(24, activation='relu', input_shape=(self.state_size,)),
            tf.keras.layers.Dense(24, activation='relu'),
            tf.keras.layers.Dense(self.action_size, activation='linear')
        ])
        model.compile(loss='mse', 
                     optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate))
        return model

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, action_list):
        if np.random.rand() <= self.epsilon:
            return random.choice(action_list)
        state_tensor = tf.convert_to_tensor(state.reshape(1, -1), dtype=tf.float32)
        act_values = self.model(state_tensor, training=False).numpy()[0]
        
        action_indices = {i: action for i, action in enumerate(action_list)}
        best_action_idx = np.argmax(act_values)
        return action_indices[best_action_idx]

    def replay(self, batch_size, action_list):
        if len(self.memory) < batch_size:
            return
            
        minibatch = random.sample(self.memory, batch_size)
        action_indices = {action: i for i, action in enumerate(action_list)}
        
        for state, action, reward, next_state, done in minibatch:
            state_tensor = tf.convert_to_tensor(state.reshape(1, -1), dtype=tf.float32)
            next_state_tensor = tf.convert_to_tensor(next_state.reshape(1, -1), dtype=tf.float32)
            
            # Current Q values
            with tf.GradientTape() as tape:
                q_values = self.model(state_tensor, training=True)[0]
                q_values_tensor = tf.convert_to_tensor(q_values)
                action_idx = action_indices[action]
                
                # Target Q values
                if done:
                    target_q = reward
                else:
                    next_q_values = self.target_model(next_state_tensor, training=False).numpy()[0]
                    target_q = reward + self.gamma * np.max(next_q_values)
                
                # Create target array identical to current output
                target_q_values = q_values.numpy()
                target_q_values[action_idx] = target_q
                
                # Calculate loss
                target_tensor = tf.convert_to_tensor(target_q_values)
                target_tensor = tf.reshape(target_tensor, (1, -1))
                q_values_tensor = tf.reshape(q_values_tensor, (1, -1))
                loss = tf.keras.losses.MSE(target_tensor, q_values_tensor)  

            # Calculate gradients and apply them
            grads = tape.gradient(loss, self.model.trainable_variables)
            self.model.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))
            
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)