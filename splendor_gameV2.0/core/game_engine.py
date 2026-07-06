"""
游戏引擎 - 控制游戏流程和状态管理
"""
import random
from typing import List, Optional
from models import Card, Noble, Player, GameState
from .validator import Validator
from .actions import ActionExecutor
from utils import (
    load_cards_from_csv,
    load_cards_from_excel,
    load_nobles_from_csv,
    load_nobles_from_excel,
    get_mock_cards,
    get_mock_nobles,
    shuffle_cards,
    shuffle_nobles
)
import config


class GameEngine:
    """游戏引擎"""

    def __init__(self, num_players: int, player_names: List[str] = None):
        """
        初始化游戏引擎

        参数:
            num_players: 玩家数量 (2/3/4)
            player_names: 玩家名称列表（可选）
        """
        assert num_players in [2, 3, 4], "玩家数量必须是2、3或4"

        self.validator = Validator()
        self.executor = ActionExecutor(self.validator)

        # 创建游戏状态
        self.game_state = GameState(num_players=num_players)

        # 初始化游戏
        self._initialize_game(player_names)

    def _initialize_game(self, player_names: List[str] = None):
        """
        初始化游戏

        参数:
            player_names: 玩家名称列表
        """
        num_players = self.game_state.num_players

        # 1. 创建玩家
        if player_names is None:
            player_names = [f"玩家{i+1}" for i in range(num_players)]

        for i in range(num_players):
            player = Player(player_id=i, name=player_names[i])
            self.game_state.players.append(player)

        # 2. 初始化宝石供应区
        self.game_state.gem_bank = config.MAX_GEMS_TOTAL[num_players].copy()

        # 3. 加载卡牌数据
        cards = self._load_cards()
        self.game_state.card_decks = shuffle_cards(cards)

        # 4. 初始化桌面卡牌
        self.game_state.table_cards = {1: [], 2: [], 3: []}
        self.game_state.refill_table_cards()

        # 5. 加载贵族数据
        nobles = self._load_nobles()
        shuffled_nobles = shuffle_nobles(nobles)

        # 根据人数选择贵族
        nobles_count = config.NOBLES_COUNT[num_players]
        self.game_state.nobles = shuffled_nobles[:nobles_count]

        # 6. 随机选择起始玩家
        self.game_state.current_player_idx = random.randint(0, num_players - 1)

        print(f"\n{'='*50}")
        print(f"游戏初始化完成！")
        print(f"玩家数量: {num_players}")
        print(f"玩家列表: {[p.name for p in self.game_state.players]}")
        print(f"起始玩家: {self.game_state.get_current_player().name}")
        print(f"贵族数量: {len(self.game_state.nobles)}")
        print(f"{'='*50}\n")

    def _load_cards(self) -> List[Card]:
        """
        加载卡牌数据
        优先从CSV加载（更快），其次Excel，最后使用测试数据

        返回:
            List[Card]: 卡牌列表
        """
        import os

        # 优先从CSV加载（更快，无需依赖openpyxl）
        if os.path.exists(config.CARDS_CSV):
            try:
                cards = load_cards_from_csv(config.CARDS_CSV)
                print(f"[OK] 从CSV加载了{len(cards)}张卡牌")
                return cards
            except Exception as e:
                print(f"从CSV加载失败: {e}")

        # 尝试从Excel加载（发展牌整合.xlsx）
        excel_path = os.path.join(config.DATA_DIR, "发展牌整合.xlsx")
        if os.path.exists(excel_path):
            try:
                cards = load_cards_from_excel(excel_path)
                print(f"[OK] 从Excel加载了{len(cards)}张卡牌")
                return cards
            except Exception as e:
                print(f"从Excel加载失败: {e}")

        # 使用测试数据
        print("[WARNING] 使用测试数据（24张卡牌）")
        return get_mock_cards()

    def _load_nobles(self) -> List[Noble]:
        """
        加载贵族数据
        优先从CSV加载（更快），其次Excel，最后使用测试数据

        返回:
            List[Noble]: 贵族列表
        """
        import os

        # 优先从CSV加载（更快，无需依赖openpyxl）
        if os.path.exists(config.NOBLES_CSV):
            try:
                nobles = load_nobles_from_csv(config.NOBLES_CSV)
                print(f"[OK] 从CSV加载了{len(nobles)}个贵族")
                return nobles
            except Exception as e:
                print(f"从CSV加载失败: {e}")

        # 尝试从Excel加载（贵族.xlsx）
        excel_path = os.path.join(config.DATA_DIR, "贵族.xlsx")
        if os.path.exists(excel_path):
            try:
                nobles = load_nobles_from_excel(excel_path)
                print(f"[OK] 从Excel加载了{len(nobles)}个贵族")
                return nobles
            except Exception as e:
                print(f"从Excel加载失败: {e}")

        # 使用测试数据
        print("[WARNING] 使用测试数据（10个贵族）")
        return get_mock_nobles()

    def take_gems_action(self, gems: dict) -> bool:
        """
        执行拿宝石动作

        参数:
            gems: 要拿取的宝石 {'white': 1, 'blue': 1, ...}

        返回:
            bool: 是否成功
        """
        return self.executor.take_gems(self.game_state, gems)

    def reserve_card_action(self, card: Card, from_deck: bool = False) -> bool:
        """
        执行保留卡牌动作

        参数:
            card: 要保留的卡牌
            from_deck: 是否从牌堆顶保留

        返回:
            bool: 是否成功
        """
        return self.executor.reserve_card(self.game_state, card, from_deck)

    def reserve_card_from_deck(self, level: int) -> bool:
        """
        从牌堆顶保留卡牌

        参数:
            level: 牌堆等级（1/2/3）

        返回:
            bool: 是否成功
        """
        # 检查牌堆是否有卡
        if level not in self.game_state.card_decks or len(self.game_state.card_decks[level]) == 0:
            print(f"等级{level}牌堆已空")
            return False

        # 从牌堆顶抽一张卡
        card = self.game_state.card_decks[level][-1]  # 取最后一张（堆顶）

        # 执行保留动作
        return self.executor.reserve_card(self.game_state, card, from_deck=True)

    def purchase_card_action(self, card: Card, from_reserved: bool = False) -> bool:
        """
        执行购买卡牌动作

        参数:
            card: 要购买的卡牌
            from_reserved: 是否从保留卡购买

        返回:
            bool: 是否成功
        """
        return self.executor.purchase_card(self.game_state, card, from_reserved)

    def end_turn(self) -> List[Noble]:
        """
        结束当前回合（第一阶段：检查贵族）

        流程：
        1. 检查是否需要弃置宝石
        2. 检查贵族拜访（返回符合条件的贵族列表）
        3. 界面层处理贵族选择
        4. 调用 complete_turn() 完成回合切换

        返回:
            List[Noble]: 符合条件的贵族列表（让玩家选择）
        """
        player = self.game_state.get_current_player()

        # 1. 检查宝石是否超过10个（界面层处理弃置）
        if player.get_total_gems() > config.MAX_HAND_GEMS:
            print(f"警告: 玩家{player.name}的宝石超过{config.MAX_HAND_GEMS}个，需要弃置")
            return []  # 需要先弃置宝石

        # 2. 检查贵族拜访（返回所有符合条件的贵族）
        qualified_nobles = self.executor.check_and_award_nobles(self.game_state)

        return qualified_nobles

    def complete_turn(self, selected_noble: Optional[Noble] = None):
        """
        完成回合切换（第二阶段：授予贵族并切换玩家）

        参数:
            selected_noble: 玩家选择的贵族（如果有）
        """
        player = self.game_state.get_current_player()

        # 授予玩家选择的贵族
        if selected_noble:
            self.executor.award_noble(player, selected_noble, self.game_state)

        # 检查胜利条件
        self.game_state.check_win_condition()

        # 切换玩家
        self.game_state.next_player()

    def is_game_over(self) -> bool:
        """
        检查游戏是否结束

        返回:
            bool: 游戏是否结束
        """
        return self.game_state.game_over

    def get_winner(self) -> Optional[Player]:
        """
        获取获胜者

        返回:
            Optional[Player]: 获胜玩家
        """
        return self.game_state.get_winner()

    def get_current_player(self) -> Player:
        """获取当前玩家"""
        return self.game_state.get_current_player()

    def get_game_state(self) -> GameState:
        """获取游戏状态"""
        return self.game_state

    def print_game_state(self):
        """打印当前游戏状态（调试用）"""
        print(f"\n{'='*50}")
        print(f"当前回合: {self.game_state.get_current_player().name}")
        print(f"最后一轮: {self.game_state.final_round}")
        print(f"游戏结束: {self.game_state.game_over}")
        print(f"\n公共宝石:")
        for color, count in self.game_state.gem_bank.items():
            print(f"  {color}: {count}")

        print(f"\n桌面卡牌:")
        for level in config.CARD_LEVELS:
            print(f"  等级{level}: {len(self.game_state.table_cards[level])}张")

        print(f"\n可用贵族: {len(self.game_state.nobles)}个")

        print(f"\n玩家状态:")
        for player in self.game_state.players:
            bonuses = player.get_bonuses()
            print(f"  {player.name}: {player.get_points()}分, "
                  f"宝石{player.get_total_gems()}个, "
                  f"卡牌{len(player.cards)}张, "
                  f"保留{len(player.reserved_cards)}张, "
                  f"贵族{len(player.nobles)}个")
            print(f"    红利: {bonuses}")

        print(f"{'='*50}\n")
