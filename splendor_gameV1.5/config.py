"""
璀璨宝石游戏配置文件
包含所有游戏常量、窗口配置、颜色定义等
"""

# 窗口设置
FULLSCREEN = False  # 是否全屏（F11切换）
WINDOW_TITLE = "璀璨宝石 Splendor"
FPS = 60

# 基准分辨率（所有UI元素基于此设计，然后缩放到实际分辨率）
BASE_WIDTH = 1920
BASE_HEIGHT = 1080

# 默认窗口分辨率
DEFAULT_WINDOW_WIDTH = 1600
DEFAULT_WINDOW_HEIGHT = 900

# 当前窗口尺寸（会在运行时更新）
WINDOW_WIDTH = DEFAULT_WINDOW_WIDTH
WINDOW_HEIGHT = DEFAULT_WINDOW_HEIGHT

# 颜色定义 (R, G, B)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_DARK_GRAY = (50, 50, 50)
COLOR_YELLOW = (255, 215, 0)  # 金黄色，用于悬停高亮
COLOR_BACKGROUND = (34, 49, 63)  # 深蓝灰色背景

# 宝石颜色定义（根据规则文档）
GEM_COLORS = {
    'white': (240, 240, 240),    # 钻石-白色
    'blue': (41, 128, 185),      # 蓝宝石-蓝色
    'green': (39, 174, 96),      # 翡翠-棕色（这里用绿色代替）
    'red': (231, 76, 60),        # 红宝石-红色
    'black': (44, 62, 80),       # 绿玛瑙-黑色
    'gold': (241, 196, 15)       # 黄金-黄色
}

# 宝石类型列表
GEM_TYPES = ['white', 'blue', 'green', 'red', 'black', 'gold']
NORMAL_GEM_TYPES = ['white', 'blue', 'green', 'red', 'black']  # 不包括黄金

# 游戏规则配置（根据人数）
MAX_GEMS_TOTAL = {
    2: {'white': 4, 'blue': 4, 'green': 4, 'red': 4, 'black': 4, 'gold': 5},
    3: {'white': 5, 'blue': 5, 'green': 5, 'red': 5, 'black': 5, 'gold': 5},
    4: {'white': 7, 'blue': 7, 'green': 7, 'red': 7, 'black': 7, 'gold': 5}
}

MAX_HAND_GEMS = 10  # 玩家手上最多持有的宝石数量
MAX_RESERVED_CARDS = 3  # 最多保留3张卡牌
CARDS_ON_TABLE = 4  # 每个等级展示的卡牌数量
WIN_POINTS = 15  # 胜利所需分数

# 贵族数量配置（根据人数）
NOBLES_COUNT = {
    2: 3,
    3: 4,
    4: 5
}

# 卡牌等级
CARD_LEVELS = [1, 2, 3]

# 卡牌数量配置
CARD_COUNTS = {
    1: 40,  # 等级I: 40张
    2: 30,  # 等级II: 30张
    3: 20   # 等级III: 20张
}

# UI尺寸配置（基于BASE_WIDTH x BASE_HEIGHT = 1920x1080）
# 所有尺寸会根据实际窗口大小自动缩放

# ============ 卡牌尺寸配置 ============
# 修改卡牌大小时，只需修改下面两个参数，其他区域会自动调整位置
CARD_WIDTH = 120  # 卡牌宽度（从140改为120）
CARD_HEIGHT = 175  # 卡牌高度（从200改为175）
CARD_MARGIN = 12  # 卡牌间距

# 计算卡牌区域高度（3行卡牌）
CARD_ROW_HEIGHT = CARD_HEIGHT + 20  # 卡牌高度 + 行间距
CARD_AREA_HEIGHT = CARD_ROW_HEIGHT * 3  # 3行卡牌的总高度

# ============ 其他UI元素尺寸 ============
# 宝石尺寸和区域高度
GEM_SIZE = 60
GEM_MARGIN = 10
GEM_AREA_HEIGHT = GEM_SIZE + 40  # 宝石 + 数字显示 + 间距

# 按钮区域高度
BUTTON_AREA_HEIGHT = 70  # 按钮高度 + 间距

# 提示框区域高度
HINT_BOX_HEIGHT = 60  # 提示框高度

# 区域间距
AREA_SPACING = 20

# ============ 动态布局计算 ============
# 宝石和按钮区域的 y 坐标基于卡牌区域自动计算
# 这样修改卡牌大小时，下方区域会自动下移
CARD_AREA_Y = 20  # 卡牌区域起始位置（贴近顶部）
GEM_AREA_Y = CARD_AREA_Y + CARD_AREA_HEIGHT + AREA_SPACING  # 卡牌下方
BUTTON_AREA_Y = GEM_AREA_Y + GEM_AREA_HEIGHT + 10  # 宝石下方（间距稍小）
HINT_BOX_Y = 1080 - HINT_BOX_HEIGHT - 10  # 贴近底部，距离底部10px

# 布局区域（基准坐标 - v7.0新布局，支持卡牌大小变化）
# 贵族列在左上，宝石改为横排，玩家区域贴近右侧
LAYOUT = {
    'title': {'y': 40},
    'noble_area': {'x': 20, 'y': 20, 'width': 160},  # 左上：贵族竖列
    'card_area': {'x': 200, 'y': CARD_AREA_Y, 'width': 700, 'height': CARD_AREA_HEIGHT},  # 中上：牌堆区域（贴近顶部）
    'gem_area': {'x': 200, 'y': GEM_AREA_Y, 'width': 700, 'height': GEM_AREA_HEIGHT},  # 中间：宝石横排（牌堆下方，动态计算）
    'button_area': {'x': 200, 'y': BUTTON_AREA_Y, 'width': 700, 'height': BUTTON_AREA_HEIGHT},  # 中下：按钮一排（宝石下方，动态计算）
    'hint_box': {'x': 10, 'y': HINT_BOX_Y, 'width': 910, 'height': HINT_BOX_HEIGHT},  # 底部：提示框（从左下到玩家区域左侧，width=920-10）
    'player_area': {'x': None, 'y': 0, 'width': 840, 'height': 1080}  # 右侧：玩家竖列（x动态计算贴近右侧）
}

# 贵族尺寸
NOBLE_SIZE = 140  # 从130增加到140，给更多空间显示需求

# 字体设置
FONT_SIZE_SMALL = 16
FONT_SIZE_MEDIUM = 24
FONT_SIZE_LARGE = 32
FONT_SIZE_TITLE = 48

# 中文字体路径（Windows系统）
CHINESE_FONTS = [
    "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",    # 黑体
    "C:/Windows/Fonts/simsun.ttc",    # 宋体
    "C:/Windows/Fonts/msyhbd.ttc",    # 微软雅黑 Bold
]

# 数据文件路径
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# 数据文件配置
# 正式数据（90张卡牌 + 10个贵族）
CARDS_CSV = os.path.join(DATA_DIR, "cards.csv")
NOBLES_CSV = os.path.join(DATA_DIR, "nobles.csv")

# 测试数据（30张卡牌，低花费高声望 + 10个贵族，低要求） 当前使用
# CARDS_CSV = os.path.join(DATA_DIR, "test_cards.csv")
# NOBLES_CSV = os.path.join(DATA_DIR, "test_nobles.csv")

# 图片路径
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
CARDS_IMG_DIR = os.path.join(IMAGES_DIR, "cards")
GEMS_IMG_DIR = os.path.join(IMAGES_DIR, "gems")
NOBLES_IMG_DIR = os.path.join(IMAGES_DIR, "nobles")
