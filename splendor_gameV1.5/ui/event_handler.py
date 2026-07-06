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
        self.selected_deck_level = None  # 选中的牌堆等级（用于从牌堆顶保留卡牌）

        # UI按钮
        self.buttons = self._create_buttons()

        # 字体（使用中文字体）
        from .renderer import get_chinese_font
        self.font_small = get_chinese_font(config.FONT_SIZE_SMALL)
        self.font_medium = get_chinese_font(config.FONT_SIZE_MEDIUM)

    def _create_buttons(self) -> Dict[str, Button]:
        """创建UI按钮（支持缩放）- 使用 button_area 布局配置"""
        buttons = {}

        # 使用缩放器计算位置和尺寸
        s = self.renderer.scaler.scale_value

        # 动作按钮（使用 button_area 布局配置）
        btn_x = self.renderer.scaler.get_layout_value('button_area', 'x')
        btn_y = self.renderer.scaler.get_layout_value('button_area', 'y')
        btn_width = s(120)  # 足够显示完整文字
        btn_height = s(50)
        btn_spacing = s(15)  # 按钮间距

        # 一排四个按钮
        buttons['take_gems'] = Button(btn_x, btn_y, btn_width, btn_height, "拿取宝石")
        buttons['reserve_card'] = Button(btn_x + (btn_width + btn_spacing), btn_y, btn_width, btn_height, "保留卡牌")
        buttons['purchase_card'] = Button(btn_x + (btn_width + btn_spacing) * 2, btn_y, btn_width, btn_height, "购买卡牌")
        buttons['end_turn'] = Button(btn_x + (btn_width + btn_spacing) * 3, btn_y, btn_width, btn_height, "结束回合")

        # 确认和取消按钮（屏幕中下方并排）
        confirm_cancel_y = s(1080 - 80)  # 调整到更底部
        button_width = s(120)
        button_height = s(50)
        button_spacing = s(20)

        # 计算两个按钮居中的起始位置
        total_width = button_width * 2 + button_spacing
        start_x = s(1920 // 2) - total_width // 2

        buttons['confirm'] = Button(
            start_x,
            confirm_cancel_y,
            button_width, button_height, "确认"
        )

        buttons['cancel'] = Button(
            start_x + button_width + button_spacing,
            confirm_cancel_y,
            button_width, button_height, "取消"
        )

        return buttons

    def recreate_buttons(self):
        """重新创建按钮（窗口大小改变时调用）"""
        self.buttons = self._create_buttons()

    def _set_hint(self, message: str):
        """
        设置底部提示框消息

        参数:
            message: 提示消息
        """
        self.renderer.set_hint_message(message)

    def _clear_hint(self):
        """清空底部提示框消息"""
        self.renderer.clear_hint_message()

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
        self._set_hint("请选择要拿取的宝石（3个不同颜色 或 2个相同颜色）")

    def _start_reserve_card_action(self):
        """开始保留卡牌动作"""
        current_player = self.game_engine.get_current_player()

        # 检查保留卡是否已达上限
        if len(current_player.reserved_cards) >= config.MAX_RESERVED_CARDS:
            self._set_hint(f"保留卡片已达上限（{config.MAX_RESERVED_CARDS}张）")
            return  # 不进入保留卡牌模式

        self.current_action = GameAction.RESERVE_CARD
        self.selected_card = None
        self._set_hint("请选择要保留的卡牌（桌面卡牌或点击牌堆顶）")

    def _start_purchase_card_action(self):
        """开始购买卡牌动作"""
        self.current_action = GameAction.PURCHASE_CARD
        self.selected_card = None
        self._set_hint("请选择要购买的卡牌（桌面卡牌或自己的保留卡）")

    def _clear_selection(self):
        """清空选择状态（不显示提示）"""
        self.current_action = None
        self.selected_gems = {}
        self.selected_card = None
        self.selected_deck_level = None

    def _cancel_action(self):
        """取消当前动作（显示取消提示）"""
        self._clear_selection()
        self._set_hint("已取消当前操作")

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
            self._set_hint("未选择任何宝石")
            return

        # 转换为标准格式
        gems_to_take = {color: 0 for color in config.NORMAL_GEM_TYPES}
        gems_to_take.update(self.selected_gems)

        # 执行动作
        success = self.game_engine.take_gems_action(gems_to_take)

        if success:
            self._clear_selection()  # 清空选择，不显示提示
            # 检查是否需要弃置宝石，然后自动结束回合
            player = self.game_engine.get_current_player()
            if player.get_total_gems() > config.MAX_HAND_GEMS:
                self._start_discard_gems()
            else:
                # 不需要弃置，自动结束回合
                self._end_turn()
        else:
            self._set_hint("拿宝石失败，请重新选择")

    def _execute_reserve_card(self):
        """执行保留卡牌动作"""
        if not self.selected_card and not self.selected_deck_level:
            self._set_hint("未选择卡牌或牌堆")
            return

        # 判断是从桌面还是牌堆顶保留
        if self.selected_deck_level:
            # 从牌堆顶保留
            success = self.game_engine.reserve_card_from_deck(self.selected_deck_level)
        else:
            # 从桌面保留
            success = self.game_engine.reserve_card_action(self.selected_card)

        if success:
            self._clear_selection()  # 清空选择，不显示提示
            # 检查是否需要弃置宝石，然后自动结束回合
            player = self.game_engine.get_current_player()
            if player.get_total_gems() > config.MAX_HAND_GEMS:
                self._start_discard_gems()
            else:
                # 不需要弃置，自动结束回合
                self._end_turn()
        else:
            self._set_hint("保留卡牌失败")

    def _execute_purchase_card(self):
        """执行购买卡牌动作"""
        if not self.selected_card:
            self._set_hint("未选择卡牌")
            return

        # 检查是否从保留卡购买
        player = self.game_engine.get_current_player()
        from_reserved = self.selected_card in player.reserved_cards

        success = self.game_engine.purchase_card_action(self.selected_card, from_reserved)

        if success:
            self._clear_selection()  # 清空选择，不显示提示
            # 购买卡不会增加宝石，直接结束回合
            self._end_turn()

    def _end_turn(self):
        """结束当前回合"""
        player = self.game_engine.get_current_player()

        # 检查是否需要弃置宝石
        if player.get_total_gems() > config.MAX_HAND_GEMS:
            self._set_hint(f"宝石超过{config.MAX_HAND_GEMS}个，请先弃置")
            self._start_discard_gems()
            return

        # 第一阶段：检查贵族
        qualified_nobles = self.game_engine.end_turn()

        # 处理贵族选择
        selected_noble = None
        if qualified_nobles:
            if len(qualified_nobles) == 1:
                # 只有一个贵族，直接选择
                selected_noble = qualified_nobles[0]
            else:
                # 多个贵族，让玩家选择
                selected_noble = self._show_noble_selection_dialog(qualified_nobles)

        # 第二阶段：完成回合（授予贵族并切换玩家）
        self.game_engine.complete_turn(selected_noble)

        # 显示贵族拜访消息（在完成回合后）
        if selected_noble:
            self._set_hint(f"贵族 {selected_noble.name} 拜访了 {player.name}，获得3分")
        else:
            # 没有贵族时，提示下一个玩家
            next_player = self.game_engine.get_current_player()
            self._set_hint(f"轮到 {next_player.name}")

        # 检查游戏是否结束
        if self.game_engine.is_game_over():
            self._show_game_over()

        # 清空选择状态（不显示提示）
        self._clear_selection()

    def _check_discard_gems(self):
        """检查并处理弃置宝石"""
        player = self.game_engine.get_current_player()

        if player.get_total_gems() > config.MAX_HAND_GEMS:
            self._start_discard_gems()

    def _start_discard_gems(self):
        """开始弃置宝石流程"""
        player = self.game_engine.get_current_player()
        excess = player.get_total_gems() - config.MAX_HAND_GEMS

        # 显示弃置界面
        self._show_discard_dialog(excess)

    def _show_discard_dialog(self, excess_count: int):
        """
        显示弃置宝石对话框（浮窗样式）

        参数:
            excess_count: 需要弃置的数量
        """
        player = self.game_engine.get_current_player()
        to_discard = {}

        screen = self.renderer.screen
        clock = pygame.time.Clock()
        discarding = True

        # 使用缩放器
        s = self.renderer.scaler.scale_value

        # 计算对话框尺寸和位置（居中浮窗）
        dialog_width = s(500)
        dialog_height = s(500)
        dialog_x = (self.renderer.screen_width - dialog_width) // 2
        dialog_y = (self.renderer.screen_height - dialog_height) // 2

        # 预先创建所有按钮（避免每帧重新创建导致闪烁）
        gem_buttons = {}  # {color: {'minus': Button, 'plus': Button}}
        y_positions = {}  # {color: y}

        y = dialog_y + s(80)
        for color in config.GEM_TYPES:
            have = player.gems.get(color, 0)
            if have > 0:
                x = dialog_x + s(50)
                minus_btn = Button(x + s(200), y - s(15), s(30), s(30), "-")
                plus_btn = Button(x + s(270), y - s(15), s(30), s(30), "+")
                gem_buttons[color] = {'minus': minus_btn, 'plus': plus_btn}
                y_positions[color] = y
                y += s(50)

        # 确认按钮
        confirm_btn = Button(
            dialog_x + dialog_width // 2 - s(60),
            y + s(30), s(120), s(40), "确认弃置"
        )

        while discarding:
            # 先渲染游戏背景（保持游戏画面可见）
            self.renderer.render(
                self.game_engine.game_state,
                self.selected_card,
                self.selected_gems,
                self.selected_deck_level
            )
            self.draw_ui(screen)

            # 获取鼠标位置（用于悬停检测）
            mouse_pos = pygame.mouse.get_pos()

            # 绘制浮窗背景（深灰色，不透明）
            dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
            pygame.draw.rect(screen, config.COLOR_DARK_GRAY, dialog_rect)
            pygame.draw.rect(screen, config.COLOR_WHITE, dialog_rect, s(3))

            # 绘制标题
            title = self.font_medium.render(f"请弃置 {excess_count} 个宝石", True, config.COLOR_WHITE)
            title_rect = title.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + s(30)))
            screen.blit(title, title_rect)

            # 显示可弃置的宝石
            for color in config.GEM_TYPES:
                have = player.gems.get(color, 0)
                discarded = to_discard.get(color, 0)

                if have > 0 and color in gem_buttons:
                    y = y_positions[color]
                    x = dialog_x + s(50)

                    # 宝石图标
                    gem_color = config.GEM_COLORS[color]
                    pygame.draw.circle(screen, gem_color, (x, y), s(20))
                    pygame.draw.circle(screen, config.COLOR_WHITE, (x, y), s(20), 2)

                    # 宝石名称和数量
                    from utils import get_gem_name
                    text = self.font_small.render(
                        f"{get_gem_name(color)}: {have}个",
                        True, config.COLOR_WHITE
                    )
                    screen.blit(text, (x + s(30), y - s(10)))

                    # 减少按钮
                    minus_btn = gem_buttons[color]['minus']
                    minus_btn.set_enabled(discarded > 0)
                    minus_btn.is_hovered = minus_btn.rect.collidepoint(mouse_pos) and minus_btn.is_enabled
                    minus_btn.draw(screen, self.font_small)

                    # 当前弃置数量
                    discard_text = self.font_small.render(str(discarded), True, config.COLOR_WHITE)
                    screen.blit(discard_text, (x + s(240), y - s(10)))

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

    def _show_noble_selection_dialog(self, qualified_nobles: List) -> Optional:
        """
        显示贵族选择对话框（浮窗样式）

        参数:
            qualified_nobles: 符合条件的贵族列表

        返回:
            选择的贵族，如果取消则返回 None
        """
        if not qualified_nobles:
            return None

        if len(qualified_nobles) == 1:
            # 只有一个贵族，直接返回
            return qualified_nobles[0]

        screen = self.renderer.screen
        clock = pygame.time.Clock()
        selecting = True
        selected_noble = None

        # 使用缩放器
        s = self.renderer.scaler.scale_value

        # 计算对话框尺寸和位置（居中浮窗）
        noble_size = s(config.NOBLE_SIZE)
        noble_spacing = s(20)
        dialog_width = len(qualified_nobles) * (noble_size + noble_spacing) + s(40)
        dialog_height = noble_size + s(120)
        dialog_x = (self.renderer.screen_width - dialog_width) // 2
        dialog_y = (self.renderer.screen_height - dialog_height) // 2

        # 预先创建贵族按钮
        noble_buttons = []  # [(noble, pygame.Rect)]

        # 计算布局（相对于对话框）
        start_y = dialog_y + s(60)

        for i, noble in enumerate(qualified_nobles):
            # 横向排列
            x = dialog_x + s(20) + i * (noble_size + noble_spacing)
            y = start_y

            # 创建一个矩形按钮区域（用于点击检测）
            btn_rect = pygame.Rect(x, y, noble_size, noble_size)
            noble_buttons.append((noble, btn_rect))

        while selecting:
            # 先渲染游戏背景（保持游戏画面可见）
            self.renderer.render(
                self.game_engine.game_state,
                self.selected_card,
                self.selected_gems,
                self.selected_deck_level
            )
            self.draw_ui(screen)

            # 获取鼠标位置
            mouse_pos = pygame.mouse.get_pos()

            # 绘制浮窗背景（深灰色，不透明）
            dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
            pygame.draw.rect(screen, config.COLOR_DARK_GRAY, dialog_rect)
            pygame.draw.rect(screen, config.COLOR_WHITE, dialog_rect, s(3))

            # 绘制标题
            title = self.font_medium.render(
                "多个贵族同时满足条件，请选择一位拜访你",
                True, config.COLOR_WHITE
            )
            title_rect = title.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + s(25)))
            screen.blit(title, title_rect)

            # 绘制每个贵族
            for noble, btn_rect in noble_buttons:
                x = btn_rect.x
                y = btn_rect.y

                # 检查鼠标悬停
                is_hovered = btn_rect.collidepoint(mouse_pos)

                # 确定边框颜色和宽度
                if is_hovered:
                    border_color = config.COLOR_YELLOW
                    border_width = s(4)
                else:
                    border_color = config.COLOR_WHITE
                    border_width = s(2)

                # 绘制背景
                pygame.draw.rect(screen, config.COLOR_DARK_GRAY, btn_rect)

                # 绘制边框
                pygame.draw.rect(screen, border_color, btn_rect, border_width)

                # 贵族名称
                name_text = self.font_small.render(noble.name, True, config.COLOR_WHITE)
                name_rect = name_text.get_rect(center=(x + noble_size // 2, y + s(20)))
                screen.blit(name_text, name_rect)

                # 显示需求（宝石图标 + 数量）
                req_y = y + s(50)
                for color in config.NORMAL_GEM_TYPES:
                    count = noble.requirements.get(color, 0)
                    if count > 0:
                        # 宝石图标
                        gem_color = config.GEM_COLORS[color]
                        gem_x = x + s(20)
                        pygame.draw.circle(screen, gem_color, (gem_x, req_y), s(12))
                        pygame.draw.circle(screen, config.COLOR_WHITE, (gem_x, req_y), s(12), 1)

                        # 数量
                        count_text = self.font_small.render(str(count), True, config.COLOR_WHITE)
                        screen.blit(count_text, (gem_x + s(20), req_y - s(10)))

                        req_y += s(30)

                # 显示分数
                points_text = self.font_medium.render("+3分", True, config.GEM_COLORS['gold'])
                points_rect = points_text.get_rect(center=(x + noble_size // 2, y + noble_size - s(25)))
                screen.blit(points_text, points_rect)

            pygame.display.flip()

            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # 检查是否点击了某个贵族
                    for noble, btn_rect in noble_buttons:
                        if btn_rect.collidepoint(event.pos):
                            selected_noble = noble
                            selecting = False
                            break

            clock.tick(config.FPS)

        return selected_noble

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
                # 检查宝石数量是否大于0
                gem_count = self.game_engine.game_state.gem_bank.get(gem_color, 0)
                if gem_count > 0:
                    self._toggle_gem_selection(gem_color)
                    return True
                else:
                    # 宝石数量为0，不处理点击
                    return False

        # 保留卡牌模式
        elif self.current_action == GameAction.RESERVE_CARD:
            # 检查是否点击卡牌
            card = self.renderer.get_card_at_pos(pos)
            if card:
                self.selected_card = card
                self.selected_deck_level = None  # 清空牌堆等级
                return True

            # 再检查是否点击牌堆
            deck_level = self.renderer.get_deck_level_at_pos(pos)
            if deck_level:
                self.selected_deck_level = deck_level  # 保存牌堆等级
                self.selected_card = None  # 清空卡牌
                return True

        # 购买卡牌模式（需要验证）
        elif self.current_action == GameAction.PURCHASE_CARD:
            card = self.renderer.get_card_at_pos(pos)
            if card:
                current_player = self.game_engine.get_current_player()

                # 检查1：是否是其他玩家的保留卡
                is_other_player_reserved = False
                for player in self.game_engine.game_state.players:
                    if player != current_player and card in player.reserved_cards:
                        is_other_player_reserved = True
                        break

                if is_other_player_reserved:
                    self._set_hint("无法购买其他玩家的保留卡")
                    return True

                # 检查2：当前玩家资源是否充足
                valid, error = self.game_engine.validator.validate_purchase_card(
                    self.game_engine.game_state, card
                )

                if not valid:
                    self._set_hint("资源不足，无法购买此卡牌")
                    return True

                # 通过验证，可以选中
                self.selected_card = card
                self.selected_deck_level = None
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

        # 获取该颜色宝石的实际数量
        gem_count = self.game_engine.game_state.gem_bank.get(color, 0)

        # 如果这个颜色已经被选了
        if current_count > 0:
            if current_count == 1:
                # 如果只选了1个，检查能否变成2个
                if len(self.selected_gems) == 1:  # 只选了这一种颜色
                    # 检查宝石数量是否 >= 4
                    if gem_count >= 4:
                        self.selected_gems[color] = 2
                    else:
                        # 宝石数量 < 4，不能选2个，取消选择
                        del self.selected_gems[color]
                else:
                    # 有其他颜色，取消这个颜色
                    del self.selected_gems[color]
            else:  # current_count == 2
                # 选了2个，再点击就取消
                del self.selected_gems[color]
        else:
            # 这个颜色还没选
            if total == 0:
                # 第一个宝石
                self.selected_gems[color] = 1
            elif total == 1:
                # 已经选了1个宝石
                self.selected_gems[color] = 1
            elif total == 2:
                if len(self.selected_gems) == 1:
                    # 已经有2个相同颜色，不能再选
                    pass
                else:
                    # 已有2个不同颜色，可以再选1个
                    self.selected_gems[color] = 1
            else:
                # 已选择3个宝石，不能再选
                pass

    def draw_ui(self, screen):
        """
        绘制UI元素（按钮、提示等）

        参数:
            screen: pygame屏幕对象
        """
        # 第一步：先更新所有按钮的启用状态
        for btn_name, btn in self.buttons.items():
            if btn_name == 'cancel':
                # 取消按钮：有当前动作时启用
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
                    # 保留卡：选了卡牌或牌堆才启用
                    btn.set_enabled(self.selected_card is not None or self.selected_deck_level is not None)
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
            if btn_name in ['confirm', 'cancel']:
                # 确认和取消按钮：只在选择了动作时一起显示
                if self.current_action:
                    btn.draw(screen, self.font_medium)
            else:
                # 其他按钮始终显示
                btn.draw(screen, self.font_medium)

        # 已删除中间的黄框提示（_draw_action_hint）
