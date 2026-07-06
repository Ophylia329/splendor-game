"""
玩家类 - 表示游戏玩家
"""
from dataclasses import dataclass, field
from typing import Dict, List
from .card import Card
from .noble import Noble


@dataclass
class Player:
    """
    玩家类

    属性:
        player_id: 玩家编号 (0, 1, 2, 3)
        name: 玩家名称
        gems: 拥有的宝石 {'white': 数量, 'blue': 数量, ..., 'gold': 数量}
        cards: 已购买的发展卡列表
        reserved_cards: 保留的卡牌列表（最多3张）
        nobles: 获得的贵族列表
    """
    player_id: int
    name: str
    gems: Dict[str, int] = field(default_factory=lambda: {
        'white': 0, 'blue': 0, 'green': 0, 'red': 0, 'black': 0, 'gold': 0
    })
    cards: List[Card] = field(default_factory=list)
    reserved_cards: List[Card] = field(default_factory=list)
    nobles: List[Noble] = field(default_factory=list)

    def get_total_gems(self) -> int:
        """获取玩家手上的宝石总数"""
        return sum(self.gems.values())

    def get_bonuses(self) -> Dict[str, int]:
        """
        获取玩家拥有的红利
        红利来自已购买的发展卡

        返回:
            Dict[str, int]: {'white': 数量, 'blue': 数量, ...}
        """
        bonuses = {'white': 0, 'blue': 0, 'green': 0, 'red': 0, 'black': 0}
        for card in self.cards:
            bonuses[card.color] += 1
        return bonuses

    def get_points(self) -> int:
        """
        计算玩家总声望分数
        分数来源：发展卡 + 贵族

        返回:
            int: 总声望分数
        """
        card_points = sum(card.points for card in self.cards)
        noble_points = sum(noble.points for noble in self.nobles)
        return card_points + noble_points

    def can_reserve_card(self) -> bool:
        """检查是否可以保留卡牌（最多3张）"""
        return len(self.reserved_cards) < 3

    def add_gems(self, gems: Dict[str, int]):
        """添加宝石到玩家手上"""
        for color, count in gems.items():
            self.gems[color] += count

    def remove_gems(self, gems: Dict[str, int]):
        """从玩家手上移除宝石"""
        for color, count in gems.items():
            self.gems[color] -= count
            assert self.gems[color] >= 0, f"{color}宝石数量不能为负数"

    def add_card(self, card: Card):
        """添加卡牌到玩家的发展卡中"""
        self.cards.append(card)

    def reserve_card(self, card: Card):
        """保留一张卡牌"""
        if self.can_reserve_card():
            self.reserved_cards.append(card)
        else:
            raise ValueError("已达到保留卡牌上限（3张）")

    def add_noble(self, noble: Noble):
        """获得贵族"""
        self.nobles.append(noble)

    def __repr__(self):
        return f"Player(id={self.player_id}, {self.name}, {self.get_points()}分)"
