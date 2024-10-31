from typing import Dict, List

class Skill:
    def __init__(self, name: str, requirements: Dict):
        self.name = name
        self.requirements = requirements
        self.level = 1
        self.damage = 10
        self.mp_cost = 5
        
    def can_learn(self, character) -> bool:
        for stat, value in self.requirements.items():
            if character.stats.get(stat, 0) < value:
                return False
        return True
        
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "level": self.level,
            "damage": self.damage,
            "mp_cost": self.mp_cost
        }

class SkillTree:
    def __init__(self):
        self.skills = {
            "Basic Attack": Skill("Basic Attack", {}),
            "Fireball": Skill("Fireball", {"intelligence": 20}),
            "Double Strike": Skill("Double Strike", {"agility": 20}),
            "Heal": Skill("Heal", {"vitality": 20}),
        }
        self.skill_paths = {
            "Fireball": ["Fire Storm", "Meteor"],
            "Double Strike": ["Triple Strike", "Shadow Strike"],
            "Heal": ["Greater Heal", "Mass Heal"]
        }