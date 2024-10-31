import numpy as np
from typing import List, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F
import random

class CombatRNN(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, output_size: int):
        super(CombatRNN, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.attention = nn.MultiheadAttention(hidden_size, 4)
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, output_size)
        )
    
    def forward(self, x, hidden=None):
        # x shape: (batch, seq_len, input_size)
        lstm_out, hidden = self.lstm(x, hidden)
        
        # Apply attention
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Get final output
        out = self.fc(attn_out[:, -1, :])
        return out, hidden
    
    def init_hidden(self, batch_size: int):
        return (torch.zeros(self.num_layers, batch_size, self.hidden_size),
                torch.zeros(self.num_layers, batch_size, self.hidden_size))

class CombatAI:
    def __init__(self, state_size: int, action_size: int):
        self.state_size = state_size
        self.action_size = action_size
        self.memory_size = 1000
        self.batch_size = 32
        self.sequence_length = 10
        
        self.model = CombatRNN(
            input_size=state_size,
            hidden_size=128,
            num_layers=2,
            output_size=action_size
        )
        self.optimizer = torch.optim.Adam(self.model.parameters())
        self.memory: List[Tuple] = []
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) > self.memory_size:
            self.memory.pop(0)
    
    def get_action(self, state, epsilon: float = 0.1):
        if np.random.random() < epsilon:
            return np.random.randint(self.action_size)
        
        state = torch.FloatTensor(state).unsqueeze(0).unsqueeze(0)
        with torch.no_grad():
            q_values, _ = self.model(state)
            return q_values.argmax().item()
    
    def train(self):
        if len(self.memory) < self.batch_size:
            return
        
        # Sample batch
        batch = random.sample(self.memory, self.batch_size)
        states = torch.FloatTensor([s[0] for s in batch])
        actions = torch.LongTensor([s[1] for s in batch])
        rewards = torch.FloatTensor([s[2] for s in batch])
        next_states = torch.FloatTensor([s[3] for s in batch])
        dones = torch.FloatTensor([s[4] for s in batch])
        
        # Get current Q values
        current_q_values, _ = self.model(states)
        current_q_values = current_q_values.gather(1, actions.unsqueeze(1))
        
        # Get next Q values
        with torch.no_grad():
            next_q_values, _ = self.model(next_states)
            max_next_q = next_q_values.max(1)[0]
            target_q_values = rewards + (1 - dones) * 0.99 * max_next_q
        
        # Calculate loss and update
        loss = F.smooth_l1_loss(current_q_values.squeeze(), target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()