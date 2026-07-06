"""
渲染器 - 负责绘制游戏画面（支持缩放）
"""
import pygame
import os
from models import GameState
from .components import CardDisplay, GemDisplay, NobleDisplay, MessageBox
from utils import UIScaler
import config


def get_chinese_font(size):
    """
    获取支持中文的字体

    参数:
        size: 字体大小

    返回:
        pygame.font.Font: 字体对象
    """
    # 尝试加载中文字体
    for font_path in config.CHINESE_FONTS:
        if os.path.exists(font_path):
            try:
                return pygame.font.Font(font_path, size)
            except:
                continue

    # 如果都失败，使用系统默认字体
    print(f"警告: 未找到中文字体，使用系统默认字体")
    return pygame.font.SysFont('simsun', size)  # 尝试使用宋体


class Renderer:
    """游戏渲染器（支持缩放）"""

    def __init__(self, screen):
        """
        初始化渲染器

        参数:
            screen: pygame屏幕对象
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # 初始化缩放器
        self.scaler = UIScaler(self.screen_width, self.screen_height)

        # 初始化字体（使用中文字体，根据缩放调整大小）
        pygame.font.init()
        self.update_fonts()

        # UI组件缓存
        self.card_displays = {}  # {level: [CardDisplay, ...]}
        self.gem_displays = []
        self.noble_displays = []
        self.reserved_card_displays = []  # 保留卡显示列表（用于点击检测）

    def update_fonts(self):
        """根据当前缩放更新字体大小"""
        self.font_small = get_chinese_font(self.scaler.scale_font_size(config.FONT_SIZE_SMALL))
        self.font_medium = get_chinese_font(self.scaler.scale_font_size(config.FONT_SIZE_MEDIUM))
        self.font_large = get_chinese_font(self.scaler.scale_font_size(config.FONT_SIZE_LARGE))
        self.font_title = get_chinese_font(self.scaler.scale_font_size(config.FONT_SIZE_TITLE))

    def resize(self, new_width, new_height):
        """
        窗口大小改变时调用

        参数:
            new_width: 新窗口宽度
            new_height: 新窗口高度
        """
        self.screen_width = new_width
        self.screen_height = new_height
        self.scaler.update_scale(new_width, new_height)
        self.update_fonts()

    def render(self, game_state: GameState, selected_card=None, selected_gems=None):
        """
        渲染整个游戏画面

        参数:
            game_state: 游戏状态
            selected_card: 当前选中的卡牌（可选）
            selected_gems: 当前选中的宝石字典（可选）
        """
        # 保存选中状态，供绘制方法使用
        self.selected_card = selected_card
        self.selected_gems = selected_gems or {}

        # 清空屏幕
        self.screen.fill(config.COLOR_BACKGROUND)

        # 绘制各个部分
        self.draw_title()
        self.draw_gems_bank(game_state)
        self.draw_table_cards(game_state)
        self.draw_nobles(game_state)
        self.draw_players_info(game_state)
        self.draw_current_player_highlight(game_state)

        # 注意：不在这里调用 flip()，由外部统一管理刷新时机

    def draw_title(self):
        """绘制游戏标题"""
        title_text = self.font_title.render("璀璨宝石 Splendor", True, config.COLOR_WHITE)
        title_y = self.scaler.get_layout_value('title', 'y')
        title_rect = title_text.get_rect(center=(self.screen_width // 2, title_y))
        self.screen.blit(title_text, title_rect)

    def draw_gems_bank(self, game_state: GameState):
        """
        绘制公共宝石供应区

        参数:
            game_state: 游戏状态
        """
        gem_x = self.scaler.get_layout_value('gem_area', 'x')
        gem_y = self.scaler.get_layout_value('gem_area', 'y')

        # 标题（保持原位置：gem_y上方30px）
        title = self.font_medium.render("公共宝石", True, config.COLOR_WHITE)
        title_y = gem_y - self.scaler.scale_value(30)  # 标题在gem_y上方30px
        self.screen.blit(title, (gem_x, title_y))

        # 宝石列表起始位置（在gem_y基础上额外下移40px，避免遮挡标题）
        gem_list_start_y = gem_y + self.scaler.scale_value(40)

        # 绘制宝石
        self.gem_displays.clear()
        gem_size = self.scaler.scale_value(config.GEM_SIZE)
        gem_spacing = self.scaler.scale_value(config.GEM_SIZE + config.GEM_MARGIN + 15)

        for i, color in enumerate(config.GEM_TYPES):
            count = game_state.gem_bank.get(color, 0)
            x = gem_x + gem_size // 2
            y = gem_list_start_y + i * gem_spacing  # 使用下移后的起始位置

            gem_display = GemDisplay(x, y, color, count, size=gem_size)
            # 设置选中状态
            if color in self.selected_gems and self.selected_gems[color] > 0:
                gem_display.is_selected = True
            gem_display.draw(self.screen, self.font_medium)
            self.gem_displays.append(gem_display)

            # 宝石名称
            from utils import get_gem_name
            name_text = self.font_small.render(get_gem_name(color), True, config.COLOR_WHITE)
            self.screen.blit(name_text, (x + gem_size // 2 + self.scaler.scale_value(10), y - self.scaler.scale_value(8)))

    def draw_table_cards(self, game_state: GameState):
        """
        绘制桌面展示的卡牌

        参数:
            game_state: 游戏状态
        """
        # 清空缓存
        self.card_displays = {1: [], 2: [], 3: []}

        # 起始位置
        card_x = self.scaler.get_layout_value('card_area', 'x')
        card_y = self.scaler.get_layout_value('card_area', 'y')
        card_width = self.scaler.scale_value(config.CARD_WIDTH)
        card_height = self.scaler.scale_value(config.CARD_HEIGHT)
        card_margin = self.scaler.scale_value(config.CARD_MARGIN)
        level_spacing = self.scaler.scale_value(195)  # 从220改为195，卡牌缩小后间距也缩小

        for level in config.CARD_LEVELS:
            # 等级标题
            level_text = self.font_medium.render(f"等级 {level}", True, config.COLOR_WHITE)
            self.screen.blit(level_text, (card_x, card_y + (level - 1) * level_spacing - self.scaler.scale_value(30)))

            # 绘制该等级的卡牌
            cards = game_state.table_cards[level]
            for i, card in enumerate(cards):
                x = card_x + i * (card_width + card_margin)
                y = card_y + (level - 1) * level_spacing

                card_display = CardDisplay(x, y, card, width=card_width, height=card_height)
                # 设置选中状态
                if self.selected_card and self.selected_card == card:
                    card_display.is_selected = True
                card_display.draw(self.screen, self.font_small, self.font_medium)
                self.card_displays[level].append(card_display)

            # 绘制牌堆
            deck_count = len(game_state.card_decks[level])
            if deck_count > 0:
                deck_x = card_x + 4 * (card_width + card_margin)
                deck_y = card_y + (level - 1) * level_spacing

                # 卡牌背面
                deck_rect = pygame.Rect(deck_x, deck_y, card_width, card_height)
                pygame.draw.rect(self.screen, config.COLOR_DARK_GRAY, deck_rect)
                pygame.draw.rect(self.screen, config.COLOR_WHITE, deck_rect, 2)

                # 剩余数量
                count_text = self.font_large.render(str(deck_count), True, config.COLOR_WHITE)
                count_rect = count_text.get_rect(center=deck_rect.center)
                self.screen.blit(count_text, count_rect)

    def draw_nobles(self, game_state: GameState):
        """
        绘制贵族（多列布局：4个2x2，5个3+2）

        参数:
            game_state: 游戏状态
        """
        noble_x = self.scaler.get_layout_value('noble_area', 'x')
        noble_y = self.scaler.get_layout_value('noble_area', 'y')
        noble_size = self.scaler.scale_value(config.NOBLE_SIZE)

        # 标题
        title = self.font_medium.render("贵族", True, config.COLOR_WHITE)
        self.screen.blit(title, (noble_x, noble_y - self.scaler.scale_value(30)))

        # 绘制贵族（多列布局）
        self.noble_displays.clear()
        noble_spacing = self.scaler.scale_value(config.NOBLE_SIZE + 15)  # 间距

        num_nobles = len(game_state.nobles)

        # 根据贵族数量决定布局
        if num_nobles <= 3:
            # 3个或以下：单列垂直排列
            for i, noble in enumerate(game_state.nobles):
                x = noble_x
                y = noble_y + i * noble_spacing
                noble_display = NobleDisplay(x, y, noble, size=noble_size)
                noble_display.draw(self.screen, self.font_small, self.font_medium)
                self.noble_displays.append(noble_display)
        elif num_nobles == 4:
            # 4个贵族：2列×2行
            for i, noble in enumerate(game_state.nobles):
                col = i // 2  # 列索引 (0或1)
                row = i % 2   # 行索引 (0或1)
                x = noble_x + col * noble_spacing
                y = noble_y + row * noble_spacing
                noble_display = NobleDisplay(x, y, noble, size=noble_size)
                noble_display.draw(self.screen, self.font_small, self.font_medium)
                self.noble_displays.append(noble_display)
        else:  # 5个贵族
            # 5个贵族：第1列3个，第2列2个
            for i, noble in enumerate(game_state.nobles):
                if i < 3:
                    # 第1列：3个
                    col = 0
                    row = i
                else:
                    # 第2列：2个
                    col = 1
                    row = i - 3
                x = noble_x + col * noble_spacing
                y = noble_y + row * noble_spacing
                noble_display = NobleDisplay(x, y, noble, size=noble_size)
                noble_display.draw(self.screen, self.font_small, self.font_medium)
                self.noble_displays.append(noble_display)

    def draw_players_info(self, game_state: GameState):
        """
        绘制玩家信息区域

        参数:
            game_state: 游戏状态
        """
        # 清空保留卡显示列表
        self.reserved_card_displays.clear()

        # 玩家信息区域在屏幕下方
        player_y = self.scaler.get_layout_value('player_area', 'y')
        player_height = self.scaler.get_layout_value('player_area', 'height')
        player_width = self.screen_width // game_state.num_players

        for i, player in enumerate(game_state.players):
            x = i * player_width + self.scaler.scale_value(10)
            self._draw_single_player_info(player, x, player_y, player_width - self.scaler.scale_value(20), player_height)

    def _draw_single_player_info(self, player, x, y, width, height):
        """
        绘制单个玩家的信息（优化：保留卡两列，宝石/红利换行）

        参数:
            player: 玩家对象
            x, y: 绘制位置
            width: 区域宽度
            height: 区域高度
        """
        # 背景框
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, config.COLOR_DARK_GRAY, bg_rect)
        pygame.draw.rect(self.screen, config.COLOR_WHITE, bg_rect, 2)

        # 缩放值
        s = self.scaler.scale_value

        # 使用较大字体，填满高度
        line_height = s(35)  # 行高
        left_margin = s(15)
        top_margin = s(15)

        # 左侧信息区域（宽度55%）
        left_width = int(width * 0.55)

        # 右侧保留卡区域（宽度45%）
        reserved_x = x + left_width

        current_y = y + top_margin

        # 1. 玩家名称和分数（加大字体）
        name_text = self.font_large.render(
            f"{player.name} - {player.get_points()}分",
            True, config.COLOR_WHITE
        )
        self.screen.blit(name_text, (x + left_margin, current_y))
        current_y += line_height + s(5)

        # 2. 宝石（每行最多3个，自动换行）
        gems_text = self.font_medium.render("宝石：", True, config.COLOR_WHITE)
        self.screen.blit(gems_text, (x + left_margin, current_y))

        gem_start_x = x + left_margin + s(60)
        gem_x = gem_start_x
        gem_y = current_y
        gem_count_in_row = 0

        for color in config.GEM_TYPES:
            count = player.gems.get(color, 0)
            if count > 0:
                # 每行最多3个，超过换行
                if gem_count_in_row >= 3:
                    gem_count_in_row = 0
                    gem_x = gem_start_x
                    gem_y += s(25)

                gem_color = config.GEM_COLORS[color]
                pygame.draw.circle(self.screen, gem_color, (gem_x, gem_y + s(10)), s(10))
                pygame.draw.circle(self.screen, config.COLOR_BLACK, (gem_x, gem_y + s(10)), s(10), 1)

                count_text = self.font_medium.render(str(count), True, config.COLOR_WHITE)
                self.screen.blit(count_text, (gem_x + s(15), gem_y))

                gem_x += s(50)
                gem_count_in_row += 1

        # 计算宝石占用的行数（至少1行）
        total_gems = sum(1 for color in config.GEM_TYPES if player.gems.get(color, 0) > 0)
        gem_rows = max(1, (total_gems + 2) // 3)  # 至少1行，向上取整
        current_y += line_height + (gem_rows - 1) * s(25)

        # 3. 红利（每行最多3个，自动换行）
        bonuses = player.get_bonuses()
        bonus_text = self.font_medium.render("红利：", True, config.COLOR_WHITE)
        self.screen.blit(bonus_text, (x + left_margin, current_y))

        bonus_start_x = x + left_margin + s(60)
        bonus_x = bonus_start_x
        bonus_y = current_y
        bonus_count_in_row = 0

        for color in config.NORMAL_GEM_TYPES:
            count = bonuses.get(color, 0)
            if count > 0:
                # 每行最多3个，超过换行
                if bonus_count_in_row >= 3:
                    bonus_count_in_row = 0
                    bonus_x = bonus_start_x
                    bonus_y += s(25)

                bonus_color = config.GEM_COLORS[color]
                pygame.draw.circle(self.screen, bonus_color, (bonus_x, bonus_y + s(10)), s(10))
                pygame.draw.circle(self.screen, config.COLOR_WHITE, (bonus_x, bonus_y + s(10)), s(10), 2)

                count_text = self.font_medium.render(str(count), True, config.COLOR_WHITE)
                self.screen.blit(count_text, (bonus_x + s(15), bonus_y))

                bonus_x += s(50)
                bonus_count_in_row += 1

        # 计算红利占用的行数（至少1行）
        total_bonuses = sum(1 for color in config.NORMAL_GEM_TYPES if bonuses.get(color, 0) > 0)
        bonus_rows = max(1, (total_bonuses + 2) // 3)  # 至少1行，向上取整
        current_y += line_height + (bonus_rows - 1) * s(25)

        # 4. 卡牌统计（垂直排列）
        card_info = [
            f"卡牌：{len(player.cards)}张",
            f"保留：{len(player.reserved_cards)}张",
            f"贵族：{len(player.nobles)}个"
        ]

        for info in card_info:
            info_text = self.font_medium.render(info, True, config.COLOR_WHITE)
            self.screen.blit(info_text, (x + left_margin, current_y))
            current_y += line_height

        # 右侧：显示保留的卡牌（两列显示）
        if player.reserved_cards:
            # 计算保留卡尺寸（缩小一点以容纳两列）
            reserved_card_width = s(80)
            reserved_card_height = s(120)
            card_spacing_x = s(8)  # 列间距
            card_spacing_y = s(8)  # 行间距

            for i, card in enumerate(player.reserved_cards):
                # 两列布局：第1,3,5张在第1列，第2,4,6张在第2列
                col = i % 2  # 列索引 (0或1)
                row = i // 2  # 行索引

                card_x = reserved_x + s(10) + col * (reserved_card_width + card_spacing_x)
                card_y = y + top_margin + row * (reserved_card_height + card_spacing_y)

                # 确保不超出边界
                if card_y + reserved_card_height > y + height - s(10):
                    break

                small_card = CardDisplay(card_x, card_y, card, width=reserved_card_width, height=reserved_card_height)
                # 设置选中状态
                if self.selected_card and self.selected_card == card:
                    small_card.is_selected = True
                small_card.draw(self.screen, self.font_small, self.font_small)
                # 保存到保留卡显示列表（用于点击检测）
                self.reserved_card_displays.append(small_card)

    def draw_current_player_highlight(self, game_state: GameState):
        """
        高亮当前玩家（使用黄色边框）

        参数:
            game_state: 游戏状态
        """
        current_idx = game_state.current_player_idx
        player_y = self.scaler.get_layout_value('player_area', 'y')
        player_height = self.scaler.get_layout_value('player_area', 'height')
        player_width = self.screen_width // game_state.num_players
        x = current_idx * player_width + self.scaler.scale_value(10)

        # 绘制黄色高亮边框（更粗，更明显）
        highlight_rect = pygame.Rect(x, player_y, player_width - self.scaler.scale_value(20), player_height)
        highlight_color = config.GEM_COLORS['gold']  # 使用黄金色
        pygame.draw.rect(self.screen, highlight_color, highlight_rect, 5)  # 边框宽度5像素

    def draw_message(self, message, duration=2000):
        """
        在屏幕中央显示消息

        参数:
            message: 消息内容
            duration: 显示时长（毫秒）
        """
        # 创建半透明背景
        msg_width = self.scaler.scale_value(600)
        msg_height = self.scaler.scale_value(200)
        s = pygame.Surface((msg_width, msg_height))
        s.set_alpha(200)
        s.fill(config.COLOR_DARK_GRAY)

        x = (self.screen_width - msg_width) // 2
        y = (self.screen_height - msg_height) // 2

        self.screen.blit(s, (x, y))

        # 绘制边框
        pygame.draw.rect(self.screen, config.COLOR_WHITE, (x, y, msg_width, msg_height), 3)

        # 绘制消息
        lines = message.split('\n')
        for i, line in enumerate(lines):
            text = self.font_large.render(line, True, config.COLOR_WHITE)
            text_rect = text.get_rect(center=(self.screen_width // 2, y + msg_height // 3 + i * self.scaler.scale_value(40)))
            self.screen.blit(text, text_rect)

        pygame.display.flip()
        pygame.time.wait(duration)

    def get_card_at_pos(self, pos):
        """
        获取鼠标位置的卡牌（包括桌面卡牌和保留卡）

        参数:
            pos: 鼠标位置 (x, y)

        返回:
            Card: 点击的卡牌，如果没有返回None
        """
        # 先检查桌面上的卡牌
        for level in config.CARD_LEVELS:
            for card_display in self.card_displays.get(level, []):
                if card_display.rect.collidepoint(pos):
                    return card_display.card

        # 再检查保留卡
        for card_display in self.reserved_card_displays:
            if card_display.rect.collidepoint(pos):
                return card_display.card

        return None

    def get_gem_at_pos(self, pos):
        """
        获取鼠标位置的宝石颜色

        参数:
            pos: 鼠标位置 (x, y)

        返回:
            str: 宝石颜色，如果没有返回None
        """
        for gem_display in self.gem_displays:
            if gem_display.rect.collidepoint(pos):
                return gem_display.color
        return None
