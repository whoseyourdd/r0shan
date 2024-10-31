from typing import Dict, List, Optional
import json
import random

class CraftingSystem:
    def __init__(self):
        with open('game/data/crafting.json', 'r') as f:
            self.data = json.load(f)
            
    def can_craft(self, recipe_id: str, materials: Dict[str, int], 
                  crafting_skills: Dict[str, int]) -> bool:
        recipe = self._get_recipe(recipe_id)
        if not recipe:
            return False
            
        # Check materials
        for material, amount in recipe['materials'].items():
            if materials.get(material, 0) < amount:
                return False
                
        # Check skill requirements
        for skill, level in recipe['skill_req'].items():
            if crafting_skills.get(skill, 0) < level:
                return False
                
        return True
        
    def craft_item(self, recipe_id: str, materials: Dict[str, int],
                   crafting_skills: Dict[str, int]) -> Optional[Dict]:
        if not self.can_craft(recipe_id, materials):
            return None
            
        recipe = self._get_recipe(recipe_id)
        result = recipe['result'].copy()
        
        # Apply crafting skill bonuses
        for skill, level in crafting_skills.items():
            if skill in self.data['crafting_skills']:
                bonuses = self.data['crafting_skills'][skill]['level_bonuses']
                for stat, bonus in bonuses.items():
                    if stat in result['stats']:
                        result['stats'][stat] += bonus * level
                        
        # Consume materials
        for material, amount in recipe['materials'].items():
            materials[material] -= amount
            
        return result
        
    def enhance_item(self, item: Dict, enhancement_stone: str) -> Dict:
        if 'enhancement' not in item:
            item['enhancement'] = 0
            
        stone_data = self.data['enhancement']['materials'][enhancement_stone]
        rules = self.data['enhancement']['rules']
        
        # Check if enhancement is possible
        if item['enhancement'] >= rules['max_level']:
            return {'success': False, 'reason': 'max_level_reached'}
            
        # Calculate success rate
        base_rate = stone_data['success_rate']
        level_penalty = rules['level_penalty'] * item['enhancement']
        success_rate = base_rate - level_penalty
        
        # Roll for success
        if random.random() * 100 < success_rate:
            item['enhancement'] += 1
            self._apply_enhancement_bonuses(item)
            return {'success': True, 'item': item}
        else:
            # Handle failure
            item['durability'] -= rules['fail_penalty']['durability']
            if item['enhancement'] >= rules['fail_penalty']['destroy_chance']['threshold']:
                if random.random() * 100 < rules['fail_penalty']['destroy_chance']['chance']:
                    return {'success': False, 'reason': 'item_destroyed'}
            return {'success': False, 'reason': 'enhance_failed', 'item': item}
            
    def _get_recipe(self, recipe_id: str) -> Optional[Dict]:
        for category in self.data['recipes']:
            if recipe_id in self.data['recipes'][category]:
                return self.data['recipes'][category][recipe_id]
        return None
        
    def _apply_enhancement_bonuses(self, item: Dict) -> None:
        item_type = item['type']
        level = item['enhancement']
        
        # Apply per-level bonuses
        per_level = self.data['enhancement']['bonuses'][item_type]['per_level']
        for stat, bonus in per_level.items():
            if stat not in item['stats']:
                item['stats'][stat] = 0
            item['stats'][stat] += bonus
            
        # Apply threshold bonuses
        thresholds = self.data['enhancement']['bonuses'][item_type]['thresholds']
        for threshold, bonuses in thresholds.items():
            if level >= int(threshold):
                for stat, bonus in bonuses.items():
                    if stat not in item['stats']:
                        item['stats'][stat] = 0
                    item['stats'][stat] += bonus