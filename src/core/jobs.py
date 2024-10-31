from typing import Dict, List
from .skills import Skill
import json  # Ensure this is imported to handle JSON

class Job:
    def __init__(self, name: str, parent: str = None, requirements: Dict = None, base_stats: Dict = None, bonus_stats: Dict = None, skills: List[str] = None):
        self.name = name
        self.parent = parent
        self.requirements = requirements or {}
        self.base_stats = base_stats or {}
        self.bonus_stats = bonus_stats or {}
        self.level = 1
        self.skills: List[Skill] = [Skill(skill) for skill in (skills or [])]  # Assuming Skill can take a skill name
        
    def available_jobs(self) -> List[str]:
        return self.job_paths.get(self.name, [])
    
    def requirements_met(self, character) -> bool:
        if self.parent:
            if character.jobs[self.parent].level < self.requirements["level"]:
                return False
        for stat, value in self.requirements.items():
            if character.stats.get(stat, 0) < value:
                return False
        return True
        
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "level": self.level,
            "skills": [skill.to_dict() for skill in self.skills]
        }

class JobTree:
    def __init__(self):
        self._load_all_jobs()
    
    def _load_all_jobs(self):
        with open('src/assets/data/jobs.json', 'r') as file:
            job_data = json.load(file)

        self.jobs = {}
        self.job_paths = {}
        
        # Load base jobs
        for job in job_data['base_jobs'].values():
            self.jobs[job['name']] = Job(name=job['name'], base_stats=job.get('base_stats', {}), skills=job.get('skills', []))

        # Load first jobs
        for job in job_data['first_jobs'].values():
            # get parent, then map it to the parent job
            parent = job.get('parent')
            if parent:
                self.job_paths[job['name']] = [parent]
            self.jobs[job['name']] = Job(
                name=job['name'],
                requirements=job.get('requirements', {}),
                bonus_stats=job.get('bonus_stats', {}),
                skills=job.get('skills', [])
            )

        # Load advanced jobs
        for job in job_data['advanced_jobs'].values():
            parent = job.get('parent')
            if parent:
                self.job_paths[job['name']] = [parent]
            self.jobs[job['name']] = Job(
                name=job['name'],
                parent=job.get('parent'),
                requirements=job.get('requirements', {}),
                bonus_stats=job.get('bonus_stats', {}),
                skills=job.get('skills', [])
            )
