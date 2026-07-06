"""
游戏状态类 - 管理整个游戏的状态
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .card import Card
from .noble import Noble
from .player import Player
import config


@dataclass
class GameState:
    """
    游戏状态类

    属性:
        num_players: 玩家数量 (2/3/4)
        players: 玩家列表
        current_player_idx: 当前玩家索引
        gem_bank: 公共宝石供应区 {'white': 数量, ...}
        card_decks: 三个等级的牌堆 {1: [Card, ...], 2: [...], 3: [...]}
        table_cards: 桌面展示的卡牌 {1: [Card, ...], 2: [...], 3: [...]}
        nobles: 可用的贵族列表
        game_over: 游戏是否结束
        final_round: 是否进入最后一轮
        trigger_player_idx: 触发结束的玩家索引
    """
    num_players: int
    players: List[Player] = field(default_factory=list)
    current_player_idx: int = 0
    gem_bank: Dict[str, int] = field(default_factory=dict)
    card_decks: Dict[int, List[Card]] = field(default_factory=dict)
    table_cards: Dict[int, List[Card]] = field(default_factory=dict)
    nobles: List[Noble] = field(default_factory=list)
    game_over: bool = False
    final_round: bool = False
    trigger_player_idx: Optional[int] = None

    def __post_init__(self):
        """初始化验证"""
        assert self.num_players in [2, 3, 4], \
            f"玩家数量必须是2、3或4，当前为{self.num_players}"

    def get_current_player(self) -> Player:
        """获取当前回合的玩家"""
        return self.players[self.current_player_idx]

    def next_player(self):
        """切换到下一个玩家"""
        self.current_player_idx = (self.current_player_idx + 1) % self.num_players

        # 检查是否完成最后一轮
        if self.final_round and self.current_player_idx == self.trigger_player_idx:
            self.game_over = True

    def check_win_condition(self):
        """
        检查是否有玩家达到胜利条件（15分）
        如果有，触发最后一轮
        """
        current_player = self.get_current_player()
        if current_player.get_points() >= config.WIN_POINTS and not self.final_round:
            self.final_round = True
            self.trigger_player_idx = self.current_player_idx

    def get_winner(self) -> Optional[Player]:
        """
        获取获胜者
        规则：分数最高者获胜；平局时发展卡最少者获胜

        返回:
            Player: 获胜玩家，如果游戏未结束返回None
        """
        if not self.game_over:
            return None

        # 按分数排序，分数相同则按卡牌数量排序
        sorted_players = sorted(
            self.players,
            key=lambda p: (p.get_points(), -len(p.cards)),
            reverse=True
        )
        return sorted_players[0]

    def refill_table_cards(self):
        """补充桌面的卡牌到4张"""
        for level in config.CARD_LEVELS:
            while len(self.table_cards[level]) < config.CARDS_ON_TABLE and self.card_decks[level]:
                card = self.card_decks[level].pop(0)
                self.table_cards[level].append(card)

    def __repr__(self):
        return f"GameState(Players={self.num_players}, Round={self.current_player_idx}, " \
               f"FinalRound={self.final_round}, GameOver={self.game_over})"
