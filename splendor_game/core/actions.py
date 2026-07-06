"""
动作执行器 - 执行玩家的游戏动作
"""
from typing import Dict, Optional
from models import Card, Noble, Player, GameState
from .validator import Validator
import config


class ActionExecutor:
    """游戏动作执行器"""

    def __init__(self, validator: Validator):
        """
        初始化动作执行器

        参数:
            validator: 验证器实例
        """
        self.validator = validator

    def take_gems(self, game_state: GameState, gems: Dict[str, int]) -> bool:
        """
        执行拿宝石动作

        参数:
            game_state: 游戏状态
            gems: 要拿取的宝石 {'white': 1, 'blue': 1, ...}

        返回:
            bool: 是否执行成功
        """
        # 验证动作
        valid, error = self.validator.validate_take_gems(game_state, gems)
        if not valid:
            print(f"拿宝石失败: {error}")
            return False

        player = game_state.get_current_player()

        # 从公共区拿取宝石
        for color, count in gems.items():
            if count > 0:
                game_state.gem_bank[color] -= count
                player.gems[color] += count

        print(f"玩家{player.name}拿取了宝石: {gems}")
        return True

    def reserve_card(self, game_state: GameState, card: Card, from_deck: bool = False) -> bool:
        """
        执行保留卡牌动作

        参数:
            game_state: 游戏状态
            card: 要保留的卡牌
            from_deck: 是否从牌堆顶保留

        返回:
            bool: 是否执行成功
        """
        # 验证动作
        valid, error = self.validator.validate_reserve_card(game_state, card, from_deck)
        if not valid:
            print(f"保留卡牌失败: {error}")
            return False

        player = game_state.get_current_player()

        # 保留卡牌
        player.reserve_card(card)

        # 从桌面移除卡牌（如果不是从牌堆顶）
        if not from_deck:
            for level in config.CARD_LEVELS:
                if card in game_state.table_cards[level]:
                    game_state.table_cards[level].remove(card)
                    break

        # 获得1个黄金
        if game_state.gem_bank.get('gold', 0) > 0:
            game_state.gem_bank['gold'] -= 1
            player.gems['gold'] += 1
            print(f"玩家{player.name}保留了卡牌{card}并获得1个黄金")
        else:
            print(f"玩家{player.name}保留了卡牌{card}（无黄金可拿）")

        # 补充桌面卡牌
        if not from_deck:
            game_state.refill_table_cards()

        return True

    def purchase_card(self, game_state: GameState, card: Card, from_reserved: bool = False) -> bool:
        """
        执行购买卡牌动作

        参数:
            game_state: 游戏状态
            card: 要购买的卡牌
            from_reserved: 是否从保留卡中购买

        返回:
            bool: 是否执行成功
        """
        # 验证动作
        valid, error = self.validator.validate_purchase_card(game_state, card)
        if not valid:
            print(f"购买卡牌失败: {error}")
            return False

        player = game_state.get_current_player()
        bonuses = player.get_bonuses()

        # 计算实际花费
        actual_cost = {}
        for color in config.NORMAL_GEM_TYPES:
            cost = card.cost.get(color, 0)
            bonus = bonuses.get(color, 0)
            actual_cost[color] = max(0, cost - bonus)

        # 计算需要支付的宝石（包括黄金）
        payment = {'white': 0, 'blue': 0, 'green': 0, 'red': 0, 'black': 0, 'gold': 0}
        gold_needed = 0

        for color in config.NORMAL_GEM_TYPES:
            needed = actual_cost[color]
            have = player.gems.get(color, 0)

            if have >= needed:
                payment[color] = needed
            else:
                payment[color] = have
                gold_needed += needed - have

        payment['gold'] = gold_needed

        # 支付宝石
        for color, count in payment.items():
            if count > 0:
                player.gems[color] -= count
                game_state.gem_bank[color] += count

        # 获得卡牌
        player.add_card(card)

        # 从桌面或保留区移除卡牌
        if from_reserved:
            player.reserved_cards.remove(card)
        else:
            for level in config.CARD_LEVELS:
                if card in game_state.table_cards[level]:
                    game_state.table_cards[level].remove(card)
                    game_state.refill_table_cards()
                    break

        print(f"玩家{player.name}购买了卡牌{card}，支付: {payment}")
        return True

    def discard_gems(self, player: Player, gems: Dict[str, int], game_state: GameState) -> bool:
        """
        执行弃置宝石动作（当超过10个时）

        参数:
            player: 玩家
            gems: 要弃置的宝石
            game_state: 游戏状态

        返回:
            bool: 是否执行成功
        """
        # 验证动作
        valid, error = self.validator.validate_discard_gems(player, gems)
        if not valid:
            print(f"弃置宝石失败: {error}")
            return False

        # 弃置宝石
        for color, count in gems.items():
            if count > 0:
                player.gems[color] -= count
                game_state.gem_bank[color] += count

        print(f"玩家{player.name}弃置了宝石: {gems}")
        return True

    def award_noble(self, player: Player, noble: Noble, game_state: GameState) -> bool:
        """
        授予玩家贵族

        参数:
            player: 玩家
            noble: 贵族
            game_state: 游戏状态

        返回:
            bool: 是否执行成功
        """
        if noble not in game_state.nobles:
            print(f"贵族{noble}不可用")
            return False

        # 检查是否满足条件
        qualified = self.validator.check_noble_visit(player, [noble])
        if noble not in qualified:
            print(f"玩家{player.name}不满足贵族{noble}的条件")
            return False

        # 授予贵族
        player.add_noble(noble)
        game_state.nobles.remove(noble)

        print(f"贵族{noble}拜访了玩家{player.name}，获得3分！")
        return True

    def check_and_award_nobles(self, game_state: GameState) -> Optional[Noble]:
        """
        检查并自动授予贵族（回合结束时调用）

        规则：每回合最多获得1个贵族

        参数:
            game_state: 游戏状态

        返回:
            Optional[Noble]: 获得的贵族（如果有）
        """
        player = game_state.get_current_player()
        qualified = self.validator.check_noble_visit(player, game_state.nobles)

        if not qualified:
            return None

        # 如果有多个贵族满足条件，让玩家选择第一个（简化处理）
        # 实际游戏中应该让玩家自己选择
        noble = qualified[0]
        self.award_noble(player, noble, game_state)
        return noble
