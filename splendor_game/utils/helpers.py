"""
辅助工具函数
"""
import random
from typing import List, Dict
from models import Card, Noble, Player
import config


def shuffle_cards(cards: List[Card]) -> Dict[int, List[Card]]:
    """
    将卡牌按等级分类并洗牌

    参数:
        cards: 所有卡牌列表

    返回:
        Dict[int, List[Card]]: {1: [卡牌...], 2: [卡牌...], 3: [卡牌...]}
    """
    decks = {1: [], 2: [], 3: []}

    # 按等级分类
    for card in cards:
        decks[card.level].append(card)

    # 分别洗牌
    for level in config.CARD_LEVELS:
        random.shuffle(decks[level])

    return decks


def shuffle_nobles(nobles: List[Noble]) -> List[Noble]:
    """
    洗混贵族列表

    参数:
        nobles: 贵族列表

    返回:
        List[Noble]: 洗混后的贵族列表
    """
    shuffled = nobles.copy()
    random.shuffle(shuffled)
    return shuffled


def calculate_actual_cost(card_cost: Dict[str, int], bonuses: Dict[str, int]) -> Dict[str, int]:
    """
    计算购买卡牌的实际花费（扣除红利后）

    参数:
        card_cost: 卡牌原始花费 {'white': 3, 'blue': 2, ...}
        bonuses: 玩家红利 {'white': 1, 'blue': 0, ...}

    返回:
        Dict[str, int]: 实际需要支付的宝石 {'white': 2, 'blue': 2, ...}
    """
    actual_cost = {}
    for color in config.NORMAL_GEM_TYPES:
        cost = card_cost.get(color, 0)
        bonus = bonuses.get(color, 0)
        actual_cost[color] = max(0, cost - bonus)
    return actual_cost


def can_afford(player: Player, card: Card) -> bool:
    """
    检查玩家是否有足够的资源购买卡牌（考虑红利和黄金）

    参数:
        player: 玩家对象
        card: 卡牌对象

    返回:
        bool: 是否能够购买
    """
    bonuses = player.get_bonuses()
    actual_cost = calculate_actual_cost(card.cost, bonuses)

    # 计算缺少的宝石数量
    shortage = 0
    for color in config.NORMAL_GEM_TYPES:
        needed = actual_cost[color]
        have = player.gems.get(color, 0)
        if have < needed:
            shortage += needed - have

    # 检查黄金是否足够补足
    return shortage <= player.gems.get('gold', 0)


def calculate_payment(player: Player, card: Card) -> Dict[str, int]:
    """
    计算购买卡牌需要支付的宝石（包括黄金的使用）

    参数:
        player: 玩家对象
        card: 卡牌对象

    返回:
        Dict[str, int]: 需要支付的宝石 {'white': 1, 'gold': 2, ...}
    """
    bonuses = player.get_bonuses()
    actual_cost = calculate_actual_cost(card.cost, bonuses)

    payment = {'white': 0, 'blue': 0, 'green': 0, 'red': 0, 'black': 0, 'gold': 0}
    gold_needed = 0

    # 计算每种颜色需要支付的数量
    for color in config.NORMAL_GEM_TYPES:
        needed = actual_cost[color]
        have = player.gems.get(color, 0)

        if have >= needed:
            payment[color] = needed
        else:
            payment[color] = have
            gold_needed += needed - have

    # 使用黄金补足
    payment['gold'] = gold_needed

    return payment


def format_gems(gems: Dict[str, int]) -> str:
    """
    格式化宝石字典为可读字符串

    参数:
        gems: 宝石字典 {'white': 2, 'blue': 1, ...}

    返回:
        str: 格式化字符串，如 "白2 蓝1"
    """
    gem_names = {
        'white': '白',
        'blue': '蓝',
        'green': '绿',
        'red': '红',
        'black': '黑',
        'gold': '金'
    }

    parts = []
    for color, count in gems.items():
        if count > 0:
            parts.append(f"{gem_names[color]}{count}")

    return " ".join(parts) if parts else "无"


def get_gem_name(color: str) -> str:
    """
    获取宝石颜色的中文名称

    参数:
        color: 颜色代码 ('white', 'blue', ...)

    返回:
        str: 中文名称
    """
    names = {
        'white': '钻石(白)',
        'blue': '蓝宝石(蓝)',
        'green': '翡翠(绿)',
        'red': '红宝石(红)',
        'black': '绿玛瑙(黑)',
        'gold': '黄金'
    }
    return names.get(color, color)
