"""
卡牌类 - 表示发展卡
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class Card:
    """
    发展卡类

    属性:
        card_id: 卡牌唯一标识
        level: 卡牌等级 (1/2/3)
        color: 红利颜色 (white/blue/green/red/black)
        cost: 购买花费 {'white': 数量, 'blue': 数量, ...}
        points: 声望分数
    """
    card_id: int
    level: int
    color: str
    cost: Dict[str, int]
    points: int

    def __post_init__(self):
        """初始化后验证数据"""
        assert self.level in [1, 2, 3], f"卡牌等级必须是1、2或3，当前为{self.level}"
        assert self.color in ['white', 'blue', 'green', 'red', 'black'], \
            f"卡牌颜色必须是white/blue/green/red/black之一，当前为{self.color}"
        assert self.points >= 0, f"声望分数不能为负数，当前为{self.points}"

    def get_total_cost(self) -> int:
        """计算卡牌总花费"""
        return sum(self.cost.values())

    def __repr__(self):
        return f"Card(id={self.card_id}, L{self.level}, {self.color}, {self.points}分)"
