from enum import Enum, auto

class StatType(Enum):
    HP = auto()
    MP = auto()
    STRENGTH = auto()
    AGILITY = auto()
    INTELLIGENCE = auto()
    VITALITY = auto()

class DerivedStatType(Enum):
    PHYSICAL_DAMAGE = auto()
    MAGICAL_DAMAGE = auto()
    CRIT_CHANCE = auto()
    CRIT_DAMAGE = auto()
    ATTACK_SPEED = auto()
    CAST_SPEED = auto()
    DODGE_CHANCE = auto()
    BLOCK_CHANCE = auto()
    HP_REGEN = auto()
    MP_REGEN = auto()

# Game balance constants
STAT_SCALING = {
    DerivedStatType.PHYSICAL_DAMAGE: {
        StatType.STRENGTH: 2.5,
        StatType.AGILITY: 1.0
    },
    DerivedStatType.MAGICAL_DAMAGE: {
        StatType.INTELLIGENCE: 3.0
    },
    DerivedStatType.CRIT_CHANCE: {
        StatType.AGILITY: 0.2  # 0.2% per point
    },
    DerivedStatType.CRIT_DAMAGE: {
        StatType.STRENGTH: 0.5,  # 0.5% per point
        StatType.AGILITY: 0.3
    },
    DerivedStatType.ATTACK_SPEED: {
        StatType.AGILITY: 0.3  # 0.3% per point
    },
    DerivedStatType.CAST_SPEED: {
        StatType.INTELLIGENCE: 0.25
    },
    DerivedStatType.DODGE_CHANCE: {
        StatType.AGILITY: 0.15
    },
    DerivedStatType.BLOCK_CHANCE: {
        StatType.VITALITY: 0.2
    },
    DerivedStatType.HP_REGEN: {
        StatType.VITALITY: 0.5
    },
    DerivedStatType.MP_REGEN: {
        StatType.INTELLIGENCE: 0.4
    }
}

# Level scaling
BASE_EXP_REQUIREMENT = 100
EXP_GROWTH_RATE = 1.5
MAX_LEVEL = 100

# Cache settings
CACHE_TTL = 3600  # 1 hour
MAX_CACHE_SIZE = 1000