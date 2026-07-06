"""
事件处理器 - 处理游戏交互逻辑
"""
import pygame
from typing import Optional, Dict, List
from models import Card, GameState
from core import GameEngine
from ui import Renderer, Button
import config


class GameAction:
    """游戏动作枚举"""
    TAKE_GEMS = "take_gems"
    RESERVE_CARD = "reserve_card"
    PURCHASE_CARD = "purchase_card"


class EventHandler:
    """事件处理器"""

    def __init__(self, game_engine: GameEngine, renderer: Renderer):
        """
        初始化事件处理器

        参数:
            game_engine: 游戏引擎
            renderer: 渲染器
        """
        self.game_engine = game_engine
        self.renderer = renderer

        # 当前动作状态
        self.current_action = None
        self.selected_gems = {}  # 选中的宝石 {'white': 1, ...}
        self.selected_card = None  # 选中的卡牌

        # UI按钮
        self.buttons = self._create_buttons()

        # 字体（使用中文字体）
        from .renderer import get_chinese_font
        self.font_small = get_chinese_font(config.FONT_SIZE_SMALL)
        self.font_medium = get_chinese_font(config.FONT_SIZE_MEDIUM)

    def _create_buttons(self) -> Dict[str, Button]:
        """创建UI按钮"""
        buttons = {}

        # 动作按钮（屏幕右侧）
        btn_x = config.WINDOW_WIDTH - 180
        btn_y = 250

        buttons['take_gems'] = Button(btn_x, btn_y, 160, 50, "拿取宝石")
        buttons['reserve_card'] = Button(btn_x, btn_y + 60, 160, 50, "保留卡牌")
        buttons['purchase_card'] = Button(btn_x, btn_y + 120, 160, 50, "购买卡牌")
        buttons['end_turn'] = Button(btn_x, btn_y + 200, 160, 50, "结束回合")
        buttons['cancel'] = Button(btn_x, btn_y + 260, 160, 50, "取消")

        # 确认按钮（屏幕中下方）
        buttons['confirm'] = Button(
            config.WINDOW_WIDTH // 2 - 80,
            config.WINDOW_HEIGHT - 300,
            160, 50, "确认动作"
        )

        return buttons

    def handle_events(self, events: List[pygame.event.Event]) -> bool:
        """
        处理事件列表

        参数:
            events: pygame事件列表

        返回:
            bool: 是否需要重新渲染
        """
        need_render = False

        for event in events:
            if event.type == pygame.QUIT:
                return False

            # 处理按钮点击
            for btn_name, btn in self.buttons.items():
                if btn.handle_event(event):
                    self._handle_button_click(btn_name)
                    need_render = True

            # 处理游戏内点击
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._handle_game_click(event.pos):
                    need_render = True

        return need_render

    def _handle_button_click(self, button_name: str):
        """
        处理按钮点击

        参数:
            button_name: 按钮名称
        """
        if button_name == 'take_gems':
            self._start_take_gems_action()
        elif button_name == 'reserve_card':
            self._start_reserve_card_action()
        elif button_name == 'purchase_card':
            self._start_purchase_card_action()
        elif button_name == 'end_turn':
            self._end_turn()
        elif button_name == 'cancel':
            self._cancel_action()
        elif button_name == 'confirm':
            self._confirm_action()

    def _start_take_gems_action(self):
        """开始拿宝石动作"""
        self.current_action = GameAction.TAKE_GEMS
        self.selected_gems = {}
        print("\n请选择要拿取的宝石（3个不同颜色 或 2个相同颜色）")

    def _start_reserve_card_action(self):
        """开始保留卡牌动作"""
        self.current_action = GameAction.RESERVE_CARD
        self.selected_card = None
        print("\n请选择要保留的卡牌")

    def _start_purchase_card_action(self):
        """开始购买卡牌动作"""
        self.current_action = GameAction.PURCHASE_CARD
        self.selected_card = None
        print("\n请选择要购买的卡牌")

    def _cancel_action(self):
        """取消当前动作"""
        self.current_action = None
        self.selected_gems = {}
        self.selected_card = None
        print("\n已取消动作")

    def _confirm_action(self):
        """确认并执行当前动作"""
        if self.current_action == GameAction.TAKE_GEMS:
            self._execute_take_gems()
        elif self.current_action == GameAction.RESERVE_CARD:
            self._execute_reserve_card()
        elif self.current_action == GameAction.PURCHASE_CARD:
            self._execute_purchase_card()

    def _execute_take_gems(self):
        """执行拿宝石动作"""
        if not self.selected_gems:
            print("未选择任何宝石")
            return

        # 转换为标准格式
        gems_to_take = {color: 0 for color in config.NORMAL_GEM_TYPES}
        gems_to_take.update(self.selected_gems)

        # 执行动作
        success = self.game_engine.take_gems_action(gems_to_take)

        if success:
            self._cancel_action()
            # 检查是否需要弃置宝石，然后自动结束回合
            player = self.game_engine.get_current_player()
            if player.get_total_gems() > config.MAX_HAND_GEMS:
                self._start_discard_gems()
            else:
                # 不需要弃置，自动结束回合
                self._end_turn()
        else:
            print("拿宝石失败，请重新选择")

    def _execute_reserve_card(self):
        """执行保留卡牌动作"""
        if not self.selected_card:
            print("未选择卡牌")
            return

        success = self.game_engine.reserve_card_action(self.selected_card)

        if success:
            self._cancel_action()
            # 检查是否需要弃置宝石，然后自动结束回合
            player = self.game_engine.get_current_player()
            if player.get_total_gems() > config.MAX_HAND_GEMS:
                self._start_discard_gems()
            else:
                # 不需要弃置，自动结束回合
                self._end_turn()
        else:
            print("保留卡牌失败")

    def _execute_purchase_card(self):
        """执行购买卡牌动作"""
        if not self.selected_card:
            print("未选择卡牌")
            return

        # 检查是否从保留卡购买
        player = self.game_engine.get_current_player()
        from_reserved = self.selected_card in player.reserved_cards

        success = self.game_engine.purchase_card_action(self.selected_card, from_reserved)

        if success:
            self._cancel_action()
            # 购买卡不会增加宝石，直接结束回合
            self._end_turn()

    def _end_turn(self):
        """结束当前回合"""
        player = self.game_engine.get_current_player()

        # 检查是否需要弃置宝石
        if player.get_total_gems() > config.MAX_HAND_GEMS:
            print(f"宝石超过{config.MAX_HAND_GEMS}个，请先弃置")
            self._start_discard_gems()
            return

        # 结束回合
        noble = self.game_engine.end_turn()

        if noble:
            self.renderer.draw_message(f"贵族 {noble.name} 拜访了 {player.name}！\n获得3分！")

        # 检查游戏是否结束
        if self.game_engine.is_game_over():
            self._show_game_over()
        else:
            # 提示下一个玩家
            next_player = self.game_engine.get_current_player()
            self.renderer.draw_message(f"轮到 {next_player.name}", duration=1000)

        self._cancel_action()

    def _check_discard_gems(self):
        """检查并处理弃置宝石"""
        player = self.game_engine.get_current_player()

        if player.get_total_gems() > config.MAX_HAND_GEMS:
            self._start_discard_gems()

    def _start_discard_gems(self):
        """开始弃置宝石流程"""
        player = self.game_engine.get_current_player()
        excess = player.get_total_gems() - config.MAX_HAND_GEMS

        print(f"\n宝石超过{config.MAX_HAND_GEMS}个，需要弃置{excess}个")

        # 显示弃置界面
        self._show_discard_dialog(excess)

    def _show_discard_dialog(self, excess_count: int):
        """
        显示弃置宝石对话框

        参数:
            excess_count: 需要弃置的数量
        """
        player = self.game_engine.get_current_player()
        to_discard = {}

        screen = self.renderer.screen
        clock = pygame.time.Clock()
        discarding = True

        # 预先创建所有按钮（避免每帧重新创建导致闪烁）
        gem_buttons = {}  # {color: {'minus': Button, 'plus': Button}}
        y_positions = {}  # {color: y}

        y = 300
        for color in config.GEM_TYPES:
            have = player.gems.get(color, 0)
            if have > 0:
                x = config.WINDOW_WIDTH // 2 - 150
                minus_btn = Button(x + 200, y - 15, 30, 30, "-")
                plus_btn = Button(x + 270, y - 15, 30, 30, "+")
                gem_buttons[color] = {'minus': minus_btn, 'plus': plus_btn}
                y_positions[color] = y
                y += 50

        # 确认按钮
        confirm_btn = Button(
            config.WINDOW_WIDTH // 2 - 60,
            y + 50, 120, 40, "确认弃置"
        )

        while discarding:
            # 获取鼠标位置（用于悬停检测）
            mouse_pos = pygame.mouse.get_pos()

            # 绘制背景（半透明）
            s = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
            s.set_alpha(128)
            s.fill(config.COLOR_BLACK)
            screen.blit(s, (0, 0))

            # 绘制提示
            title = self.font_medium.render(f"请弃置 {excess_count} 个宝石", True, config.COLOR_WHITE)
            screen.blit(title, (config.WINDOW_WIDTH // 2 - 100, 200))

            # 显示可弃置的宝石
            for color in config.GEM_TYPES:
                have = player.gems.get(color, 0)
                discarded = to_discard.get(color, 0)

                if have > 0 and color in gem_buttons:
                    y = y_positions[color]
                    x = config.WINDOW_WIDTH // 2 - 150

                    # 宝石图标
                    gem_color = config.GEM_COLORS[color]
                    pygame.draw.circle(screen, gem_color, (x, y), 20)
                    pygame.draw.circle(screen, config.COLOR_WHITE, (x, y), 20, 2)

                    # 宝石名称和数量
                    from utils import get_gem_name
                    text = self.font_small.render(
                        f"{get_gem_name(color)}: {have}个",
                        True, config.COLOR_WHITE
                    )
                    screen.blit(text, (x + 30, y - 10))

                    # 减少按钮
                    minus_btn = gem_buttons[color]['minus']
                    minus_btn.set_enabled(discarded > 0)
                    minus_btn.is_hovered = minus_btn.rect.collidepoint(mouse_pos) and minus_btn.is_enabled
                    minus_btn.draw(screen, self.font_small)

                    # 当前弃置数量
                    discard_text = self.font_small.render(str(discarded), True, config.COLOR_WHITE)
                    screen.blit(discard_text, (x + 240, y - 10))

                    # 增加按钮
                    plus_btn = gem_buttons[color]['plus']
                    plus_btn.set_enabled(discarded < have)
                    plus_btn.is_hovered = plus_btn.rect.collidepoint(mouse_pos) and plus_btn.is_enabled
                    plus_btn.draw(screen, self.font_small)

            # 确认按钮
            total_discarded = sum(to_discard.values())
            confirm_btn.set_enabled(total_discarded == excess_count)
            confirm_btn.is_hovered = confirm_btn.rect.collidepoint(mouse_pos) and confirm_btn.is_enabled
            confirm_btn.draw(screen, self.font_medium)

            pygame.display.flip()

            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

                # 检查宝石按钮
                for color, buttons in gem_buttons.items():
                    if buttons['minus'].handle_event(event):
                        current = to_discard.get(color, 0)
                        to_discard[color] = max(0, current - 1)

                    if buttons['plus'].handle_event(event):
                        current = to_discard.get(color, 0)
                        have = player.gems.get(color, 0)
                        to_discard[color] = min(have, current + 1)

                # 检查确认按钮
                if confirm_btn.handle_event(event):
                    if total_discarded == excess_count:
                        # 执行弃置
                        self.game_engine.executor.discard_gems(
                            player, to_discard, self.game_engine.game_state
                        )
                        discarding = False
                        # 弃置完成后自动结束回合
                        self._end_turn()

            clock.tick(config.FPS)

    def _show_game_over(self):
        """显示游戏结束画面"""
        winner = self.game_engine.get_winner()

        message = f"游戏结束！\n{winner.name} 获胜！\n最终得分: {winner.get_points()}分"
        self.renderer.draw_message(message, duration=5000)

    def _handle_game_click(self, pos) -> bool:
        """
        处理游戏内点击（卡牌、宝石等）

        参数:
            pos: 鼠标位置

        返回:
            bool: 是否处理了点击
        """
        # 拿宝石模式
        if self.current_action == GameAction.TAKE_GEMS:
            gem_color = self.renderer.get_gem_at_pos(pos)
            if gem_color and gem_color != 'gold':
                self._toggle_gem_selection(gem_color)
                return True

        # 保留/购买卡牌模式
        elif self.current_action in [GameAction.RESERVE_CARD, GameAction.PURCHASE_CARD]:
            card = self.renderer.get_card_at_pos(pos)
            if card:
                self.selected_card = card
                print(f"选中卡牌: {card}")
                return True

        return False

    def _toggle_gem_selection(self, color: str):
        """
        切换宝石选择状态

        参数:
            color: 宝石颜色
        """
        total = sum(self.selected_gems.values())
        current_count = self.selected_gems.get(color, 0)

        # 如果这个颜色已经被选了
        if current_count > 0:
            if current_count == 1:
                # 如果只选了1个，检查能否变成2个
                if len(self.selected_gems) == 1:  # 只选了这一种颜色
                    self.selected_gems[color] = 2
                    print(f"选择 {color} x2")
                else:
                    # 有其他颜色，取消这个颜色
                    del self.selected_gems[color]
                    print(f"取消选择 {color}")
            else:  # current_count == 2
                # 选了2个，再点击就取消
                del self.selected_gems[color]
                print(f"取消选择 {color}")
        else:
            # 这个颜色还没选
            if total == 0:
                # 第一个宝石
                self.selected_gems[color] = 1
                print(f"选择 {color} x1")
            elif total == 1:
                # 已经选了1个宝石
                self.selected_gems[color] = 1
                print(f"选择 {color} x1")
            elif total == 2:
                if len(self.selected_gems) == 1:
                    # 已经有2个相同颜色，不能再选
                    print("已选择2个相同颜色，不能再选")
                else:
                    # 已有2个不同颜色，可以再选1个
                    self.selected_gems[color] = 1
                    print(f"选择 {color} x1")
            else:
                print("已选择3个宝石，不能再选")

        print(f"当前选择: {self.selected_gems}")

    def draw_ui(self, screen):
        """
        绘制UI元素（按钮、提示等）

        参数:
            screen: pygame屏幕对象
        """
        # 第一步：先更新所有按钮的启用状态
        for btn_name, btn in self.buttons.items():
            if btn_name == 'cancel':
                btn.set_enabled(self.current_action is not None)
            elif btn_name in ['take_gems', 'reserve_card', 'purchase_card']:
                btn.set_enabled(self.current_action is None)
            elif btn_name == 'end_turn':
                # end_turn 按钮在有当前动作时禁用
                btn.set_enabled(self.current_action is None)
            elif btn_name == 'confirm':
                # confirm 按钮根据当前动作类型决定是否启用
                if self.current_action == GameAction.TAKE_GEMS:
                    # 拿宝石：至少选了宝石才启用
                    btn.set_enabled(len(self.selected_gems) > 0)
                elif self.current_action == GameAction.RESERVE_CARD:
                    # 保留卡：选了卡牌才启用
                    btn.set_enabled(self.selected_card is not None)
                elif self.current_action == GameAction.PURCHASE_CARD:
                    # 购买卡：选了卡牌才启用
                    btn.set_enabled(self.selected_card is not None)
                else:
                    btn.set_enabled(False)

        # 第二步：再更新所有按钮的悬停状态（基于最新的 is_enabled）
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons.values():
            btn.is_hovered = btn.rect.collidepoint(mouse_pos) and btn.is_enabled

        # 第三步：绘制按钮
        for btn_name, btn in self.buttons.items():
            if btn_name == 'confirm':
                # 只在选择了动作时显示
                if self.current_action:
                    btn.draw(screen, self.font_medium)
            else:
                btn.draw(screen, self.font_medium)

        # 绘制当前动作提示
        if self.current_action:
            self._draw_action_hint(screen)

        # 绘制选中的宝石/卡牌
        if self.current_action == GameAction.TAKE_GEMS and self.selected_gems:
            self._draw_selected_gems(screen)
        elif self.selected_card:
            self._draw_selected_card_hint(screen)

    def _draw_action_hint(self, screen):
        """绘制动作提示"""
        hints = {
            GameAction.TAKE_GEMS: "点击宝石选择（3不同 或 2相同）",
            GameAction.RESERVE_CARD: "点击卡牌保留（获得1黄金）",
            GameAction.PURCHASE_CARD: "点击卡牌购买"
        }

        hint_text = hints.get(self.current_action, "")
        text_surface = self.font_medium.render(hint_text, True, config.COLOR_WHITE)

        # 背景框
        bg_rect = text_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - 330))
        bg_rect.inflate_ip(20, 10)
        pygame.draw.rect(screen, config.COLOR_DARK_GRAY, bg_rect)
        pygame.draw.rect(screen, config.COLOR_WHITE, bg_rect, 2)

        screen.blit(text_surface, text_surface.get_rect(center=bg_rect.center))

    def _draw_selected_gems(self, screen):
        """绘制已选择的宝石"""
        y = config.WINDOW_HEIGHT - 360
        text = "已选择: "

        for color, count in self.selected_gems.items():
            from utils import get_gem_name
            text += f"{get_gem_name(color)}x{count} "

        text_surface = self.font_small.render(text, True, config.COLOR_WHITE)
        screen.blit(text_surface, (config.WINDOW_WIDTH // 2 - 100, y))

    def _draw_selected_card_hint(self, screen):
        """绘制选中卡牌的提示"""
        if self.selected_card:
            y = config.WINDOW_HEIGHT - 360
            text = f"已选择: {self.selected_card}"
            text_surface = self.font_small.render(text, True, config.COLOR_WHITE)
            screen.blit(text_surface, (config.WINDOW_WIDTH // 2 - 100, y))
