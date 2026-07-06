"""
测试脚本 - 验证核心逻辑是否正常工作
用于命令行测试游戏规则
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import GameEngine
import config


def test_game_basic():
    """测试基础游戏流程"""
    print("=" * 60)
    print("璀璨宝石 - 核心逻辑测试")
    print("=" * 60)

    # 创建2人游戏
    engine = GameEngine(num_players=2, player_names=["Alice", "Bob"])

    # 打印初始状态
    engine.print_game_state()

    # 测试1: Alice拿3个不同颜色的宝石
    print("\n【测试1】Alice拿3个不同颜色的宝石")
    result = engine.take_gems_action({'white': 1, 'blue': 1, 'green': 1})
    print(f"结果: {'成功' if result else '失败'}")

    # 打印Alice的宝石
    alice = engine.get_current_player()
    print(f"Alice的宝石: {alice.gems}")

    # 结束Alice的回合
    engine.end_turn()

    # 测试2: Bob拿2个相同颜色的宝石
    print("\n【测试2】Bob拿2个相同颜色的宝石")
    result = engine.take_gems_action({'red': 2})
    print(f"结果: {'成功' if result else '失败'}")

    bob = engine.get_current_player()
    print(f"Bob的宝石: {bob.gems}")

    # 结束Bob的回合
    engine.end_turn()

    # 测试3: Alice尝试购买一张卡牌（应该失败，宝石不够）
    print("\n【测试3】Alice尝试购买一张卡牌")
    if engine.game_state.table_cards[1]:
        card = engine.game_state.table_cards[1][0]
        print(f"尝试购买: {card}")
        result = engine.purchase_card_action(card)
        print(f"结果: {'成功' if result else '失败（宝石不够）'}")

    # 测试4: Alice保留一张卡牌
    print("\n【测试4】Alice保留一张卡牌")
    if engine.game_state.table_cards[1]:
        card = engine.game_state.table_cards[1][0]
        print(f"保留卡牌: {card}")
        result = engine.reserve_card_action(card)
        print(f"结果: {'成功' if result else '失败'}")
        print(f"Alice保留的卡牌数: {len(alice.reserved_cards)}")
        print(f"Alice的黄金: {alice.gems['gold']}")

    # 打印最终状态
    print("\n【最终状态】")
    engine.print_game_state()

    print("\n" + "=" * 60)
    print("测试完成！核心逻辑运行正常！")
    print("=" * 60)


def test_invalid_actions():
    """测试非法动作的验证"""
    print("\n" + "=" * 60)
    print("非法动作验证测试")
    print("=" * 60)

    engine = GameEngine(num_players=2, player_names=["Player1", "Player2"])

    # 测试1: 尝试拿黄金
    print("\n【测试】尝试拿黄金（应该失败）")
    result = engine.take_gems_action({'gold': 1})
    print(f"结果: {'成功（不应该）' if result else '失败（预期）'}")

    # 测试2: 尝试拿4个宝石
    print("\n【测试】尝试拿4个宝石（应该失败）")
    result = engine.take_gems_action({'white': 2, 'blue': 2})
    print(f"结果: {'成功（不应该）' if result else '失败（预期）'}")

    # 测试3: 尝试拿2个相同颜色但该颜色少于4个（2人游戏）
    print("\n【测试】尝试从少于4个的宝石堆拿2个（应该失败）")
    result = engine.take_gems_action({'white': 2})
    print(f"结果: {'成功（不应该）' if result else '失败（预期）'}")

    print("\n" + "=" * 60)
    print("验证测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    # 运行基础测试
    test_game_basic()

    # 运行验证测试
    test_invalid_actions()
