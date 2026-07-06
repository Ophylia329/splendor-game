"""
缩放管理器 - 处理不同分辨率下的UI缩放
"""
import config


class UIScaler:
    """UI缩放管理器"""

    def __init__(self, actual_width, actual_height):
        """
        初始化缩放管理器

        参数:
            actual_width: 实际窗口宽度
            actual_height: 实际窗口高度
        """
        self.actual_width = actual_width
        self.actual_height = actual_height

        # 计算缩放比例
        self.scale_x = actual_width / config.BASE_WIDTH
        self.scale_y = actual_height / config.BASE_HEIGHT

        # 使用统一缩放比例（取较小值，保持纵横比）
        self.scale = min(self.scale_x, self.scale_y)

    def scale_value(self, value):
        """
        缩放数值

        参数:
            value: 基准值

        返回:
            int: 缩放后的值
        """
        return int(value * self.scale)

    def scale_pos(self, x, y):
        """
        缩放坐标位置

        参数:
            x, y: 基准坐标

        返回:
            tuple: 缩放后的坐标 (x, y)
        """
        return (int(x * self.scale), int(y * self.scale))

    def scale_size(self, width, height):
        """
        缩放尺寸

        参数:
            width, height: 基准尺寸

        返回:
            tuple: 缩放后的尺寸 (width, height)
        """
        return (int(width * self.scale), int(height * self.scale))

    def scale_font_size(self, size):
        """
        缩放字体大小

        参数:
            size: 基准字体大小

        返回:
            int: 缩放后的字体大小（至少为10）
        """
        return max(10, int(size * self.scale))

    def get_layout_value(self, area, key):
        """
        获取缩放后的布局值

        参数:
            area: 布局区域名称（如'gem_area'）
            key: 键名（如'x', 'y', 'width'）

        返回:
            int: 缩放后的值
        """
        if area not in config.LAYOUT:
            return 0

        value = config.LAYOUT[area].get(key, 0)
        return self.scale_value(value)

    def update_scale(self, new_width, new_height):
        """
        更新缩放比例（窗口大小改变时调用）

        参数:
            new_width: 新窗口宽度
            new_height: 新窗口高度
        """
        self.actual_width = new_width
        self.actual_height = new_height
        self.scale_x = new_width / config.BASE_WIDTH
        self.scale_y = new_height / config.BASE_HEIGHT
        self.scale = min(self.scale_x, self.scale_y)
