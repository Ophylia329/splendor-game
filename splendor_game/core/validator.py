"""
动作验证器 - 验证玩家动作的合法性
"""
from typing import Dict, List, Tuple
from models import Card, Player, GameState
import config


class Validator:
    """游戏动作验证器"""

    @staticmethod
    def validate_take_gems(game_state: GameState, gems: Dict[str, int]) -> Tuple[bool, str]:
        """
        验证拿宝石动作的合法性

        规则：
        1. 拿3个不同颜色的宝石（不能是黄金）
        2. 拿2个相同颜色的宝石（该颜色至少有4个）
        3. 不能拿黄金
        4. 回合结束后宝石总数不超过10个

        参数:
            game_state: 游戏状态
            gems: 要拿取的宝石 {'white': 1, 'blue': 1, ...}

        返回:
            Tuple[bool, str]: (是否合法, 错误信息)
        """
        player = game_state.get_current_player()
        gem_bank = game_state.gem_bank

        # 计算拿取的宝石数量
        total_take = sum(gems.values())
        colors_taken = [color for color, count in gems.items() if count > 0]

        # 规则1：不能拿黄金
        if gems.get('gold', 0) > 0:
            return False, "不能通过拿取宝石行动获得黄金"

        # 规则2：只能拿取普通颜色的宝石
        for color in colors_taken:
            if color not in config.NORMAL_GEM_TYPES:
                return False, f"不能拿取{color}类型的宝石"

        # 规则3：检查是拿3个不同还是2个相同
        if total_take == 3:
            # 拿3个不同颜色
            if len(colors_taken) != 3:
                return False, "拿3个宝石时必须是3种不同颜色"

            for color in colors_taken:
                if gems[color] != 1:
                    return False, "拿3个不同颜色时，每种颜色只能拿1个"

                if gem_bank.get(color, 0) < 1:
                    return False, f"{color}宝石不足"

        elif total_take == 2:
            # 拿2个相同颜色
            if len(colors_taken) != 1:
                return False, "拿2个宝石时必须是同一种颜色"

            color = colors_taken[0]
            if gems[color] != 2:
                return False, "拿2个相同颜色时，必须拿取2个"

            # 该颜色至少有4个才能拿2个
            if gem_bank.get(color, 0) < 4:
                return False, f"{color}宝石少于4个，不能拿取2个"

        else:
            return False, f"只能拿2个或3个宝石，当前拿取{total_take}个"

        # 规则4：检查拿取后是否超过10个
        player_total = player.get_total_gems()
        if player_total + total_take > config.MAX_HAND_GEMS:
            return False, f"拿取后宝石总数将超过{config.MAX_HAND_GEMS}个（当前{player_total}个）"

        return True, ""

    @staticmethod
    def validate_reserve_card(game_state: GameState, card: Card, from_deck: bool = False) -> Tuple[bool, str]:
        """
        验证保留卡牌动作的合法性

        规则：
        1. 最多保留3张卡牌
        2. 可以从桌面或牌堆顶保留
        3. 保留时获得1个黄金（如果有）

        参数:
            game_state: 游戏状态
            card: 要保留的卡牌
            from_deck: 是否从牌堆顶保留

        返回:
            Tuple[bool, str]: (是否合法, 错误信息)
        """
        player = game_state.get_current_player()

        # 规则1：检查保留卡数量
        if len(player.reserved_cards) >= config.MAX_RESERVED_CARDS:
            return False, f"已达到保留卡上限（{config.MAX_RESERVED_CARDS}张）"

        # 规则2：检查卡牌是否存在
        if not from_deck:
            # 从桌面保留
            found = False
            for level in config.CARD_LEVELS:
                if card in game_state.table_cards[level]:
                    found = True
                    break

            if not found:
                return False, "该卡牌不在桌面上"

        # 规则3：检查拿黄金后是否超过10个
        if game_state.gem_bank.get('gold', 0) > 0:
            player_total = player.get_total_gems()
            if player_total + 1 > config.MAX_HAND_GEMS:
                return False, f"拿取黄金后宝石总数将超过{config.MAX_HAND_GEMS}个"

        return True, ""

    @staticmethod
    def validate_purchase_card(game_state: GameState, card: Card) -> Tuple[bool, str]:
        """
        验证购买卡牌动作的合法性

        规则：
        1. 必须有足够的宝石（考虑红利和黄金）
        2. 可以购买桌面或保留的卡牌

        参数:
            game_state: 游戏状态
            card: 要购买的卡牌

        返回:
            Tuple[bool, str]: (是否合法, 错误信息)
        """
        player = game_state.get_current_player()
        bonuses = player.get_bonuses()

        # 计算实际花费（扣除红利）
        actual_cost = {}
        for color in config.NORMAL_GEM_TYPES:
            cost = card.cost.get(color, 0)
            bonus = bonuses.get(color, 0)
            actual_cost[color] = max(0, cost - bonus)

        # 检查是否有足够的宝石（包括黄金）
        shortage = 0
        for color in config.NORMAL_GEM_TYPES:
            needed = actual_cost[color]
            have = player.gems.get(color, 0)
            if have < needed:
                shortage += needed - have

        # 检查黄金是否足够
        gold_available = player.gems.get('gold', 0)
        if shortage > gold_available:
            return False, f"宝石不足，缺少{shortage}个，但只有{gold_available}个黄金"

        return True, ""

    @staticmethod
    def validate_discard_gems(player: Player, gems: Dict[str, int]) -> Tuple[bool, str]:
        """
        验证弃置宝石的合法性

        规则：
        1. 回合结束时宝石总数不能超过10个
        2. 必须弃置到正好10个

        参数:
            player: 玩家
            gems: 要弃置的宝石

        返回:
            Tuple[bool, str]: (是否合法, 错误信息)
        """
        current_total = player.get_total_gems()
        discard_total = sum(gems.values())

        # 检查是否需要弃置
        if current_total <= config.MAX_HAND_GEMS:
            return False, "当前宝石总数未超过上限，无需弃置"

        # 检查弃置的宝石是否拥有
        for color, count in gems.items():
            if player.gems.get(color, 0) < count:
                return False, f"{color}宝石不足，无法弃置{count}个"

        # 检查弃置后是否正好10个
        if current_total - discard_total != config.MAX_HAND_GEMS:
            return False, f"必须弃置到正好{config.MAX_HAND_GEMS}个宝石"

        return True, ""

    @staticmethod
    def check_noble_visit(player: Player, nobles: List) -> List:
        """
        检查哪些贵族可以拜访玩家

        规则：
        1. 玩家的红利必须满足贵族要求
        2. 每回合最多获得1个贵族

        参数:
            player: 玩家
            nobles: 可用的贵族列表

        返回:
            List: 满足条件的贵族列表
        """
        bonuses = player.get_bonuses()
        qualified_nobles = []

        for noble in nobles:
            if noble.check_requirements(bonuses):
                qualified_nobles.append(noble)

        return qualified_nobles
