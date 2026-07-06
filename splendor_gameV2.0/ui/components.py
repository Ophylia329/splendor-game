"""
UI组件 - 可复用的界面组件
"""
import pygame
import os
import config


class Button:
    """按钮组件"""

    def __init__(self, x, y, width, height, text, color=config.COLOR_LIGHT_GRAY):
        """
        初始化按钮

        参数:
            x, y: 按钮位置
            width, height: 按钮尺寸
            text: 按钮文字
            color: 按钮颜色
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = config.COLOR_WHITE
        self.text_color = config.COLOR_BLACK
        self.is_hovered = False
        self.is_enabled = True

        # 缓存文字表面（避免每帧重新渲染）
        self._text_surface_cache = None
        self._cached_font = None

    def draw(self, screen, font):
        """
        绘制按钮

        参数:
            screen: pygame屏幕对象
            font: 字体对象
        """
        # 选择颜色
        if not self.is_enabled:
            color = config.COLOR_GRAY
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color

        # 绘制按钮背景
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, config.COLOR_BLACK, self.rect, 2)  # 边框

        # 缓存文字表面，只在字体改变时重新渲染
        if self._text_surface_cache is None or self._cached_font != font:
            self._text_surface_cache = font.render(self.text, True, self.text_color)
            self._cached_font = font

        # 绘制文字
        text_rect = self._text_surface_cache.get_rect(center=self.rect.center)
        screen.blit(self._text_surface_cache, text_rect)

    def handle_event(self, event):
        """
        处理鼠标事件

        参数:
            event: pygame事件

        返回:
            bool: 是否被点击
        """
        if not self.is_enabled:
            return False

        # 只处理点击事件，悬停状态由外部统一管理
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def set_enabled(self, enabled):
        """设置按钮是否可用"""
        self.is_enabled = enabled


class CardDisplay:
    """卡牌显示组件"""

    # 类级别的图片缓存（所有实例共享）
    _image_cache = {}  # {card_id: pygame.Surface}

    def __init__(self, x, y, card, width=None, height=None):
        """
        初始化卡牌显示

        参数:
            x, y: 卡牌位置
            card: 卡牌对象
            width, height: 卡牌尺寸（可选）
        """
        self.x = x
        self.y = y
        self.card = card
        self.width = width or config.CARD_WIDTH
        self.height = height or config.CARD_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.is_hovered = False
        self.is_selected = False  # 选中状态
        self.is_purchasable = False  # 可购买状态（绿色边框）

        # 尝试加载卡牌图片
        self.image = self._load_card_image()

    def _load_card_image(self):
        """
        加载卡牌图片（带缓存）

        返回:
            pygame.Surface: 缩放后的图片，如果不存在返回None
        """
        card_id = self.card.card_id

        # 检查缓存（使用 card_id + 尺寸作为key）
        cache_key = f"{card_id}_{self.width}_{self.height}"
        if cache_key in CardDisplay._image_cache:
            return CardDisplay._image_cache[cache_key]

        # 尝试加载图片
        image_path = os.path.join(config.CARDS_IMG_DIR, f"card_{card_id}.png")

        if os.path.exists(image_path):
            try:
                # 加载并缩放图片
                original_image = pygame.image.load(image_path)
                scaled_image = pygame.transform.scale(original_image, (self.width, self.height))

                # 缓存图片
                CardDisplay._image_cache[cache_key] = scaled_image
                return scaled_image
            except Exception as e:
                print(f"警告: 无法加载卡牌图片 {image_path}: {e}")
                return None

        return None

    def draw(self, screen, font_small, font_medium):
        """
        绘制卡牌

        参数:
            screen: pygame屏幕对象
            font_small: 小字体
            font_medium: 中字体
        """
        # 如果有图片素材，直接显示图片
        if self.image:
            # 绘制图片
            screen.blit(self.image, self.rect)

            # 边框优先级：黄色（选中/悬停） > 绿色（可购买）
            if self.is_selected or self.is_hovered:
                pygame.draw.rect(screen, config.COLOR_YELLOW, self.rect, 3)
            elif self.is_purchasable:
                pygame.draw.rect(screen, config.COLOR_GREEN, self.rect, 3)

        else:
            # 没有图片，显示原来的文字信息
            # 卡牌背景（纯黑色）
            pygame.draw.rect(screen, config.COLOR_BLACK, self.rect)

            # 边框优先级：黄色（选中/悬停） > 绿色（可购买）
            if self.is_selected or self.is_hovered:
                pygame.draw.rect(screen, config.COLOR_YELLOW, self.rect, 3)
            elif self.is_purchasable:
                pygame.draw.rect(screen, config.COLOR_GREEN, self.rect, 3)

            # 绘制声望分数（右上角）
            if self.card.points > 0:
                points_text = font_medium.render(str(self.card.points), True, config.COLOR_WHITE)
                points_bg = pygame.Rect(self.rect.right - 30, self.rect.top + 5, 25, 25)
                pygame.draw.circle(screen, config.COLOR_BLACK, points_bg.center, 15)
                screen.blit(points_text, points_text.get_rect(center=points_bg.center))

            # 绘制红利图标（左上角）
            bonus_color = config.GEM_COLORS[self.card.color]
            pygame.draw.circle(screen, bonus_color,
                              (self.rect.left + 20, self.rect.top + 20), 12)
            pygame.draw.circle(screen, config.COLOR_WHITE,
                              (self.rect.left + 20, self.rect.top + 20), 12, 2)

            # 绘制花费（中下部分）
            # 计算有多少个花费项
            cost_items = [(color, cost) for color, cost in self.card.cost.items() if cost > 0]
            num_items = len(cost_items)

            # 动态计算起始位置和间距，确保不超出边界
            available_height = self.height - 55 - 25  # 顶部55像素（图标+分数），底部25像素（等级）
            if num_items > 0:
                item_spacing = min(18, available_height // num_items)  # 最大间距18，但不超过可用空间
                y_start = self.rect.top + 55

                for i, (color, cost) in enumerate(cost_items):
                    # 宝石图标（缩小到7像素）
                    gem_color = config.GEM_COLORS[color]
                    gem_x = self.rect.left + 12
                    gem_y = y_start + i * item_spacing

                    pygame.draw.circle(screen, gem_color, (gem_x, gem_y), 7)
                    pygame.draw.circle(screen, config.COLOR_BLACK, (gem_x, gem_y), 7, 1)

                    # 花费数字
                    cost_text = font_small.render(str(cost), True, config.COLOR_WHITE)
                    screen.blit(cost_text, (gem_x + 13, gem_y - 7))

            # 绘制等级标识（底部）
            level_text = font_small.render(f"L{self.card.level}", True, config.COLOR_WHITE)
            level_rect = level_text.get_rect(center=(self.rect.centerx, self.rect.bottom - 10))
            screen.blit(level_text, level_rect)

    def handle_event(self, event):
        """
        处理鼠标事件

        参数:
            event: pygame事件

        返回:
            bool: 是否被点击
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class GemDisplay:
    """宝石显示组件"""

    # 类级别的图片缓存（所有实例共享）
    _image_cache = {}  # {color_size: pygame.Surface}

    def __init__(self, x, y, color, count, size=None):
        """
        初始化宝石显示

        参数:
            x, y: 宝石位置
            color: 宝石颜色
            count: 宝石数量
            size: 宝石大小
        """
        self.x = x
        self.y = y
        self.color = color
        self.count = count
        self.size = size or config.GEM_SIZE
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        self.is_hovered = False
        self.is_selected = False  # 选中状态

        # 尝试加载宝石图片
        self.image = self._load_gem_image()

    def _load_gem_image(self):
        """
        加载宝石图片（带缓存）

        返回:
            pygame.Surface: 缩放后的图片，如果不存在返回None
        """
        # 检查缓存（使用 color + 尺寸作为key）
        cache_key = f"{self.color}_{self.size}"
        if cache_key in GemDisplay._image_cache:
            return GemDisplay._image_cache[cache_key]

        # 尝试加载图片
        image_path = os.path.join(config.GEMS_IMG_DIR, f"gem_{self.color}.png")

        if os.path.exists(image_path):
            try:
                # 加载并缩放图片为圆形尺寸
                original_image = pygame.image.load(image_path)
                scaled_image = pygame.transform.scale(original_image, (self.size, self.size))

                # 缓存图片
                GemDisplay._image_cache[cache_key] = scaled_image
                return scaled_image
            except Exception as e:
                print(f"警告: 无法加载宝石图片 {image_path}: {e}")
                return None

        return None

    def draw(self, screen, font):
        """
        绘制宝石（支持图片或纯色圆形）

        参数:
            screen: pygame屏幕对象
            font: 字体对象
        """
        # 如果有图片素材，显示图片
        if self.image:
            # 绘制图片（居中）
            image_rect = self.image.get_rect(center=(self.x, self.y))
            screen.blit(self.image, image_rect)

            # 只在选中或悬停时绘制黄色边框
            if self.is_selected or self.is_hovered:
                pygame.draw.circle(screen, config.COLOR_YELLOW, (self.x, self.y), self.size // 2, 3)

        else:
            # 没有图片，显示纯色圆形
            # 绘制宝石圆形（纯色）
            gem_color = config.GEM_COLORS.get(self.color, config.COLOR_GRAY)
            pygame.draw.circle(screen, gem_color, (self.x, self.y), self.size // 2)

            # 只在选中或悬停时绘制黄色边框
            if self.is_selected or self.is_hovered:
                pygame.draw.circle(screen, config.COLOR_YELLOW, (self.x, self.y), self.size // 2, 3)

        # 数量在外面显示，不在这里绘制

    def handle_event(self, event):
        """
        处理鼠标事件

        参数:
            event: pygame事件

        返回:
            bool: 是否被点击
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class NobleDisplay:
    """贵族显示组件"""

    # 类级别的图片缓存（所有实例共享）
    _image_cache = {}  # {noble_id: pygame.Surface}

    def __init__(self, x, y, noble, size=100):
        """
        初始化贵族显示

        参数:
            x, y: 贵族位置
            noble: 贵族对象
            size: 显示尺寸
        """
        self.x = x
        self.y = y
        self.noble = noble
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)
        self.is_hovered = False

        # 尝试加载贵族图片
        self.image = self._load_noble_image()

    def _load_noble_image(self):
        """
        加载贵族图片（带缓存）

        返回:
            pygame.Surface: 缩放后的图片，如果不存在返回None
        """
        noble_id = self.noble.noble_id

        # 检查缓存（使用 noble_id + 尺寸作为key）
        cache_key = f"{noble_id}_{self.size}"
        if cache_key in NobleDisplay._image_cache:
            return NobleDisplay._image_cache[cache_key]

        # 尝试加载图片
        image_path = os.path.join(config.NOBLES_IMG_DIR, f"noble_{noble_id}.png")

        if os.path.exists(image_path):
            try:
                # 加载并缩放图片
                original_image = pygame.image.load(image_path)
                scaled_image = pygame.transform.scale(original_image, (self.size, self.size))

                # 缓存图片
                NobleDisplay._image_cache[cache_key] = scaled_image
                return scaled_image
            except Exception as e:
                print(f"警告: 无法加载贵族图片 {image_path}: {e}")
                return None

        return None

    def draw(self, screen, font_small, font_medium):
        """
        绘制贵族

        参数:
            screen: pygame屏幕对象
            font_small: 小字体
            font_medium: 中字体
        """
        # 如果有图片素材，直接显示图片
        if self.image:
            # 绘制图片
            screen.blit(self.image, self.rect)

            # 只在悬停时绘制黄色边框
            if self.is_hovered:
                pygame.draw.rect(screen, config.COLOR_YELLOW, self.rect, 4)

        else:
            # 没有图片，显示原来的文字信息
            # 背景
            pygame.draw.rect(screen, config.COLOR_DARK_GRAY, self.rect)

            # 只在悬停时绘制黄色边框
            if self.is_hovered:
                pygame.draw.rect(screen, config.COLOR_YELLOW, self.rect, 3)

            # 绘制分数（顶部中央）
            points_text = font_medium.render("3", True, config.COLOR_WHITE)
            points_rect = points_text.get_rect(center=(self.rect.centerx, self.rect.top + 20))
            pygame.draw.circle(screen, config.GEM_COLORS['gold'], points_rect.center, 15)
            screen.blit(points_text, points_rect)

            # 绘制需求（下半部分）
            # 计算有多少个需求项
            req_items = [(color, req) for color, req in self.noble.requirements.items() if req > 0]
            num_items = len(req_items)

            # 动态计算起始位置和间距，确保不超出边界
            available_height = self.size - 45 - 10  # 顶部45像素（分数），底部10像素留白
            if num_items > 0:
                item_spacing = min(16, available_height // num_items)  # 从13改为16，最大间距增加
                y_start = self.rect.top + 45

                for i, (color, req) in enumerate(req_items):
                    gem_color = config.GEM_COLORS[color]
                    gem_x = self.rect.left + 20
                    gem_y = y_start + i * item_spacing

                    # 宝石图标（从5增大到8像素，更清晰）
                    pygame.draw.circle(screen, gem_color, (gem_x, gem_y), 8)
                    pygame.draw.circle(screen, config.COLOR_WHITE, (gem_x, gem_y), 8, 1)

                    # 需求数字（使用medium字体，更清晰）
                    req_text = font_medium.render(str(req), True, config.COLOR_WHITE)
                    screen.blit(req_text, (gem_x + 13, gem_y - 8))

    def handle_event(self, event):
        """
        处理鼠标事件

        参数:
            event: pygame事件

        返回:
            bool: 是否被点击
        """
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class MessageBox:
    """消息框组件"""

    def __init__(self, x, y, width, height, message, bg_color=config.COLOR_DARK_GRAY):
        """
        初始化消息框

        参数:
            x, y: 消息框位置
            width, height: 消息框尺寸
            message: 消息内容
            bg_color: 背景颜色
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.message = message
        self.bg_color = bg_color

    def draw(self, screen, font):
        """
        绘制消息框

        参数:
            screen: pygame屏幕对象
            font: 字体对象
        """
        # 背景
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, config.COLOR_WHITE, self.rect, 2)

        # 文字（支持多行）
        lines = self.message.split('\n')
        y_offset = self.rect.top + 10

        for line in lines:
            text_surface = font.render(line, True, config.COLOR_WHITE)
            screen.blit(text_surface, (self.rect.left + 10, y_offset))
            y_offset += font.get_height() + 5

    def set_message(self, message):
        """更新消息内容"""
        self.message = message
