from typing import Dict, List, Optional
from .stats import Stats
from .constants import StatType, DerivedStatType
from .jobs import Job
import json

class Character:
    def __init__(self, name: str, race: str):
        self.name = name
        self.race = race
        self.level = 1
        self.exp = 0
        
        # Initialize base stats
        base_stats = {stat: 10 for stat in StatType}
        self.stats = Stats(base_stats)
        
        self.current_job = None
        self.jobs = []
        self.skills = []
        self.inventory = []
        self.status_effects = []
        
        # Load race bonuses
        self._apply_race_bonuses()
    
    def _apply_race_bonuses(self):
        with open('src/assets/data/races.json', 'r') as f:
            races = json.load(f)
            if self.race in races:
                race_stats = races[self.race]["stats"]
                for stat, value in race_stats.items():
                    self.stats.update_stat(StatType[stat.upper()], value, True)
    
    def add_job(self, job: Job):
        if job.requirements_met(self):
            self.jobs.append(job)
    
    def level_up(self):
        self.level += 1
        
        # Calculate stat increases based on job and race
        stat_increases = self._calculate_stat_increases()
        for stat, increase in stat_increases.items():
            self.stats.update_stat(stat, 
                                 self.stats.get_total_stat(stat) + increase, 
                                 True)
    
    def _calculate_stat_increases(self) -> Dict[StatType, float]:
        increases = {stat: 0 for stat in StatType}
        
        # Base increases
        increases[StatType.HP] = 10
        increases[StatType.MP] = 5
        
        # Job-based increases
        if self.current_job:
            job_stats = self.current_job.get_level_stats()
            for stat, value in job_stats.items():
                increases[stat] += value
        
        return increases