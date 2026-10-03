import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class SkillSystem:
    def __init__(self, db_manager):
        self.db = db_manager
        self.skills = {
            'coding': {'level': 1, 'experience': 0},
            'trading': {'level': 1, 'experience': 0},
            'content_creation': {'level': 1, 'experience': 0},
            'research': {'level': 1, 'experience': 0},
            'automation': {'level': 1, 'experience': 0},
        }

    def gain_experience(self, skill: str, amount: float):
        if skill not in self.skills:
            self.skills[skill] = {'level': 1, 'experience': 0}
        self.skills[skill]['experience'] += amount
        new_level = int(self.skills[skill]['experience'] / 100) + 1
        self.skills[skill]['level'] = new_level

    def get_all_skills(self):
        return self.skills


class LearningSystem:
    def __init__(self, db_manager):
        self.db = db_manager

    def learn_from_trade(self, trade_result: Dict):
        self.db.save_memory(f"trade_{trade_result.get('symbol')}", trade_result)

    def learn_from_code(self, code_result: Dict):
        if code_result.get('success'):
            self.db.save_memory('successful_code_pattern', code_result)

    def get_improvement_suggestions(self):
        return [
            'Improve risk management',
            'Review strategy quality',
            'Increase data quality checks',
            'Add stronger automation safeguards',
        ]


class FeatureLockSystem:
    def __init__(self, db_manager):
        self.db = db_manager
        self.locked_features = {
            'coding': {'locked': False, 'offline': False},
            'trading': {'locked': False, 'offline': False},
            'content': {'locked': False, 'offline': False},
            'research': {'locked': False, 'offline': False},
            'automation': {'locked': False, 'offline': False},
        }

    def lock_feature(self, feature: str):
        self.locked_features[feature] = {'locked': True, 'offline': True, 'locked_at': datetime.now().isoformat()}

    def unlock_feature(self, feature: str):
        if feature in self.locked_features:
            self.locked_features[feature]['locked'] = False
            self.locked_features[feature]['offline'] = False

    def is_feature_locked(self, feature: str) -> bool:
        return bool(self.locked_features.get(feature, {}).get('locked', False))

