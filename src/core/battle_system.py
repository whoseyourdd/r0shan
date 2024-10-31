from typing import List, Dict, Optional
import torch
from .character import Character
from .stats import Stats
from .ai.neural_network import CombatAI
from .cache import cached_result
from .constants import StatType, DerivedStatType
import random

class BattleSystem:
    def __init__(self):
        self.turn_counter = 0
        self.combat_log: List[Dict] = []
        self.state_size = len(StatType) + len(DerivedStatType) + 5  # +5 for status effects
        self.action_size = 10  # Basic actions + skills
        
        self.ai = CombatAI(self.state_size, self.action_size)
    
    @cached_result()
    def get_battle_state(self, character: Character) -> List[float]:
        state = []
        
        # Add base stats
        for stat in StatType:
            state.append(character.stats.get_total_stat(stat))
        
        # Add derived stats
        for stat in DerivedStatType:
            state.append(character.stats.derived_stats[stat])
        
        # Add status effects (normalized)
        for effect in character.status_effects:
            state.append(1.0 if effect in character.status_effects else 0.0)
        
        return state
    
    def execute_action(self, attacker: Character, defender: Character, 
                      action_id: int) -> Dict[str, float]:
        # Get derived stats for damage calculation
        attacker_stats = attacker.stats.derived_stats
        defender_stats = defender.stats.derived_stats
        
        # Calculate damage with critical hits
        is_crit = random.random() < attacker_stats[DerivedStatType.CRIT_CHANCE] / 100
        
        if action_id < 5:  # Physical attacks
            base_damage = attacker_stats[DerivedStatType.PHYSICAL_DAMAGE]
            if is_crit:
                base_damage *= 1 + (attacker_stats[DerivedStatType.CRIT_DAMAGE] / 100)
        else:  # Magical attacks
            base_damage = attacker_stats[DerivedStatType.MAGICAL_DAMAGE]
            if is_crit:
                base_damage *= 1.5
        
        # Apply dodge/block
        if random.random() < defender_stats[DerivedStatType.DODGE_CHANCE] / 100:
            return {"damage": 0, "dodged": True}
        
        if random.random() < defender_stats[DerivedStatType.BLOCK_CHANCE] / 100:
            base_damage *= 0.5
        
        return {
            "damage": base_damage,
            "critical": is_crit,
            "blocked": base_damage < attacker_stats[DerivedStatType.PHYSICAL_DAMAGE]
        }
    
    def train_ai(self, episodes: int = 1000):
        for _ in range(episodes):
            state = self.get_battle_state(self.team1[0])
            done = False
            
            while not done:
                action = self.ai.get_action(state)
                result = self.execute_action(self.team1[0], self.team2[0], action)
                
                reward = result["damage"]
                if result.get("critical", False):
                    reward *= 1.5
                
                next_state = self.get_battle_state(self.team1[0])
                done = self.is_battle_over()
                
                self.ai.remember(state, action, reward, next_state, done)
                self.ai.train()
                
                state = next_state