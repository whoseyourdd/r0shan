from dataclasses import dataclass
from typing import Dict
from .constants import StatType, DerivedStatType, STAT_SCALING
import math

@dataclass
class Stats:
    base_stats: Dict[StatType, float]
    bonus_stats: Dict[StatType, float] = None
    derived_stats: Dict[DerivedStatType, float] = None
    
    def __post_init__(self):
        self.bonus_stats = self.bonus_stats or {stat: 0 for stat in StatType}
        self.derived_stats = {}
        self._calculate_derived_stats()
    
    def get_total_stat(self, stat_type: StatType) -> float:
        return self.base_stats[stat_type] + self.bonus_stats[stat_type]
    
    def _calculate_derived_stats(self):
        for derived_stat, scaling in STAT_SCALING.items():
            total = 0
            for base_stat, multiplier in scaling.items():
                total += self.get_total_stat(base_stat) * multiplier
            
            # Apply diminishing returns for certain stats
            if derived_stat in [DerivedStatType.CRIT_CHANCE, 
                              DerivedStatType.DODGE_CHANCE, 
                              DerivedStatType.BLOCK_CHANCE]:
                total = 100 * (1 - math.exp(-total / 100))
            
            self.derived_stats[derived_stat] = total
    
    def update_stat(self, stat_type: StatType, value: float, is_base: bool = False):
        if is_base:
            self.base_stats[stat_type] = value
        else:
            self.bonus_stats[stat_type] = value
        self._calculate_derived_stats()
    
    def apply_buff(self, stat_type: StatType, value: float):
        self.bonus_stats[stat_type] += value
        self._calculate_derived_stats()
    
    def remove_buff(self, stat_type: StatType, value: float):
        self.bonus_stats[stat_type] -= value
        self._calculate_derived_stats()